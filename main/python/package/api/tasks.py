from json.decoder import JSONDecodeError
import os
from pathlib import Path
import logging
from typing import Iterable
import uuid
import json
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon


logging.basicConfig(level = logging.DEBUG)

TASKS_DIR = os.path.join(Path.home(), ".todo")
TASKS_FILEPATH = os.path.join(TASKS_DIR, "tasks.json")
HISTORY_FILEPATH = os.path.join(TASKS_DIR, "history.json")
CONFIG_FILEPATH = os.path.join(TASKS_DIR, "config.ini")

DEFAULT_TASK_CONFIG = {"general":{}}
DEFAULT_HISTORY_CONFIG = {}
DEFAULT_CONFIG = {"first_time":True, "auto_clean":False, "notifications":True}



#fonctions
##helpers
def str_to_qdate(date):
    if date: return QDate(*[int(d) for d in date.split("-")])
    return QDate()

def qdate_to_str(qdate: QDate):
    return str(qdate.year())+"-"+str(qdate.month())+"-"+str(qdate.day())

def cast_dict_to_task(task_dict: dict, folder):
    return {key:Task(key, value["achieved"], folder, value["priority"], value["date"], True) for key, value in task_dict.items()}

##file system initialization
def init_files():
    init_task_file()
    init_history_file()
    init_config_file()

def init_task_file(force = False):
    if not os.path.exists(TASKS_DIR): os.mkdir(TASKS_DIR)
    if not os.path.exists(TASKS_FILEPATH) or force:
        with open(TASKS_FILEPATH, "x") as f:
            json.dump(DEFAULT_TASK_CONFIG, f)

def init_history_file(force = False):
    if not os.path.exists(HISTORY_FILEPATH) or force:
        with open(HISTORY_FILEPATH, "w") as f:
            json.dump(DEFAULT_HISTORY_CONFIG, f)

def init_config_file(force = False):
    if not os.path.exists(CONFIG_FILEPATH) or force:
        with open(CONFIG_FILEPATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f)


##data management
def load_tasks()->dict:
    if os.path.exists(TASKS_FILEPATH):
        with open(TASKS_FILEPATH, "r") as f:
            try:
                tasks = json.load(f)
                for folder in tasks: tasks[folder] = cast_dict_to_task(tasks[folder], folder)
                return tasks
            except JSONDecodeError:
                dump_tasks(DEFAULT_TASK_CONFIG)
                return json.load(f)
    return {}

def load_history():
    if os.path.exists(HISTORY_FILEPATH):
        with open(HISTORY_FILEPATH, "r") as f:
            try:
                return json.load(f)
            except JSONDecodeError:
                init_history_file(True)
    return {}

def load_config():
    if os.path.exists(CONFIG_FILEPATH):
        with open(CONFIG_FILEPATH, "r") as f:
            try:
                return json.load(f)
            except JSONDecodeError:
                init_config_file(True)
    return {}


def simple_load_tasks()->dict:
    if os.path.exists(TASKS_FILEPATH):
        with open(TASKS_FILEPATH, "r") as f:
            try:
                return json.load(f)
            except JSONDecodeError:
                dump_tasks(DEFAULT_TASK_CONFIG)
                return json.load(f)
    return {}


def delete_all_tasks():
    empty = {"general":{}}
    with open(TASKS_FILEPATH, "w") as f:
        json.dump(empty, f) 

def delete_task(folder, name):
    tasks = simple_load_tasks()
    tasks[folder].pop(name)
    dump_tasks(tasks)

def delete_tasks(cleanable_tasks: Iterable[tuple]):
    tasks = simple_load_tasks()
    for folder, task in cleanable_tasks: del tasks[folder][task]
    with open(TASKS_FILEPATH, "w") as f: json.dump(tasks, f)

def dump_tasks(tasks):
    with open(TASKS_FILEPATH, "w") as f:
        json.dump(tasks, f)

def dump_history(history):
    with open(HISTORY_FILEPATH, "w") as f:
        json.dump(history, f)

def change_folder_name(old_name, new_name):
    tasks = simple_load_tasks()
    if old_name in tasks and not new_name in tasks:
        tasks[new_name] = tasks[old_name]
        del tasks[old_name]
        dump_tasks(tasks)

def add_task_to_history(task):
    history = load_history()
    history[task.folder].append(task.name)
    dump_history(history)

def add_task_to_history(folder, name):
    history = load_history()
    if folder in history: history[folder].append(name)
    else: history[folder] = [name]
    dump_history(history)

def add_tasks_to_history(tasks):
    for folder, name in tasks:
        add_task_to_history(folder, name)



#class
class Task:
    def __init__(self, name, achieved=False, folder="general", priority = 0, date="", loaded=False):
        self.name = name
        self.achieved = achieved
        self.folder = folder
        self.priority = priority
        self.date = str_to_qdate(date)
        if not loaded: self.dump()
    
    def toDict(self):
        return {"achieved":self.achieved, "priority":self.priority, "date":qdate_to_str(self.date)}

    def switch_folder(self, new_folder:str):
        tasks = simple_load_tasks()
        del tasks[self.folder][self.name]
        if new_folder in tasks: tasks[new_folder][self.name] = self.toDict()
        else: tasks[new_folder] = {self.name:self.toDict()}
        with open (TASKS_FILEPATH,"w") as fw:
            json.dump(tasks, fw) 
        self.folder = new_folder
        
    def switch_status(self):
        self.achieved = not self.achieved
        self.dump()
    def rename(self, new_name):
        self.name = new_name
        self.dump()
    def change_date(self, new_date):
        if isinstance(new_date, QDate):
            self.date = new_date
            self.dump()
    
    def update(self, data: dict):
        if "name" in data and self.name != data["name"]:
            delete_task(self.folder, self.name)
            self.name = data["name"]

        if "date" in data:
            if isinstance(data["date"], QDate): 
                self.date = data["date"]
            else: self.date = str_to_qdate(data["date"])
        if "priority" in data: self.priority = data["priority"]
        self.dump()

    def dump(self):
        tasks = simple_load_tasks()
        tasks[self.folder][self.name] = self.toDict()
        with open (TASKS_FILEPATH,"w") as fw:
            json.dump(tasks, fw) 
        
    def delete(self):
        with open(TASKS_FILEPATH, "r") as f:
            tasks = json.load(f)
            del tasks[self.folder][self.name]
            with open (TASKS_FILEPATH, "w") as fw:
                json.dump(tasks, fw)

    def __str__(self):
        return self.name
    def __repr__(self) -> str:
        return str(self.achieved)