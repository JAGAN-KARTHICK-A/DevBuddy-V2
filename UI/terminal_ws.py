import asyncio
import websockets
import os
import sys
import json

try:
    if sys.platform == 'win32':
        import winpty as pywinpty
    else:
        import pty
except ImportError:
    print("FATAL ERROR: A required terminal library is missing.")
    if sys.platform == 'win32':
        print("On Windows, please run: pip install pywinpty")
    sys.exit(1)

WS_HOST = '127.0.0.1'
WS_PORT = 3002

async def bridge(websocket):
    print("IDE client connected. Spawning shell...")
    process = None
    winpty_proc = None
    master_fd = None
    try:
        if sys.platform == 'win32':
            shell = 'powershell.exe'
            winpty_proc = pywinpty.PtyProcess.spawn(shell)
            
            loop = asyncio.get_running_loop()

            async def pty_to_ws():
                while winpty_proc.isalive():
                    data = await loop.run_in_executor(None, winpty_proc.read)
                    if not data:
                        break
                    await websocket.send(data)

            async def ws_to_pty():
                async for message in websocket:
                    try:
                        msg_obj = json.loads(message)
                        if msg_obj.get('type') == 'resize':
                            rows = msg_obj.get('rows', 24)
                            cols = msg_obj.get('cols', 80)
                            winpty_proc.setwinsize(rows, cols)
                            continue
                    except (json.JSONDecodeError, TypeError, AttributeError):
                        winpty_proc.write(message)

            await asyncio.gather(pty_to_ws(), ws_to_pty())

        else:
            shell = os.environ.get('SHELL', 'bash')
            master_fd, slave_fd = pty.openpty()

            process = await asyncio.create_subprocess_exec(
                shell,
                stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
                close_fds=True
            )
            os.close(slave_fd)

            loop = asyncio.get_running_loop()
            reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(reader)
            await loop.connect_read_pipe(lambda: protocol, os.fdopen(master_fd, 'rb', 0))

            async def pty_to_ws():
                while not reader.at_eof():
                    data = await reader.read(65536)
                    if data:
                        await websocket.send(data.decode(errors='ignore'))

            async def ws_to_pty():
                async for message in websocket:
                    try:
                        msg_obj = json.loads(message)
                        if msg_obj.get('type') == 'resize':
                            import fcntl, termios, struct
                            rows = msg_obj.get('rows', 24)
                            cols = msg_obj.get('cols', 80)
                            fcntl.ioctl(master_fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
                            continue
                    except (json.JSONDecodeError, TypeError):
                        os.write(master_fd, message.encode())

            await asyncio.gather(pty_to_ws(), ws_to_pty())

    except websockets.exceptions.ConnectionClosed:
        print("Connection closed normally.")
    except Exception as e:
        print(f"An error occurred in the bridge: {e}")
    finally:
        print("Client disconnected. Terminating shell process.")
        if process and process.returncode is None:
            process.terminate()
            await process.wait()
        if master_fd:
            try:
                os.close(master_fd)
            except:
                pass
        if winpty_proc:
            winpty_proc.close()

async def main():
    print(f"Terminal WebSocket server starting on ws://{WS_HOST}:{WS_PORT}")
    async with websockets.serve(bridge, WS_HOST, WS_PORT):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user.")
