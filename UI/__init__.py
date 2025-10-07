from .core import API
import webview
import os
import shutil
import sys
import subprocess
import atexit
from config import Config
import time

class UI():
    def __init__(self):
        self.__api = API()
        self.__terminal_process = None
        self.__config = Config()
    def __get_cwd(self, file):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), file)
    def __get_current_path(self, file):
        return os.path.join(os.path.dirname(os.path.realpath(__file__))+"/templates/", file)
    def start_terminal_bridge(self):
        print("Starting terminal bridge...")
        command = [sys.executable, self.__get_cwd('terminal_ws.py')]
        __path = self.__api.getProjectPath()
        self.__terminal_process = subprocess.Popen(command, cwd=__path)
        print(f"Terminal bridge started with PID: {self.__terminal_process.pid}")
    def stop_terminal_bridge(self):
        if self.__terminal_process and self.__terminal_process.poll() is None:
            print("Stopping terminal bridge...")
            self.__terminal_process.terminate()
            self.__terminal_process.wait()
            self.__terminal_process = None
    def startApp(self):
        atexit.register(self.stop_terminal_bridge)
        primary_screen = webview.screens[0]
        screen_width = primary_screen.width
        screen_height = primary_screen.height

        splash_width = 650
        splash_height = 440

        splash_x = int((screen_width - splash_width) / 2)
        splash_y = int((screen_height - splash_height) / 2)

        splash_window = webview.create_window(
            'Loading DevBuddy...',
            self.__get_current_path('splash.html'),
            width=splash_width,
            height=splash_height,
            frameless=True,
            on_top=True,
            easy_drag=False,
            x=splash_x,
            y=splash_y
        )

        def destroy_splash(window):
            time.sleep(8)
            window.destroy()

        webview.start(destroy_splash, splash_window, debug=self.__config.DEBUG)

        __window = webview.create_window(
                'DevBuddy-V2',
                self.__get_current_path("index.html"),
                js_api=self.__api,
                easy_drag=True,
                resizable=False,
                frameless=True,
                height=689,
                width=976,
                y=int((screen_height-689) / 2),
                x=int((screen_width-976) / 2)
            )
        self.__api.setWindow(__window)
        webview.start(debug=self.__config.DEBUG)
        if self.__api.START_EDITOR:
            __editor_window = webview.create_window(
                'DevBuddy-V2 Code Editor',
                self.__get_current_path('editor.html'),
                width=1200,
                height=800,
                resizable=True,
                min_size=(800, 600),
                js_api=self.__api
            )
            self.__api.setWindow(None)
            self.start_terminal_bridge()
            self.__api.setEditorWindow(__editor_window)
            def on_closing():
                print("Window is closing, ensuring terminal bridge is stopped.")
                self.stop_terminal_bridge()
            __editor_window.events.closing += on_closing
            webview.start(debug=self.__config.DEBUG)
