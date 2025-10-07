from config import DatabaseConfig
import sqlite3
import os
import pickle

class DB_Service():
    def __init__(self):
        self.__config = DatabaseConfig()
        self.__init_tables()
    def __execute_command(self, command, args=()):
        __conn = sqlite3.connect(self.__config.DB_PATH)
        __cursor = __conn.cursor()
        if args == ():__cursor.execute(command)
        else:__cursor.execute(command, args)
        __conn.commit()
        __d = __cursor.fetchall()
        __cursor.close()
        __conn.close()
        return __d
    def __init_tables(self):
        if not os.path.exists(self.__config.DB_PATH):
            with open(self.__config.DB_PATH, "w") as __f:
                __f.write("")
        self.__execute_command("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, path TEXT NOT NULL, language TEXT NOT NULL, model_name TEXT NOT NULL, apiKey TEXT NOT NULL, start_date TEXT NOT NULL, chat_history BLOB NOT NULL)")
    def __check_project_exists(self, name, path):
        __name_check = self.__execute_command("SELECT 1 FROM projects WHERE name=? LIMIT 1", (name,))
        __path_check = self.__execute_command("SELECT 1 FROM projects WHERE path=? LIMIT 1", (path,))
        return __name_check or __path_check
    def createNewProject(self, name, path, language, model_name, apiKey):
        if self.__check_project_exists(name, path): return False
        __convoHistory = pickle.dumps([])
        self.__execute_command("INSERT INTO projects(name, path, language, model_name, apiKey, chat_history, start_date) VALUES (?, ?, ?, ?, ?, ?, DATETIME('now'))", (name, path, language, model_name, apiKey, __convoHistory))
        return True
    def listAllProjects(self):
        __d = self.__execute_command("SELECT id, name, path, language, model_name, apiKey, start_date FROM projects")
        return __d
    def getProjectByID(self, id):
        return self.__execute_command("SELECT id, name, path, language, model_name, apiKey, start_date FROM projects WHERE id=?", (id,))
    def saveProjectChatHistory(self, name, path, history):
        return self.__execute_command("UPDATE projects SET chat_history=? WHERE name=? AND path=?", (pickle.dumps(history), name,path))
    def getProjectChatHistory(self, name, path):
        return pickle.loads(self.__execute_command("SELECT chat_history FROM projects WHERE name=? AND path=?", (name,path))[0][0])
    def deleteProject(self, name, path):
        if self.__check_project_exists(name, path):
            self.__execute_command("DELETE FROM projects WHERE name=? AND path=?", (name, path))
            return True
        return False


