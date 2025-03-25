#!/usr/bin/python3
import sys
from PyQt6 import QtWidgets, QtGui, QtCore

from PyQt6.QtWidgets import *
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import *
from PyQt6.QtCore import Qt  # Import Qt from PyQt6.QtCore

import os,subprocess
from PyQt6.QtGui import QIcon, QPixmap
from stagers import Ui_HTTPListenerDialog
from c2front5 import *
from c4profile import *
from PyQt6 import QtWidgets
from badgerterminal import badgerteriminal
import asyncio
import threading
from PyQt6.QtCore import QTimer
# import datetime 
def print_ascii_art(version="v0"):

    print(f"""
      
   ______ ____  ______      ______ ___ 
  / ____// __ \/_  __/     / ____/|__ \\
 / / __ / /_/ / / /______ / /     __/ /
/ /_/ // ____/ / //_____// /___  / __/ 
\____//_/     /_/        \____/ /____/ {version}
                                       


    """)

# Call the function with a custom version
print_ascii_art("v1.0")


class stager_window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_HTTPListenerDialog()
        self.ui.setupUi(self)

        self.ui.comboBox.activated[int].connect(self.shellocde)
        self.ui.comboBox_6.activated[int].connect(self.delivery)

        # self.ui.setItemText.clicked.connect(self.uploade_shellcode)
        self.print = MainWindow.print_event
    #  actions by indexing such as from self.comboBox.setItemText(1,
    def shellocde(self, index):
         if index  == 1:
            self.print("Uploading shellcode button clicked!")
         if index  == 0:
             self.print("List old ones......")

    def delivery(self, i):
        if i == 0:
            self.print('MSI gen.......')
        if i == 1:
            self.print('OneClick gen......')
        if i == 2:
            self.print('shellcode gen ....')

