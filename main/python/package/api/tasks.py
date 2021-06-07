from json.decoder import JSONDecodeError
import os
from pathlib import Path
import logging
from typing import Iterable
import uuid
import json
from PyQt5.QtGui import QIcon


logging.basicConfig(level = logging.DEBUG)

TASKS_DIR = os.path.join(Path.home(), ".todo")
TASKS_FILEPATH = os.path.join(TASKS_DIR, "tasks.json")

DEFAULT_TASK_CONFIG = {"general":{}}



#fonctions
def cast_dict_to_task(task_dict: dict, folder):
    return {key:Task(key, value, folder, True) for key, value in task_dict.items()}

def load_tasks():
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


def simple_load_tasks()->dict:
    if os.path.exists(TASKS_FILEPATH):
        with open(TASKS_FILEPATH, "r") as f:
            try:
                return json.load(f)
            except JSONDecodeError:
                dump_tasks(DEFAULT_TASK_CONFIG)
                return json.load(f)
    return {}


def init_task_file():
    if not os.path.exists(TASKS_DIR): os.mkdir(TASKS_DIR)
    if not os.path.exists(TASKS_FILEPATH):
        with open(TASKS_FILEPATH, "x") as f:
            json.dump(DEFAULT_TASK_CONFIG, f)


def delete_all_tasks():
    empty = {"general":{}}
    with open(TASKS_FILEPATH, "w") as f:
        json.dump(empty, f) 

def delete_tasks(cleanable_tasks: Iterable[tuple]):
    tasks = simple_load_tasks()
    for folder, task in cleanable_tasks: del tasks[folder][task]
    with open(TASKS_FILEPATH, "w") as f: json.dump(tasks, f)

def dump_tasks(tasks):
    with open(TASKS_FILEPATH, "w") as f:
        json.dump(tasks, f)

#class
class Task:
    def __init__(self, name, achieved=False, folder="general", loaded=False):
        self.name = name
        self.achieved = achieved
        self.folder = folder
        if not loaded: self.dump()
    
    def switch_folder(self, new_folder:str):
        tasks = simple_load_tasks()
        del tasks[self.folder][self.name]
        if new_folder in tasks: tasks[new_folder][self.name] = self.achieved
        else: tasks[new_folder] = {self.name:self.achieved}
        with open (TASKS_FILEPATH,"w") as fw:
            json.dump(tasks, fw) 
        self.folder = new_folder
        
    def switch_status(self):
        self.achieved = not self.achieved
        self.dump()

    def dump(self):
        tasks = simple_load_tasks()
        tasks[self.folder][self.name] = self.achieved
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