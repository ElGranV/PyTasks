from typing import overload
from PyQt5.QtWidgets import QAction, QCalendarWidget, QCheckBox, QComboBox, QDialog, QInputDialog, QLabel, QLineEdit, QMenu, QMessageBox, QPushButton, QShortcut, QStyle, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QTabWidget
from PyQt5.QtCore import QCalendar, QModelIndex, Qt
from PyQt5.QtGui import QColor, QContextMenuEvent, QIcon, QKeySequence, QMouseEvent
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from .api.tasks import Task, add_tasks_to_history, delete_tasks, load_tasks





COLORS = {False:(219, 45, 114), True:(255, 255, 255)}
BLACK = QColor(*(0,0,0))
WHITE = QColor(*(255,255,255))
BLUE = (44, 140, 240)

ICON_CHECKED = QIcon(ApplicationContext().get_resource("checked.png"))
ICON_FOLDER = QIcon(ApplicationContext().get_resource("folder.png"))
ICON_BOARD = QIcon(ApplicationContext().get_resource("board.png"))
ICON_QUIT = QIcon(ApplicationContext().get_resource("remove.png"))

BUTTON_OK_STYLE = f"background-color: rgb{str(BLUE)}; color:white; border-radius: 3%;"


class TaskItem(QListWidgetItem):
    def __init__(self, name, achieved=False):
        super().__init__(name)
        self.name = name
        self.achieved = achieved
        self.setBackground(WHITE)
        self.setForeground(Qt.black)
        self.set_icon() 
        
    def set_icon(self):
        if self.achieved:
            self.setIcon(ICON_CHECKED)
        else:
            self.setIcon(ICON_BOARD)
            #self.setForeground(WHITE)

    def switch_status(self):
        self.achieved = not self.achieved
        self.set_icon()

    def __str__(self):
        return self.name

class CustomListWidget(QListWidget):
    def contextMenuEvent(self, e: QContextMenuEvent) -> None:
        menu = QMenu(self)
        details = menu.addAction("Détails")
        delete = menu.addAction("Supprimer")
        action = menu.exec(e.globalPos())
        if action == details: self.launchDialog()
        if action == delete: self.delete()

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
        self.lw_tasks = CustomListWidget()
        for task in self.tasks.values(): 
            self.lw_tasks.addItem(TaskItem(task.name, task.achieved))

    def modify_widgets(self):
        self.lw_tasks.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lw_tasks.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lw_tasks.launchDialog = self.launchDialog
        self.lw_tasks.delete = self.delete_selected_item
        


    def create_layouts(self):
        self.main_layout = QHBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lw_tasks)

    def setup_connections(self):
        self.lw_tasks.clicked.connect(self.lw_tasks_clicked)
        
#core functions
##data
    def update_data(self):
        self.lw_tasks.clear()
        tasks = load_tasks()[self.folder]
        for task in tasks.values(): self.lw_tasks.addItem(TaskItem(task.name, task.achieved))
        self.tasks = tasks
    
    
    def addTask(self, task):
        if not task.name in self.tasks:
            self.tasks[task.name]=task
            self.lw_tasks.addItem(TaskItem(task.name, task.achieved))
    
    def clean_done_tasks(self):
        cleanable_tasks = []
        for i in range(self.lw_tasks.count()):
           item = self.lw_tasks.item(i)
           if item.achieved: cleanable_tasks.append([self.folder, item.name])
        delete_tasks(cleanable_tasks)
        add_tasks_to_history(cleanable_tasks)
##triggered  
    def lw_tasks_clicked(self, index):
        self.tasks[index.data()].switch_status()
        self.lw_tasks.currentItem().switch_status()
    
    def delete_selected_item(self):
        items = self.lw_tasks.selectedItems()
        for item in items:
            self.tasks[item.name].delete()
            self.tasks.pop(item.name)
            self.update_data()
        
    def launchDialog(self):
        task_name = self.lw_tasks.currentItem().name
        details= TaskDetails(self.tasks[task_name], self)
        data, result = details.get()
        if data and result:
            if not data["name"] in self.tasks or data["name"] == task_name:
                self.tasks[task_name].update(data)
                self.update_data()
            else:
                QMessageBox(QMessageBox.Icon(), "Impossible de sauvegarder les modifications", "Vous avez entré le nom d'une tâche qui existe déjà")



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
        self.btn_ok.setStyleSheet(BUTTON_OK_STYLE)
        self.btn_undo.setStyleSheet("border-radius: 3%")

        self.btn_ok.setFlat(True)
        self.btn_undo.setFlat(True)
    

    def get(self, placeholder = ""):
        self.edit.setText(placeholder)
        result = self.exec()
        value = self.edit.text()
        return [value, result]

###

class TaskDetails(QDialog):
    def __init__(self, task, parent = None):
        super().__init__(parent)
        self.task = task
        self.setWindowModality(Qt.ApplicationModal)
        self.setup_ui()
        self.data = {}
    
    def setup_ui(self):
        self.setStyleSheet("background-color:white")
        self.create_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()
        self.modify_widgets()
        #self.setStyleSheet("height: 100px; width: 180px; background-color: white; font-size:15px")
        
    def create_widgets(self):
        self.edit = QLineEdit(self.task.name)
        self.calendar_wgt = QCalendarWidget()
        self.btn_save = QPushButton("Enregistrer")
        self.btn_quit = QPushButton("Quitter")
        self.combo_priority = QComboBox()
        


    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.upper_layout = QHBoxLayout()
        self.button_layout = QHBoxLayout()
        
        
    def add_widgets_to_layouts(self):
        self.upper_layout.addWidget(self.edit)
        self.upper_layout.addWidget(self.combo_priority)
        self.main_layout.addLayout(self.upper_layout)
        self.main_layout.addWidget(self.calendar_wgt)
        
        self.button_layout.addStretch()
        self.main_layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.btn_save)
        self.button_layout.addWidget(self.btn_quit)
        
      
    def setup_connections(self):
        self.btn_save.clicked.connect(self.save)
        self.btn_quit.clicked.connect(self.reject)
        
    def modify_widgets(self):
        self.btn_save.setStyleSheet(BUTTON_OK_STYLE+"padding:12px")
        self.btn_save.setFlat(True)
        self.btn_quit.setFlat(True)

        self.combo_priority.addItem("Normal")
        self.combo_priority.addItem("Urgent")
        self.combo_priority.addItem("Très urgent")
    
    ##triggered
    def save(self):
        self.data["name"] = self.edit.text()
        self.data["date"] = self.calendar_wgt.selectedDate()
        self.data["priority"] = self.combo_priority.currentData()
        self.accept()
    
    def get(self):
        result = self.exec()
        return [self.data, result]
        

class PopupNotification(QDialog):
    def __init__(self, tasks, parent =  None):
        super().__init__(parent)
        self.tasks = tasks
    
    def setup_ui(self):
        self.create_layouts()
        self.create_widgets()
        self.add_widgets_to_layouts()

    def create_widgets(self):
        self.btn_quit = QPushButton(ICON_QUIT)
        self.lbl = QLabel("Vos tâches pour aujourd'hui")
        self.lw_today_tasks = QListWidget()
        self.lw_urgent_tasks = QListWidget()
    
    def create_layouts(self):
        pass
    
    def add_widgets_to_layouts(self):
        pass