class c4profile(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.uic4 = Ui_c4profile()
       
        self.uic4.setupUi(self)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

       
      
        self.ui.centralwidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self.ui.centralwidget)
        
        # defualt_value  = 'Listening incoming'
        # with open('event_log.json', 'w') as f:
        #     json.dumps(defualt_value)


        self.setWindowTitle('LLM-AGI-C2')
        self.resize(1600, 900)

        self.lisener = set()
    

        self.timer = QTimer(self)

        self.timer.timeout.connect(self.web)

        self.timer.start(1000)

        # self.exit_button = QPushButton("Exit")
        # self.exit_button.clicked.connect(QApplication.instance().quit)

        # self.button_layout = QHBoxLayout()
        # self.button_layout.addStretch()
        # self.button_layout.addWidget(self.exit_button)

        

       


        # # Optional: Set size policy to allow expanding
        def sysinfo(self):
            
            commands = [
                    "cat /etc/os-release",       # OS Version
                    "uname -r",                  # Kernel Version
                    "nasm -v",                   # NASM Version
                    "g++ --version",             # C++ Compiler Version
                    "gcc --version",             # GCC Version
                    "nvidia-smi",                # NVIDIA Driver and CUDA Version
                    "date",                      # System Date & Time
                    "timedatectl",               # Time Zone
                    "lscpu",                     # CPU Information
                    "lsmem",
                    "date",
                    "ifconfig",
            ]
            # self.ui.event_log_widget.clear()
            
            for cmd in commands:
                try:
                    # listener_tab = Ui_MainWindow.ListenerTab()
                    result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
                    # Append each result to the event log
                    self.ui.event_log_widget.insertHtml(f"<b style='color:#00ff00;'>Command : </b> {cmd}<br><pre style='color: #ffcc00;'>{result}</pre><br>")
                    # self.ui.web_activity_widget.append(f"<b style='color:#00ff00;'>Command : </b> <pre style='color: #00ff00;'>f'{self.info}'<</pre><br>")
                    # self.ui.baderwidget.append(f"<b style='color:#00ff00;'>Command : </b> {cmd}<br><pre style='color: #00ff00;'>{result}</pre><br>")
                except subprocess.CalledProcessError as e:
                    # If command fails, print the error message
                    self.ui.event_log_widget.insertHtml(f"Command: {cmd}\nError: {e.output}\n")

            # self.ui.web_activity_widget.append(f"<b style='color:#00ff00;'> </b> <pre style='color: #00ff00;f'{info}'<</pre><br>")
            # self.ui.web_activity_widget.insertHtml(f"<b style='color:#8dffff;'></b> <pre style='color: #8dffff;'>{self.info}<</pre><br>")

            # self.ui.baderwidget.append(f"<b style='color:#00ff00;'>Command : </b> {info}<br><pre style='color: #00ff00;'>{result}</pre><br>")

                   
        sysinfo(self)

     
    
        

        toolbar = QToolBar()
        button_action = QAction(QIcon('images/h12.png'), '&Operator', self)
        button_action.setStatusTip('Havoc')
        button_action.triggered.connect(self.inputbox)
        button_action.setCheckable(True)
       
        button_action2 = QAction(QtGui.QIcon('images/h2.png'), 'Writing to home dir', self)
        button_action2.setStatusTip('Havoc2')
        button_action2.triggered.connect(self.write)
        button_action2.setCheckable(True)
        # toolbar.addAction(button_action2)

        button_action3 = QAction(QtGui.QIcon('images/h3.png'), 'Clicking', self)
        button_action3.setStatusTip('Payload')
        button_action3.triggered.connect(self.click)
        button_action3.setCheckable(True)
        # toolbar.addAction(button_action3)

        button_action4 = QAction(QtGui.QIcon('images/h3.png'), 'x64-bin-actions', self)
        button_action4.setStatusTip('x64-bin')
        button_action4.triggered.connect(self.x64_bin)
        button_action4.setCheckable(True)


        stager = QAction(QtGui.QIcon('images/h5.png'), 'Settings', self)
        stager.setStatusTip('Stagers-Gen Settings')
        stager.triggered.connect(self.stager_window)
        stager.setCheckable(True)

        C4Profiler = QAction(QtGui.QIcon('images/h.png'), 'C4Profiler', self)
        C4Profiler.setStatusTip('C4Profiler')
        C4Profiler.triggered.connect(self.c4profile)
        C4Profiler.setCheckable(True)

        AutoPilot = QAction(QtGui.QIcon('images/h.png'), 'AutoPolit', self)
        AutoPilot.setStatusTip('START LISENER')
        # AutoPilot.triggered.connect(start_ts(self))
        AutoPilot.setCheckable(True)


        self.setStatusBar(QStatusBar(self))

        menu = self.menuBar()
        file_menu = menu.addMenu("&Operator")
        file_menu.addAction(button_action)
        file_menu.addSeparator()
        # file_menu.addAction(button_action2)
        # file_menu.addSeparator()

        file_menu2 = menu.addMenu("&Payloads")
        # file_menu2.addAction(button_action3)
        
        file_submenu = file_menu2.addMenu(QtGui.QIcon('images/h3.png'), 'stageless__x64.bin')
        file_submenu2 = file_submenu.addMenu(QIcon('images/h3.png'), 'Writing file')
        file_submenu2.addAction(button_action2)
        
        file_menu3 = menu.addMenu("&Stagers")
    
        file_submenu3 = file_submenu.addMenu(QtGui.QIcon('images/h3.png'), 'x64_bin gen')
        file_submenu3.addAction(button_action4)
        file_submenu4 = file_menu3.addMenu(QtGui.QIcon("images/h5.png"), "&Stagers-0")
        file_submenu4.addAction(stager)        

        button_action_fullscreen = QAction(QtGui.QIcon('images/h.png'), 'Toggle Fullscreen', self)
        button_action_fullscreen.triggered.connect(self.toggle_fullscreen)
        toolbar.addAction(button_action_fullscreen)

        file_menu4 = menu.addMenu("&C4Profiler")
        file_menu4.addAction(C4Profiler)

   

    def web(self):
        try:
            with open('event_log.json', 'r' ) as f:
                current = json.load(f)
                # current = frozenset(current2.items())
                if  current is None:
                    current = {'info': 'listening', 'info1': ''}
                    self.ui.web_activity_widget.insertHtml(f"<b style='color:#8dffff;'></b> <pre style='color: #8dffff;'>{current}<</pre><br>")

                else:

                    hash_current = frozenset(current.items())
                    if hash_current not in self.lisener:

                        info = current.get('info', '')
                        info1 = current.get('info1', '')
                        payload = current.get('payload','')
                        self.lisener.add(hash_current)

                        print(self.lisener)
                        self.ui.web_activity_widget.insertHtml(f"<b style='color:#8dffff;'></b> <pre style='color: #8dffff;'>{info}<</pre><br>")
                        self.ui.web_activity_widget.insertHtml(f"<b style='color:#8dffff;'></b> <pre style='color: #8dffff;'>{info1}<</pre><br>")
                        self.ui.web_activity_widget.insertHtml(f"<b style='color:red;'></b> <pre style='color: #00ff00;'>{payload}<</pre><br>")
                
                    else:
                        pass            
            
        except FileNotFoundError:
            print("The file 'event_log.json' was not found.")
        except json.JSONDecodeError:
            print("Failed to decode JSON from 'event_log.json'. The file might be empty or contain invalid JSON.")
            # Optionally, you might want to handle this by creating a default JSON or informing the user
            current = {'info': '', 'info1': ''}
            # self.ui.web_activity_widget.insertHtml(f"<b style='color:#8dffff;'></b> <pre style='color: #8dffff;'>{current['info']}</pre><br>")
        except Exception as e:
            print(f"An error occurred: {e}")

    def print_event(self , cmd):
            
        try:
            # listener_tab = Ui_MainWindow.ListenerTab()
            # result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
            # Append each result to the event log
            # self.ui.event_log_widget.append(f"<b style='color:#00ff00;'>Command : </b> {cmd}<br><pre style='color: #00ff00;'></pre><br>")
            self.ui.web_activity_widget.append(f"<b style='color:#00ff00;'>Command : </b> {cmd}<br><pre style='color: #00ff00;'></pre><br>")
        except subprocess.CalledProcessError as e:
            # If command fails, print the error message
            self.ui.web_activity_widget.append(f"Command: {cmd}\nError: {e.output}\n")

   
  

    def stager_window(self):
        self.w = stager_window()
        self.w.show()


    def c4profile(self):
        self.w = c4profile()
        self.w.show()


    def stager(self):
        s = 'stager .....'
        
        self.print_event(s)
        # print ('generating stage 0 msi file reading mp4.......', s)

    def x64_bin(self,s):
        s = 'x64_bin.....'
        self.print_event(s)

        # s = "echo 'generating stageless__x64.bin  file....' " 
        
        # self.printtoevent(s)
        
        # print('generating stageless__x64.bin  file....', s)

    def click(self,s ):
        s = 'click .....'

        self.print_event(s)


    def write(self, s):
        
        print('writing file .... to home dir ')
        os.system('make qt')
    

    # def nc(self):
    #     cmd = f'nc -nvlp {port}'
    #     subprocess.run('date', stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

    def inputbox(self):
        msg = QMessageBox()
        # msg.setIcon(QMessageBox.information)
        msg.setText('LLM agent C2 Project')
        msg.setStyleSheet("color: white; font-size: 16px;")
        msg.setWindowTitle('LLM C2')
        pixmap = QPixmap('images/h12.png')
        msg.setIconPixmap(pixmap)
        # msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()


    def toggle_fullscreen(self,s):
        
        if  self.isFullScreen:
            self.showNormal()
            self.is_FullScreen = False
        else:
            self.showFullScreen()
            self.is_FullScreen = True
    
    def mouseDoubleClickEvent(self,s):
        self.toggle_fullscreen(s)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()

    app.exec()