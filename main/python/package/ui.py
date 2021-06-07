from PyQt5.QtWidgets import QShortcut, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QTabWidget
from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.QtGui import QColor, QIcon, QKeySequence
from fbs_runtime.application_context.PyQt5 import ApplicationContext

from .api.tasks import delete_tasks





COLORS = {False:(219, 45, 114), True:(255, 255, 255)}
BLACK = QColor(*(0,0,0))
WHITE = QColor(*(255,255,255))

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
        