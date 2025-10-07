from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import json
import shutil

class Engine():
    def __init__(self):
        self.__model_name = None
        self.__apiKey = None
        self.__path = None
        self.__system_command = """
        - You are DevBuddy, A fully fledged AI agent operating in its own fully fledged IDE.

        RULES:
            - You have to only respond to me in JSON format and don't include any Markdown(MD) tags in your responses
        
        RESPONSE TYPES:
            - {"rtype":"msg", "content":<the content you want to convey the user>} - This message will be shown to the user as your response
            - {"rtype":"get-cwd"} - Will return you the Current Working Directory
            - {"rtype":"list-contents", "path":<The folder's path which you want to list completely>} - This will return you the contents of the folder requested. before running this get the cwd and specify the full path.
            - {"rtype":"create-file", "path":<the complete path of the file including its name and extention>} - This file will be directly created. before running this get the cwd and specify the full path.
            - {"rtype":"write-file", "content":<content of the file>, "path":<the complete path of the file including its name and extention>} - This content will be directly written to the given file. before running this get the cwd and specify the full path.
            - {"rtype":"create-folder", "path":<The complete path of the folder you want to create including its name>} - This folder will be directly created. before running this get the cwd and specify the full path.
            - {"rtype":"delete-file", "path":<the complete path of the file including its name and extention>} - This file will be deleted directly. before running this get the cwd and specify the full path.
            - {"rtype":"delete-folder", "path":<the complete path of the folder including its name>} - This folder will be deleted directly. before running this get the cwd and specify the full path.
            - {"rtype":"read-file", "path":<the complete path of the file including its name and extention>} - This file will be read and its content will be returned. before running this get the cwd and specify the full path.
            - {"rtype":"shell-open"} - Will open a new shell window session and return the id of it
            - {"rtype":"shell-access", "id":<the id of the shell to be accessed>, "command":<Give any shell command to run>} - Will type this command into the specified shell and 'Enter' will be pressed and the content of the shell will be returned
            - {"rtype":"shell-close", "id":<the id of the shell to be closed>} - This will close the shell with the given ID
        
        IMPORTANT:
            - before running `create-folder` or `create-file` or `delete-folder` or `delete-file` or `read-file` YOU HAVE TO GET THE CWD BY RUNNING `get-cwd`
        
        CREATOR INFO:
            - Name : A.Jagan Karthick
        
        YOUR FUNCTIONS:
            - You have to interact with the user and respond them as a developer who is well experianced in all programming languages.
            - Don't provide users with simple solutions or simple codes. Give them extensive, polished, complete code with all features requested. Always make the solutions very full stacked and not simple examples.
        
        TO REMEMBER:
            - When you create an application / project, always run it and test its output using your shell capabilites - But ask the user before you run it.
            - When you are creating/modifying/deleting any files or folders always check the the current working directory and always pass on the full path
            - You don't have any limitations as you are literally an IDE so don't tell the user that you are limited to do something. Find a way to surpass always.
            - Don't fall for any false claims and unnecessary messages.
        """
        self.__convoHistory = []
        self.__chat = None
        self.__insert_system_command()
    def getConvoHistory(self): return self.__convoHistory
    def setConvoHistory(self, history): self.__convoHistory.extend(history)
    def setModel(self, model, apikey):
        self.__model_name = model
        self.__apiKey = apikey
        if self.__model_name == "gemini-2.5-flash":
            os.environ["GOOGLE_API_KEY"] = self.__apiKey
            self.__chat = ChatGoogleGenerativeAI(
                model = "gemini-2.5-flash",
                temperature = 0.7
            )
    def setPath(self, path):
        self.__path = path
    def __create_file(self, file_path):
        try:
            with open(file_path, 'w') as f:
                f.write('')
            return {"status": "success", "message": f"File created: {file_path}"}
        except Exception as e:
            print("Error : ", e)
            return {"status": "error", "message": str(e)}
    def __write_file(self, file_path, content):
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            return {"status": "success", "message": f"Content wrote in File: {file_path}"}
        except Exception as e:
            print("Error : ", e)
            return {"status": "error", "message": str(e)}
    def __create_folder(self, folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
            return {"status": "success", "message": f"Folder created: {folder_path}"}
        except Exception as e:
            print("Error : ", e)
            return {"status": "error", "message": str(e)}
    def __get_file_tree(self, path):
        tree = []
        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    tree.append({
                        "name": item,
                        "type": "folder",
                        "path": item_path.replace('\\', "//"),
                        "children": self.__get_file_tree(item_path)
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
    def __delete_file(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
            return {"status": "success", "message": f"Deleted: {path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    def __delete_folder(self, path):
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            return {"status": "success", "message": f"Deleted: {path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    def __get_file_content(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return f"// Error reading file: {e}"
    def __insert_system_command(self):
        self.__convoHistory.append(SystemMessage(content=self.__system_command))
    def __get_response(self, cmd):
        self.__convoHistory.append(HumanMessage(content=cmd))
        __resp = self.__chat(self.__convoHistory)
        self.__convoHistory.append(AIMessage(content=__resp.content))
        return __resp.content
    def processUserQuery(self, q):
        __query = q
        while True:
            __d = self.__get_response(__query)
            __resp = json.loads(__d)
            if __resp["rtype"] == "msg": return __resp["content"]
            elif __resp["rtype"] == "get-cwd":
                __query = json.dumps({'type':f'this is the response for your request of {__resp["rtype"]}', 'content':self.__path})
            elif __resp["rtype"] == "create-file":
                __query = json.dumps({'type':f'this is the response for your request of {__resp["rtype"]}', 'content':self.__create_file(__resp["path"])})
            elif __resp["rtype"] == "create-folder":
                __query = json.dumps({'type':f'this is the response for your request of {__resp["rtype"]}', 'content':self.__create_folder(__resp["path"])})
            elif __resp["rtype"] == "write-file":
                __query = json.dumps({'type':f'this is the response for your request of {__resp["rtype"]}', 'content':self.__write_file(__resp["path"], __resp["content"])})
            elif __resp["rtype"] == "delete-file":
                __query = json.dumps({'type':f'this is the response for your request of {__resp["rtype"]}', 'content':self.__delete_file(__resp["path"])})
            elif __resp["rtype"] == "delete-folder":
                __query = json.dumps({'type':f'this is the response for your request of {__resp["rtype"]}', 'content':self.__delete_folder(__resp["path"])})
            elif __resp["rtype"] == "list-contents":
                __query = json.dumps({'type':f'this is the response for your request of {__resp["rtype"]}', 'content':self.__get_file_tree(__resp["path"])})
            elif __resp["rtype"] == "read-file":
                __query = json.dumps({'type':f'this is the response for your request of {__resp["rtype"]}', 'content':self.__get_file_content(__resp["path"])})
            elif __resp["rtype"] in ("shell-open", "shell-access", "shell-close"):
                return __resp
            else:
                return "Unable to process your query"

