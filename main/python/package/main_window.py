import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication, QModelIndex, QSettings, Qt
from PyQt5.QtGui import QIcon, QKeySequence, QMouseEvent
import os

from .ui import *
from .api.tasks import *

class MainWindow(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.setWindowTitle("Tableau de bord")
        self.setup_data()
        self.setup_ui()
        self.add_to_startup()
        
    
    def setup_data(self):
        init_files()
        self.tasks = load_tasks()
        self.config = load_config() 

    #ui functions
    def setup_ui(self):
        self.create_widgets()
        self.create_layouts()
        self.create_tray_icon()
        self.add_widgets_to_layouts()
        self.modify_widgets()
        self.setup_connections()
        self.init_window_position()

    def create_widgets(self):
        self.tabWidget = QTabWidget()
        for folder in self.tasks: self.tabWidget.addTab(TabView(folder, self.tasks[folder]), folder)
        self.load_tasks()

        self.btn_add = QPushButton()
        self.btn_clean = QPushButton()
        self.btn_folder = QPushButton()
        self.btn_quit = QPushButton()
        
    def modify_widgets(self):
        res = self.ctx.get_resource("style.css")
        with open(res, "r") as file:
            self.setStyleSheet(file.read())
        
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.btn_add.setIcon(QIcon(self.ctx.get_resource("plus.png")))
        self.btn_clean.setIcon(QIcon(self.ctx.get_resource("clean.png")))
        self.btn_quit.setIcon(QIcon(self.ctx.get_resource("remove.png")))
        self.btn_folder.setIcon(ICON_FOLDER)
        self.btn_quit.setStyleSheet("border-radius: 50%")
        


    def create_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.tabWidget)
        self.main_layout.addLayout(self.button_layout)
        self.button_layout.addWidget(self.btn_add)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.btn_folder)
        self.button_layout.addWidget(self.btn_clean)
        self.button_layout.addWidget(self.btn_quit)

    def setup_connections(self):
        self.btn_add.clicked.connect(self.create_task)
        self.btn_clean.clicked.connect(self.clean_done_tasks)
        self.btn_quit.clicked.connect(self.exit)
        self.btn_folder.clicked.connect(self.add_folder)
        self.tabWidget.tabBarDoubleClicked.connect(self.folder_double_clicked)
        QShortcut(QKeySequence("+"), self.tabWidget, self.create_task)
        QShortcut(QKeySequence("Backspace"), self.tabWidget, self.delete_selected_items)
        
        self.tray.activated.connect(self.tray_icon_clicked)
#icone qui s'affiche dans le systray
    def create_tray_icon(self):
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(self.ctx.get_resource("home.png")))
        self.tray.setVisible(True)
    
    def init_window_position(self):
        tray_x = self.tray.geometry().x()
        tray_y = self.tray.geometry().y()
        size = self.sizeHint()
        w = size.width()
        h = size.height()
        self.move(tray_x-(w/2), tray_y - h -50)
    
#triggered functions
    def create_task(self):
        name, result = InputText("Entrez le nom de votre tâche :").get()
        if name and result:
            folder = self.tabWidget.currentWidget().folder
            self.tasks[folder][name] = Task(name, False, folder)
            self.tabWidget.currentWidget().addTask(self.tasks[folder][name])
    
    def load_tasks(self):
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).update_data()

    def clean_done_tasks(self):
        self.tabWidget.currentWidget().clean_done_tasks()
        self.load_tasks()
    
    def delete_selected_items(self):
        self.tabWidget.currentWidget().delete_selected_item()
        self.load_tasks()
       
    
    def tray_icon_clicked(self):
        if self.isHidden():
            self.showNormal()
        else:
            self.hide()

    def add_folder(self):
        name, result = InputText("Entrez le nom du nouveau dossier").get()
        if name and result:
            self.tabWidget.addTab(TabView(name, {}), name)
            self.tasks[name] = {}
            self.dump()

    def folder_double_clicked(self):
        current = self.tabWidget.currentWidget()
        new_name, result = InputText("Entrez le nouveau nom du dossier :", "Confirmer").get(current.folder)
        if new_name and result:
            change_folder_name(current.folder, new_name)
            current.folder = new_name
            self.tabWidget.setTabText(self.tabWidget.indexOf(current), new_name)
            self.load_tasks()

#core functions
    def dump(self):
        tasks = {folder:{name:self.tasks[folder][name].achieved for name in self.tasks[folder]} for folder in self.tasks}
        dump_tasks(tasks)

    def add_to_startup(self):#lancer l'application au au démarrage
        if getattr(sys, "frozen", False):
            setting = QSettings("HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", QSettings.NativeFormat)
            app_path = QCoreApplication.applicationFilePath()
            app_path = app_path.replace("/", "\\")
            setting.setValue("PyTasks", app_path)
    def exit(self):
        try:
            self.hide()
            if self.config["auto_clean"]: self.clean_done_tasks()
        finally:
            self.close()
        

        
