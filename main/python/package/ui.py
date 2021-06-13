from typing import overload
from PyQt5.QtWidgets import QDialog, QInputDialog, QLabel, QLineEdit, QPushButton, QShortcut, QStyle, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QTabWidget
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QColor, QIcon, QKeySequence
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from .api.tasks import delete_tasks





COLORS = {False:(219, 45, 114), True:(255, 255, 255)}
BLACK = QColor(*(0,0,0))
WHITE = QColor(*(255,255,255))
BLUE = (44, 140, 240)

ICON_CHECKED = QIcon(ApplicationContext().get_resource("checked.png"))
ICON_FOLDER = QIcon(ApplicationContext().get_resource("folder.png"))


class TaskItem(QListWidgetItem):
    def __init__(self, name, achieved=False):
        super().__init__(name)
        self.name = name
        self.achieved = achieved
        self.set_background() 
        
    def set_background(self):
        self.setBackground(QColor(*COLORS[self.achieved]))
        if self.achieved:
            self.setForeground(Qt.black)
            self.setIcon(ICON_CHECKED)
        else:
            self.setIcon(QIcon())
            self.setForeground(WHITE)

    
    def switch_status(self):
        self.achieved = not self.achieved
        self.set_background()

    def __str__(self):
        return self.name

class TabView(QWidget):
    def __init__(self, folder, tasks):
        super().__init__()
        self.tasks = tasks
        self.folder = folder
        self.setup_ui()
    
#ui functions 
    def setup_ui(self):
        self.create_widgets()
        self.create_layouts()
        self.modify_widgets()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lw_tasks = QListWidget()
        for task in self.tasks.values(): 
            self.lw_tasks.addItem(TaskItem(task.name, task.achieved))

    def modify_widgets(self):
        self.lw_tasks.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lw_tasks.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def create_layouts(self):
        self.main_layout = QHBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lw_tasks)

    def setup_connections(self):
        self.lw_tasks.clicked.connect(self.lw_tasks_clicked)
        
#core functions
##data
    def update_data(self, tasks):
        self.lw_tasks.clear()
        for task in tasks.values(): self.lw_tasks.addItem(TaskItem(task.name, task.achieved))
        self.tasks = tasks
    
    def addTask(self, task):
        self.tasks[task.name]=task
        self.lw_tasks.addItem(TaskItem(task.name, task.achieved))
    
    def clean_done_tasks(self):
        cleanable_tasks = []
        for i in range(self.lw_tasks.count()):
           item = self.lw_tasks.item(i)
           if item.achieved: cleanable_tasks.append([self.folder, item.name])
        delete_tasks(cleanable_tasks)
##triggered  
    def lw_tasks_clicked(self, index):
        self.tasks[index.data()].switch_status()
        self.lw_tasks.currentItem().switch_status()
    
    def delete_selected_item(self):
        items = self.lw_tasks.selectedItems()
        for item in items:
            self.tasks[item.name].delete()

class InputText(QDialog):
    def __init__(self,  label_text="Votre texte :", ok_text = "Créer", undo_text = "Annuler"):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.ok_text = ok_text
        self.undo_text = undo_text
        self.label_text = label_text
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.create_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()
        self.modify_widgets()
        self.setStyleSheet("height: 60px; width: 180px; background-color: white; font-size:18px")
        
    def create_widgets(self):
        self.edit = QLineEdit()
        self.btn_ok = QPushButton(self.ok_text)
        self.btn_undo = QPushButton(self.undo_text)
        self.lbl = QLabel(self.label_text)

    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout()
        
        
    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl)
        self.main_layout.addWidget(self.edit)
        self.main_layout.addLayout(self.button_layout)
        self.button_layout.addSpacing(1)
        self.button_layout.addWidget(self.btn_ok)
        self.button_layout.addWidget(self.btn_undo)
    
    def setup_connections(self):
        self.btn_ok.clicked.connect(self.accept)
        self.btn_undo.clicked.connect(self.reject)
    def modify_widgets(self):
        self.btn_ok.setStyleSheet(f"background-color: rgb{str(BLUE)}; color:white; border-radius: 3%")
        self.btn_undo.setStyleSheet("border-radius: 3%")

        self.btn_ok.setFlat(True)
        self.btn_undo.setFlat(True)
    

    def get(self):
        result = self.exec()
        value = self.edit.text()
        return [value, result]

