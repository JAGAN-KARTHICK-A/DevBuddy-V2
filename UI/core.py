import webview
import os
import json
import shutil
from dataStore import DB_Service
import sys
import subprocess
from models import Engine
import threading
import uuid
from strip_ansi import strip_ansi
from langchain.schema import SystemMessage, HumanMessage, AIMessage

class API:
    def __init__(self):
        self.__window = None
        self.__editor_window = None
        self.__project_path_state = None
        self.START_EDITOR = False
        self.__project_name = None
        self.__db = DB_Service()
        self.__engine = Engine()
        self.__command_callbacks = {}
        self.__model_name = None
        self.__apiKey = None
    def command_callback(self, callback_id, result):
        result = strip_ansi(result)
        if callback_id in self.__command_callbacks:
            callback = self.__command_callbacks[callback_id]
            callback['result'] = result
            callback['event'].set()
    def __open_shell_tab(self):
        if self.__editor_window:
            __d = self.__editor_window.evaluate_js('window.js_api.open_shell_tab()')
            return __d
        return None

    def __close_shell_tab(self, shell_id):
        if self.__editor_window:
            self.__editor_window.evaluate_js(f"window.js_api.close_shell_tab('{shell_id}')")
        return f"Closed the shell with id: {shell_id}"
    def __enter_command(self, shell_id, command, timeout=15):
        if not self.__window:
            return "Error: Window not available."

        callback_id = str(uuid.uuid4())
        event = threading.Event()
        self.__command_callbacks[callback_id] = {'event': event, 'result': None}

        end_marker = f"END_OF_COMMAND_{callback_id}"
        shell_echo_command = 'Write-Output' if sys.platform == 'win32' else 'echo'
        
        full_command_to_run = f"{command}; {shell_echo_command} '{end_marker}'"

        sanitized_command = full_command_to_run.replace('\\', '\\\\').replace("'", "\\'")
        
        js_code = f"window.js_api.enter_command_and_get_output('{shell_id}', '{sanitized_command}', '{end_marker}', '{callback_id}')"
        self.__window.evaluate_js(js_code)

        event.wait(timeout)

        if callback_id in self.__command_callbacks:
            result = self.__command_callbacks[callback_id]['result']
            del self.__command_callbacks[callback_id]
            return result
        else:
            if callback_id in self.__command_callbacks:
                del self.__command_callbacks[callback_id]
            return "Error: Command timed out or callback failed."
    def getProjectPath(self): return self.__project_path_state
    def __get_current_path(self, file):
        return os.path.join(os.path.dirname(os.path.realpath(__file__))+"/templates/", file)
    def list_projects(self):
        return self.__db.listAllProjects()
    def setWindow(self, window):
        self.__window = window
    def setEditorWindow(self, window):
        self.__editor_window = window
        self.__window = window
        self.__engine.setPath(self.__project_path_state)
        self.__engine.setModel(self.__model_name, self.__apiKey)
        self.__engine.setConvoHistory(self.__db.getProjectChatHistory(self.__project_name, self.__project_path_state))
    def open_folder_dialog(self):
        if self.__window is None:
            return None
        result = self.__window.create_file_dialog(webview.FOLDER_DIALOG)
        return result[0].replace('\\', "//") if result and len(result) > 0 else None
    def create_project(self, folder_path, language, name, model_name, apiKey):
        self.__project_path_state = folder_path
        self.__model_name = model_name
        self.__apiKey = apiKey
        if self.__window:
            self.__window.destroy()
            self.__window = None
        self.START_EDITOR = True
        self.__project_name = name
        self.__db.createNewProject(name, folder_path, language, model_name, apiKey)
        return {"status": "success", "message": "Editor is opening..."}
    def openProject(self, id):
        __details = self.__db.getProjectByID(id)
        self.__project_path_state = __details[0][2]
        self.__engine.setModel(__details[0][4], __details[0][5])
        if self.__window:
            self.__window.destroy()
            self.__window = None
        self.START_EDITOR = True
        self.__project_name = __details[0][1]
        self.__engine.setConvoHistory(self.__db.getProjectChatHistory(self.__project_name, self.__project_path_state))
        return {"status": "success", "message": "Editor is opening..."}
    def get_file_tree(self, path):
        tree = []
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    tree.append({
                        "name": item,
                        "type": "folder",
                        "path": item_path.replace('\\', "//"),
                        "children": self.get_file_tree(item_path)
                    })
                else:
                    tree.append({
                        "name": item,
                        "type": "file",
                        "path": item_path.replace('\\', "//") 
                    })
        except Exception as e:
            print(f"Error reading path {path}: {e}")
            return []
        return sorted(tree, key=lambda x: (x['type'] != 'folder', x['name']))
    def get_project_data(self):
        if not self.__project_path_state or not os.path.isdir(self.__project_path_state):
            return None

        file_tree = self.get_file_tree(self.__project_path_state)
        return {"project_path": self.__project_path_state+"/", "file_tree": file_tree}
    def get_file_content(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return f"// Error reading file: {e}"
    def create_file(self, file_path):
        try:
            with open(file_path, 'w') as f:
                f.write('')
            print(file_path)
            return {"status": "success", "message": f"File created: {file_path}"}
        except Exception as e:
            print("Error : ", e)
            return {"status": "error", "message": str(e)}
    def create_folder(self, folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
            return {"status": "success", "message": f"Folder created: {folder_path}"}
        except Exception as e:
            print("Error : ", e)
            return {"status": "error", "message": str(e)}
    def delete_item(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            return {"status": "success", "message": f"Deleted: {path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    def save_file(self, file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"File saved: {file_path}")
            return {"status": "success", "message": f"File saved successfully."}
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")
            return {"status": "error", "message": str(e)}
    def rename_item(self, old_path, new_path):
        try:
            os.rename(old_path, new_path)
            print(f"Renamed: {old_path} -> {new_path}")
            return {"status": "success", "message": "Item renamed successfully."}
        except Exception as e:
            print(f"Error renaming {old_path}: {e}")
            return {"status": "error", "message": str(e)}
    def reveal_in_explorer(self, path):
        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', '/select,', os.path.normpath(path)])
            elif sys.platform == 'darwin':
                subprocess.run(['open', '-R', path])
            else:
                subprocess.run(['xdg-open', os.path.dirname(path)])
            return {"status": "success"}
        except Exception as e:
            print(f"Error revealing file: {e}")
            return {"status": "error", "message": str(e)}
    def deleteProject(self, name, path):
        return self.__db.deleteProject(name, path)
    def __parseChatHistory(self, history):
        __history = []
        for msg in history:
            if isinstance(msg, HumanMessage): role = "user"
            elif isinstance(msg, AIMessage): role = "assistant"
            if isinstance(msg, SystemMessage) != True:
                if isinstance(msg, AIMessage):
                    __history.append({
                        "role": role,
                        "content": str(json.loads(msg.content)["content"])
                    })
                else:
                    __history.append({
                        "role": role,
                        "content": str(msg.content)
                    })
        return __history
    def getProjectChatHistory(self):
        __d = self.__db.getProjectChatHistory(self.__project_name, self.__project_path_state)
        return self.__parseChatHistory(__d)
    def chatInput(self, msg):
        __msg = msg
        try:
            while True:
                __resp = self.__engine.processUserQuery(__msg)
                if type(__resp) == str:
                    self.__db.saveProjectChatHistory(self.__project_name, self.__project_path_state, self.__engine.getConvoHistory())
                    return __resp
                else:
                    if __resp["rtype"] == "shell-open":
                        __d = self.__open_shell_tab()
                        __msg = json.dumps({'type':f'this is the response for your request of {__resp["rtype"]}', 'content':__d})
                    elif __resp["rtype"] == "shell-access":
                        __d = self.__enter_command(__resp["id"], __resp["command"])
                        __msg = json.dumps({'type':f'this is the response for your request of {__resp["rtype"]}', 'content':__d})
                    elif __resp["rtype"] == "shell-close":
                        __d = self.__close_shell_tab(__resp["id"])
                        __msg = json.dumps({'type':f'this is the response for your request of {__resp["rtype"]}', 'content':__d})
        except:
            return "Unable to process your request. Try Again."
    def close_app(self):
        if self.__window:
            self.__window.destroy()
        if self.__editor_window:
            self.__editor_window.destroy()


