from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QAction, QIcon
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QHeaderView
from functools import partial
from badgertab import badger_session
import json,os,subprocess
# from c2 import MainWindow
DATA_FILE = 'sessions_database.json'
DATA_FILE2 = 'listenertab.json'

from dir_list import FileBrowser

class badgerterminal(QtWidgets.QWidget):
    
    def __init__(self, parent=None): # need to inherirant the parent
        super().__init__(parent)
        self.badger_dict = self.load_database()
        # self.badger_dict = json.dumps(self.badger_dict) 
        self.badger_num = 0
        self.last_data_state = json.dumps(self.badger_dict)  
        # self.elements = []
        # # print(f'self.elements -->: {self.elements}')
        # self.badger_num = max([int(key) for key in self.badger_dict.keys()] or [0])
        # print(f'Initial self.badger_num -->: {self.badger_num}')

        self.verticalLayout = QtWidgets.QVBoxLayout(self)

        self.title = [
                    "External IP", "Internal IP", "ID", "Host", "UID", "Last Seen (sec)",
                    "PID", "TID", "Process", "Arch/OS (Build)", "Payload Arch", "Pivot Stream", "Note"
                ]
        
    
        self.badger_tab = QtWidgets.QTableWidget()
        self.badger_tab.setColumnCount(13)  # Adjust as necessary for your table
        self.badger_tab.setRowCount(self.badger_num)  # Adjust as necessary
        self.badger_tab.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection) # Improtant: this fixs select multiple row but not all the rows or one row
        self.badger_tab.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.badger_tab.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.badger_tab.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.badger_tab.horizontalHeader().setStretchLastSection(True)
        # self.badger_tab.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.badger_tab.setHorizontalHeaderLabels(self.title)
        self.badger_tab.setStyleSheet("""
                                        
    QTableWidget {
        background-color: #1B1B1B;  /* Very dark background #1B1B1B*/
        color: white;  /* Text color */
        gridline-color: black;  /* Grid lines color */
        border: 1px solid black;
    }
    QTableWidget::item {
        height: 30px;  /* Row height */
        background-color: #1B1B1B;  /* Dark background for items */
        border-bottom: 0.1px solid black;  /* Horizontal lines (thinner) */
        border-right: 0.1px solid black;   /* Vertical lines (thinner) */
    }
    QTableWidget::item:selected {
        background-color: rgb(100, 0, 0); /* Highlight selected item */
        color: white;  /* Text color for selected items */
    }
    QHeaderView::section {
        background-color: rgb(45, 45, 45);  /* Slightly lighter header background */
        color: white;  /* Header text color */
        font-weight: bold;
        border-right: 0.1px solid black;  /* Add border to header for vertical lines (thinner) */
        border-bottom: 0.1px solid black; /* Add border to header for horizontal lines (thinner) */
    }
    QTableCornerButton::section {
        background-color: rgb(45, 45, 45);  /* Corner button (top-left) color */
        border: 0.1px solid black; /* Thinner corner border */
    }
""")
        self.populate_tab()
      
        self.verticalLayout.addWidget(self.badger_tab)

       

        self.badger_tab.selectionModel().selectionChanged.connect(self.on_selection_chanegd)

        self.last_update_time = self.get_last_update_time()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_for_updates)
        self.timer.start(1000)

    def on_selection_chanegd(self):
        self.total_rows = self.badger_tab.rowCount()
        self.selected_rows = len(self.get_selected_rows())

        if self.total_rows > 0 and self.selected_rows == self.total_rows:
            print("All rows are selected.")
            self.badger_tab.selectAll()
        

    def load_database(self):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except (FileExistsError, json.JSONDecodeError):
            return {}
        
    def save_database(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.badger_dict, f)

    def get_last_update_time(self):
        try:
            return os.path.getmtime(DATA_FILE)
        except FileNotFoundError:
            return None
        
    def get_selected_rows(self):
        total_rows = self.badger_tab.rowCount()
      
        selected_indexes =  [index.row() for index in self.badger_tab.selectionModel().selectedRows()]

        if len(selected_indexes) == total_rows:
        
            return list(range(total_rows))
        
        return selected_indexes
    
    
    def set_selected_rows(self, rows):
        """Restore selection to specified rows. If rows include all indexes, select all rows."""

        total_rows = self.badger_tab.rowCount()

        if (len(rows)) == total_rows:
            self.badger_tab.selectAll()
        else:
            self.badger_tab.clearSelection()
            for row in rows:
                    self.badger_tab.selectRow(row)

        
    def check_for_updates(self):
        selected_rows = self.get_selected_rows()

        current_modified_time = self.get_last_update_time()
        if current_modified_time != self.last_update_time:
            # Update the last known modified time
            self.last_update_time = current_modified_time

            # Reload data and update the dictionary
            self.badger_dict = self.load_database()

            self.refresh_table()
            # Restore previously selected rows

            self.set_selected_rows(selected_rows)
            # self.refresh_table()


    def add_rows(self,elements):
        # for key, elements in self.badger_dict.items():
            row_idx = self.badger_tab.rowCount()
            self.badger_tab.insertRow(row_idx)
            for col_idx, cell_data in enumerate(elements):
                item = QtWidgets.QTableWidgetItem(cell_data)
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled) # readonly
                self.badger_tab.setItem(row_idx, col_idx, item)

    def populate_tab(self):
        print(f'current self.badger_dict: {self.badger_dict}')
        for key, elements in self.badger_dict.items():
            self.add_rows(elements)

    def refresh_table(self):
        self.badger_tab.setRowCount(0) #clear all rows
        self.populate_tab()

    def clear_badger(self):

        selected_indexes  = self.badger_tab.selectionModel().selectedRows()
        
        if not selected_indexes:
            print("no row selected")
            return 

        selected_rows = sorted([index.row() for index in selected_indexes])
        print(f"Selected rows to delete: {selected_rows}")

        # if self.on_selection_chanegd():
        if len(selected_indexes) == self.badger_tab.rowCount():
            
            self.badger_dict = {}
            with open(DATA_FILE, 'w') as f:
                json.dump(self.badger_dict, f)
            self.badger_tab.setRowCount(0)
            self.badger_dict.clear() 
            self.badger_num = 0
            print('All badgers are clearned')
        else:
            # row_num = sorted([index.row() for index in selected_indexes], reverse=True)
            for row in reversed(selected_rows):
                key_to_remove = str(row + 1)
                # row_to_remove = row + 1
                if key_to_remove in self.badger_dict:
                        del self.badger_dict[key_to_remove]
                self.badger_tab.removeRow(row)
                print(f"Row_num {row + 1} Removed")
                
            self.reiindex_badger_dict()

    def reiindex_badger_dict(self):
        self.badger_dict = {str(i+ 1): elements for i, (key, elements) in enumerate(self.badger_dict.items())}
        self.badger_num = len(self.badger_dict)
        self.save_database()
        
    def add_bagders(self, elements):
        # if self.badger_num > 0:
        #     elements = self.badger_dict[self.badger_num]
        # else:
        self.badger_num += 1
        key = str(self.badger_num)
        self.badger_dict[key] = elements
        
        row_idx = self.badger_tab.rowCount()
        self.badger_tab.insertRow(row_idx)

        for col_idx, cell_data in enumerate(elements):
            item = QtWidgets.QTableWidgetItem(cell_data)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled) # readonly
            self.badger_tab.setItem(row_idx, col_idx, item)

        self.save_database()
        print(f'Updated self.badger_dict: {self.badger_dict}')

            #    002611  dark green
            # 1B1B1B      dark
            #002611 drcula

    def badger_menu(self, show_badger):
            # self.show_badger_function = show_badger
            self.badger_tab.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
            self.badger_tab.customContextMenuRequested.connect(lambda pos: self.menu(pos, show_badger))  # show badger tab--->: If you need to define the menu() method like def menu(self, pos, show_badger) where show_badger is passed as an argument, and this function will be passed from outside the class, you can use lambda or partial to pass the show_badger argument when connecting it to the customContextMenuRequested event.
            self.badger_tab.itemDoubleClicked.connect(show_badger) #double mouse clieck 
    

    def menu(self,pos,show_badger):
        menu = QtWidgets.QMenu()
        # self.show_badger_function = show_badger
        
                    
        submenu_action = menu.addAction(QtGui.QIcon('images/h12.png') ,"Show llm-agent.exe")
        submenu_action.triggered.connect(partial(show_badger))
        # submenu_action2 = menu.addAction("Shellcode")
        # submenu_action2.triggered.connect(lambda: self.context_menu_action("Shellcode gen...."))
        submenu_action2 = menu.addAction(QtGui.QIcon('images/h10.png') ,"Remove llm-agent.exe")
        submenu_action2.triggered.connect(lambda: self.clear_badger())

        
        menu.exec(self.badger_tab.viewport().mapToGlobal(pos))

    def context_menu_action(self,action):
        print(action)


    
class Ui_MainWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        super(Ui_MainWindow, self).__init__(parent)
        self.detached_window = {}
        self.timer = QtCore.QTimer(self)
        self.current_index = 0 
        self.timer.timeout.connect(self.check_proximity)
        self.timer.start(100)  # Adjusted timing 

        self.separator = None
        self.separator_created = False 
        # self.badger_num = 0
        # self.element = []
        self.badger_terminal = badgerterminal()
   
    class Overlay(QtWidgets.QWidget):
        def __init__(self,parent=None):
            super().__init__(parent)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)
            self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
            self.setStyleSheet("background-color: rgba(255, 0, 0, 100);")

   
    class Zoominout(QtWidgets.QTextEdit):
         def __init__ (self, parent=None):
            super().__init__(parent)

         def wheelEvent(self, event: QtGui.QWheelEvent):
            # Check if the Ctrl key is pressed while scrolling

             if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
                 if event.angleDelta().y() > 0:
                     self.zoomIn(1)
                 else:
                     self.zoomOut(1)
             else:
                 super().wheelEvent(event)

    class ListenerTab(QtWidgets.QWidget):
    
        def __init__(self, parent=None): # need to inherirant the parent
            
            super().__init__(parent)
            self.brower = FileBrowser()
            self.listner_dict = self.load_database2()
            self.listner_num = 0
            self.last_data_state = json.dumps(self.listner_dict)  


            self.verticalLayout = QtWidgets.QVBoxLayout(self)
            self.listner_tab = QtWidgets.QTableWidget()
            self.listner_tab.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection) # Improtant: this fixs select multiple row but not all the rows or one row

            self.listner_tab.setColumnCount(7)  
            self.listner_tab.setRowCount(self.listner_num)  
            self.listner_tab.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

            # self.listner_tab.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
            self.listner_tab.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Stretch rows to fit content dynamically
            self.listner_tab.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

            # Optionally, set the resizing of the headers
            self.listner_tab.horizontalHeader().setStretchLastSection(True)
            title = [
                        "Name", "Auth", "Host", "Port", "SSL", "Type",
                        "URL(s)"]

           # below code should only be triggred when c4profile's save button is clicked. 

            # self.elements = ["http-listener", "YES", "127.0.0.1", "4444", "YES" , "NULL" ,"openai/index.html/1231233123213123131231233123.exe" ]
            # # elements = []

            self.listner_tab.setHorizontalHeaderLabels(title)

            self.elements = []

            self.listner_tab.setStyleSheet("""
        QTableWidget {
            background-color: #1B1B1B;  /* dark dimmer green background */
            color: white;  /* Text color */
            gridline-color: black;  /* Grid lines color */
            border: 1px solid black;
                                           
        }
        QTableWidget::item {
            height: 30px;  /* Row height */
            background-color: #1B1B1B;  /* Dark background for items */
            border-bottom: 0.1px solid black;  /* Horizontal lines (thinner) */
            border-right: 0.1px solid black;   /* Vertical lines (thinner) */
        }
        QTableWidget::item:selected {
            background-color: rgb(100, 0, 0); /* Highlight selected item */
            color: white;  /* Text color for selected items */
        }
        QHeaderView::section {
            background-color: rgb(45, 45, 45);  /* Slightly lighter header background */
            color: white;  /* Header text color */
            font-weight: bold;
            border-right: 0.1px solid black;  /* Add border to header for vertical lines (thinner) */
            border-bottom: 0.1px solid black; /* Add border to header for horizontal lines (thinner) */
        }
        QTableCornerButton::section {
            background-color: rgb(45, 45, 45);  /* Corner button (top-left) color */
            border: 0.1px solid black; /* Thinner corner border */
        }
    """)

            self.verticalLayout.addWidget(self.listner_tab)
            self.populate_tab()

            self.listner_tab.selectionModel().selectionChanged.connect(self.on_selection_chanegd)

            self.listner_tab.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
            self.last_update_time = self.get_last_update_time()
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.check_for_updates)
            self.timer.start(1000)
            self.elements = []

        def on_selection_changed(self):
            self.total_rows = self.listner_tab.rowCount()
            self.selected_rows = len(self.selected_rows)

        def load_database2(self):
            try:
                with open(DATA_FILE2) as f:
                    return json.load(f)
            except (FileExistsError, json.JSONDecodeError):
                return {}
            
        def get_selected_rows(self):
            total_rows = self.listner_tab.rowCount()

            selected_indexes = [index.row() for index in self.listner_tab.selectionModel().selectedRows()]

            if len(selected_indexes) == total_rows:
                return list(range(total_rows))
            
            return selected_indexes
        
        def set_selected_rows(self, rows):

            total_rows = self.listner_tab.rowCount()

            if (len(rows)) == total_rows:
                self.listner_tab.selectAll()
            else:
                self.listner_tab.clearSelection()
                for row in rows:
                    self.listner_tab.selectRow(row)


        def get_last_update_time(self):
            try:
                return os.path.getmtime(DATA_FILE2)
            except FileNotFoundError:
                return None
            
        def check_for_updates(self):
            selected_rows = self.get_selected_rows()

            current_modified_time = self.get_last_update_time()
            if current_modified_time != self.last_update_time:
                # Update the last known modified time
                self.last_update_time = current_modified_time

                # Reload data and update the dictionary
                self.listner_dict = self.load_database2()

                self.refresh_table()
                # Restore previously selected rows

                self.set_selected_rows(selected_rows)



        def add_rows(self,elements):
            # for key, elements in self.badger_dict.items():
                row_idx = self.listner_tab.rowCount()
                self.listner_tab.insertRow(row_idx)
                for col_idx, cell_data in enumerate(elements):
                    item = QtWidgets.QTableWidgetItem(cell_data)
                    item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled) # readonly
                    self.listner_tab.setItem(row_idx, col_idx, item)

        def populate_tab(self):
            print(f'current self.listner_dict: {self.listner_dict}')
            for key, elements in self.listner_dict.items():
                self.add_rows(elements)

        def refresh_table(self):
            self.listner_tab.setRowCount(0) #clear all rows
            self.populate_tab()

            
        def save_database(self):
            with open(DATA_FILE2, 'w') as f:
                json.dump(self.listner_dict, f)

        def on_selection_chanegd(self):
            self.total_rows = self.listner_tab.rowCount()
            self.selected_rows = len(self.get_selected_rows())

            if self.total_rows > 0 and self.selected_rows == self.total_rows:
                print("All rows are selected.")
                self.listner_tab.selectAll()

        def clear_listener(self):

            selected_indexes  = self.listner_tab.selectionModel().selectedRows()
            
            if not selected_indexes:
                print("no row selected")
                return 

            selected_rows = sorted([index.row() for index in selected_indexes])
            print(f"Selected rows to delete: {selected_rows}")

            # if self.on_selection_chanegd():
            if len(selected_indexes) == self.listner_tab.rowCount():
                
                self.listner_dict = {}
                with open(DATA_FILE2, 'a') as f:
                    json.dump(self.listner_dict, f)
                self.listner_tab.setRowCount(0)
                self.listner_dict.clear() 
                self.listner_num = 0
                print('All listners are clearned')
            else:
                # row_num = sorted([index.row() for index in selected_indexes], reverse=True)
                for row in reversed(selected_rows):
                    key_to_remove = str(row + 1)
                    # row_to_remove = row + 1
                    if key_to_remove in self.listner_dict:
                            del self.listner_dict[key_to_remove]
                    self.listner_tab.removeRow(row)
                    print(f"Row_num {row + 1} Removed")
                    
                self.reiindex_listener_dict()

        def reiindex_listener_dict(self):
            self.listner_dict = {str(i+ 1): elements for i, (key, elements) in enumerate(self.listner_dict.items())}
            self.listner_num = len(self.listner_dict)
            self.save_database()
          

        def listener_menu(self, show_listner):
                # self.show_badger_function = show_badger
                self.listner_tab.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
                self.listner_tab.customContextMenuRequested.connect(lambda pos: self.menu(pos, show_listner))  # show badger tab--->: If you need to define the menu() method like def menu(self, pos, show_badger) where show_badger is passed as an argument, and this function will be passed from outside the class, you can use lambda or partial to pass the show_badger argument when connecting it to the customContextMenuRequested event.
                self.listner_tab.itemDoubleClicked.connect(show_listner) #double mouse clieck 
        

        def menu(self,pos,show_listner):
            menu = QtWidgets.QMenu()



            button_action4 = QAction(QtGui.QIcon('images/h3.png'), 'x64-bin-actions', self)
            button_action4.setStatusTip('x64-bin')
            button_action4.triggered.connect(self.x64_bin)
            button_action4.setCheckable(True)

            remove_lisener = menu.addAction(QtGui.QIcon('images/h10.png') ,"Remove listener")
            remove_lisener.triggered.connect(lambda: self.clear_listener())
            submenu_action1 = menu.addMenu(QtGui.QIcon('images/h3.png'), 'Payloads')
            # submenu_action1.triggered.connect(lambda: self.x64_bin('x64 bin'))

            file_submenu2 = submenu_action1.addMenu(QtGui.QIcon('images/h3.png'), 'x64 Payloads')
            file_submenu2 = file_submenu2.addMenu(QtGui.QIcon('images/h3.png'), 'llm-agent_x64.bin')
            file_submenu2.addAction(button_action4)
        
            file_submenu3 = submenu_action1.addMenu(QtGui.QIcon('images/h3.png'), 'x32 Payloads')
            file_submenu3 = file_submenu3.addMenu(QtGui.QIcon('images/h3.png'), 'llm-agent_x32.bin')

            file_submenu3.addAction(button_action4)


            stagers = menu.addMenu(QtGui.QIcon("images/h5.png"), "&Stagers")
            stagers0 = stagers.addMenu(QtGui.QIcon("images/h5.png"), "&Stagers-0")
            stagers1 = stagers.addMenu(QtGui.QIcon("images/h5.png"), "&Stagers-1")
            stagers0.addAction(button_action4)
            stagers1.addAction(button_action4)

            menu.exec(self.listner_tab.viewport().mapToGlobal(pos))

        def context_menu_action(self,action):
            print(action)
    

        def stager(self):
            # s = 'cd /home/kali/Desktop/c2/GPT-C2/pic_stager/ && make'
            self.brower.show()

            # ui.print_event2(s)
            # ui.event_log_widget.insertHtml(f"<b style='color:#00ff00;'>Command : </b> {s}<br><pre style='color: #ffcc00;'></pre><br>")
            # ui.web_activity_widget.append(f"<b style='color:#00ff00;'>Command : </b> {s}<br><pre style='color: #ffcc00;'></pre><br>")
            # subprocess.run(s, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            # print(f'done running {s}')

        def x64_bin(self,s):
            self.brower.show()

            
            # ui.print_event2(s)
            # ui.web_activity_widget.append(f"<b style='color:#00ff00;'>Command : </b> {s}<br><pre style='color: #ffcc00;'></pre><br>")

            # subprocess.run(s, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            print(f'done running {s}')
            
        # def print_event(self , s):
        #     self.ui = stager_window()
        #     self.ui.print_event
        #     print(f'from print_event {s}')
        #     self.ui.web_activity_widget.append(f"<b style='color:#00ff00;'>Command : </b> {s}<br><pre style='color: #00ff00;'></pre><br>")

        def add_listener(self, elements):
             # if self.badger_num > 0:
            #     elements = self.badger_dict[self.badger_num]
            # else:
            print(f'adding elements {elements}')
            self.listner_num += 1
            key = str(self.listner_num)
            self.listner_dict[key] = elements
            
            row_idx = self.listner_tab.rowCount()
            self.listner_tab.insertRow(row_idx)

            for col_idx, cell_data in enumerate(elements):
                item = QtWidgets.QTableWidgetItem(cell_data)
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled) # readonly
                self.listner_tab.setItem(row_idx, col_idx, item)

            self.save_database()
            print(f'Updated self.listner_dict: {self.listner_dict}')


            

    



    def setupUi(self, MainWindow):


        
        MainWindow.setObjectName("MainWindow")
        # MainWindow.resize(1800, 1200)  #

        # central widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        # MainWindow.setCentralWidget(self.centralwidget)
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)

# ============================ Dont move this is constant badger session=================

        self.Listeners = self.ListenerTab()
        self.main_vertical_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical, self.centralwidget)
        self.badger = QtWidgets.QTabWidget()
 
        self.bottom_horizontal_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.left_vertical_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)

        for tab_name in ["Listeners", "LLM-Agents", "Creds", "Downloads", "AutoPilot", "Voice-Model"]:

                       
            if tab_name == "Listeners":
                self.Listeners = self.ListenerTab()
                self.Listeners.listener_menu(self.show_listener)
                # self.badger_terminal = self.ListenerTab()
                self.badger.addTab(self.Listeners , tab_name)
            
            elif tab_name == "LLM-Agents":
            
                self.badger_terminal = badgerterminal() 
                self.badger_terminal.badger_menu(self.show_badger)
                 # opens a badger session when clicks #important!!!
                self.badger.addTab(self.badger_terminal , tab_name)
            
            else:
                tab = QtWidgets.QWidget()
                self.layout = QtWidgets.QVBoxLayout(tab)
                self.baderwidget = self.Zoominout()
                self.baderwidget.setReadOnly(True)
                self.baderwidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                self.baderwidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                self.baderwidget.setReadOnly(True) 

                
                self.layout.addWidget(self.baderwidget)
                self.badger.addTab(tab, tab_name)
            # self.badger.addTab(tab , tab_name)

        self.main_vertical_splitter.addWidget(self.badger)
    

# ============================ Dont move this is the constant badger session    ================
       
    #    ================= exit box ============
   
   

        self.counting_left = QLabel("Current TIme: >: --:--:--")
        self.counting_left.setStyleSheet("font-size: 15px; color: #00ff00;")


        self.exit_button = QPushButton("Exit C2")
        self.exit_button.clicked.connect(QApplication.instance().quit)
        
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.counting_left, alignment=Qt.AlignmentFlag.AlignLeft)
        # self.button_layout.addStretch()
        self.button_layout.addWidget(self.exit_button, alignment=Qt.AlignmentFlag.AlignRight)
        


#  ==========================  event, web and gpt group bexes ==========================================
       
       
        # self.bottom_horizontal_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        # self.left_vertical_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)

        self.event_log_groupbox = QtWidgets.QGroupBox("Event Logs")
        self.event_log_layout = QtWidgets.QVBoxLayout(self.event_log_groupbox)
        self.event_log_widget = self.Zoominout(self.event_log_groupbox)
        self.event_log_widget.setReadOnly(True)
        self.event_log_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.event_log_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.event_log_layout.addWidget(self.event_log_widget)
        # self.main_vertical_splitter.addWidget(self.badger)

        self.left_vertical_splitter.addWidget(self.event_log_groupbox)
     

        # Web Activities Section (bottom part of left splitter)
        self.web_activities_groupbox = QtWidgets.QGroupBox("Web Activities")
        self.web_activities_layout = QtWidgets.QVBoxLayout(self.web_activities_groupbox)
        self.web_activity_widget  = QtWidgets.QTextEdit(self.web_activities_groupbox)
        self.web_activity_widget.setReadOnly(True)
        self.web_activity_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.web_activity_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.web_activities_layout.addWidget(self.web_activity_widget )
        self.left_vertical_splitter.addWidget(self.web_activities_groupbox)
        # Add the left splitter to the bottom horizontal splitter
        self.left_vertical_splitter.setCollapsible(0, False)
        self.left_vertical_splitter.setCollapsible(1, False)
        self.bottom_horizontal_splitter.addWidget(self.left_vertical_splitter)


        self.GPTWidget = QtWidgets.QTabWidget()
        self.Listeners = self.ListenerTab()
        # self.GPTWidget.addTab(self.Listeners, "Listensers")
        for tab_label in ["AutoPilot", "Traning", "Log"]:
            if tab_label == 'GPT':
                self.Listeners = self.ListenerTab()
                self.GPTWidget.addTab(self.Listeners, tab_label)

            else:
                tab = QtWidgets.QWidget()
                layout = QtWidgets.QVBoxLayout(tab)
                self.textwidget = self.Zoominout()
                self.textwidget.setReadOnly(True)
                self.textwidget.setText('<span style="color:red;"></span><br>')
                self.textwidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                self.textwidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                layout.addWidget(self.textwidget)
            # tab.setObjectName(tab_name)
                self.GPTWidget.addTab(tab, tab_label)

        self.bottom_horizontal_splitter.addWidget(self.GPTWidget)
        
        self.bottom_horizontal_splitter.setStretchFactor(0,1)
        # self.bottom_horizontal_splitter.setStretchFactor(1,2)
        
        self.bottom_horizontal_splitter.setStyleSheet("""
    QTextEdit {
        selection-background-color:  #8B0000;  /* Change highlight color to red */
    }
   """)

        # # Adding bottom splitter to main vertical splitter
        self.main_vertical_splitter.addWidget(self.bottom_horizontal_splitter)
        self.main_layout.addWidget(self.main_vertical_splitter) # important
        self.main_vertical_splitter.setCollapsible(0, False)   # Now it's safe to set collapsible
        self.main_vertical_splitter.setCollapsible(1, False)
        self.bottom_horizontal_splitter.setCollapsible(0, False)
        self.bottom_horizontal_splitter.setCollapsible(1, False)

        self.apply_dark_theme(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.maintabWidget = QtWidgets.QTabWidget()
        self.maintabWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        maincontainer_widget = QtWidgets.QWidget()
        maincontainer_layout = QtWidgets.QVBoxLayout(maincontainer_widget)
        maincontainer_layout.addWidget(self.main_vertical_splitter) # important
        self.maintabWidget.addTab(maincontainer_widget, "Watchlist")


        self.main_layout.addWidget(self.maintabWidget) # important
        self.main_layout.addLayout(self.button_layout) # important

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.update_time()
        # self.main_layout.addWidget(self.counting_left) # important
        # self.badger_terminal.badger_menu(self.show_badger) # opens a badger session when clicks
            

        self.desktop_names = [
                'Desktop-1', 'Desktop-2', 'Desktop-3', 'Desktop-4', 'Desktop-5',
                'Desktop-6', 'Desktop-7', 'Desktop-8', 'Desktop-9', 'Desktop-10',
                'Desktop-11', 'Desktop-12', 'Desktop-13'
            ]
    
        self.current_index = 0 # Start with the first index

    def update_time(self):
        current_time = datetime.now().strftime("%a %d %b %H:%M:%S %Z %Y")
        self.counting_left.setText(f"Current time >: {current_time}")


    def print_event2(self , s):

        try:
            # listener_tab = Ui_MainWindow.ListenerTab()
            # result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
            # Append each result to the event log
            self.event_log_widget.insertHtml(f"<b style='color:#00ff00;'>Command : </b> {s}<br><pre style='color: #00ff00;'></pre><br>")
            self.web_activity_widget.insertHtml(f"<b style='color:#00ff00;'>Command : </b> {s}<br><pre style='color: #00ff00;'></pre><br>")
        except subprocess.CalledProcessError as e:
            # If command fails, print the error message
            self.web_activity_widget.insertHtml(f"Command: {s}\nError: {e.output}\n")


    def show_badger(self):

        # self.detached_windows = {}
         
        self.badgerWidget = QtWidgets.QTabWidget()
        self.badger_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical,self.badgerWidget)
        # self.badger_splitter_hol = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal,self.badgerWidget)
        self.badgerWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        self.badgercontainer_layout = QtWidgets.QVBoxLayout(self.badgerWidget)
        self.badger_terminal = badgerterminal() #important!!!
      #important!!!
        self.badger_splitter.addWidget(self.badger_terminal) # self.badger_terminal here not self.badgerWidget else will will stuck
       
# Add your table or any widget on the left side of the splitte  vertical split badger tab at top
        

# container to hold the badger to be detached or reattach
        self.target_widget = QtWidgets.QWidget()
        self.target_layout = QtWidgets.QVBoxLayout(self.target_widget)

# ==================== badger terminal 
        self.form = QtWidgets.QWidget()
        self.badger_ui = badger_session()
        self.badger_ui.setupUi(self.form)

# container to hold the badger to be detached or reattach
       
        self.target_layout.addWidget(self.form)
        self.badger_splitter.addWidget(self.target_widget)
   
        self.badgercontainer_layout.addWidget(self.badger_splitter)

        # self.target_widget.setStyleSheet("border: 1px solid black;")




# ==================== badger tabs 

        self.badgername = self.desktop_names[self.current_index]
        self.tab_index = self.maintabWidget.addTab(self.badgerWidget, f"{self.badgername}") #improtant not casue tab conflicts
        
        self.maintabWidget.setTabsClosable(True)
        self.maintabWidget.setMovable(True)
        self.maintabWidget.setAcceptDrops(True)

        self.drag_start_pos = None
        # self.detached_window = {}

        self.tab_Bar = self.maintabWidget.tabBar()
        # self.tab_Bar.installEventFilter(self)
        self.index = self.maintabWidget.currentIndex()

        # self.timer = QtCore.QTimer(self)
        # self.timer.timeout.connect(self.check_proximity)
        # self.timer.start(100)

        if self.tab_Bar:
            print("Tab bar initialized successfully.")
            self.tab_Bar.installEventFilter(self)
            self.tab_Bar.tabBarDoubleClicked.connect(self.on_tab_double_clicked)
            # self.tab_Bar.tabCloseRequested.connect(on_close_tab)
        else:
            print("Tab bar is None.")

        self.maintabWidget.setCurrentIndex(self.tab_index)
        self.close_tab  = self.badger_ui.pushButton #signal the pushbotton to close the tab

        def close_current_tab():
            index = self.maintabWidget.currentIndex()
            if index != 0:
                # self.current_index -= 1
                self.maintabWidget.removeTab(index)
                self.detached_window.pop(index) #using self.maintabWidget.currentIndex() to track current tab to close else you can only close the tab you just created but can't close the previous ones 
        self.close_tab.clicked.connect(close_current_tab)


        self.current_index +=1
        if self.current_index >= len(self.desktop_names):
            self.current_index = 0
        
        self.badger_splitter.setCollapsible(0,False)
        self.badger_splitter.setCollapsible(1,False)
        self.badger_terminal.badger_menu(self.show_badger)

    def show_listener(self):

        # self.detached_windows = {}
         
        self.listenerWidget = QtWidgets.QTabWidget()
        self.listener_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical,self.listenerWidget)
        # self.badger_splitter_hol = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal,self.badgerWidget)
        self.listenerWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)
        self.listenercontainer_layout = QtWidgets.QVBoxLayout(self.listenerWidget)
        self.listener_terminal = self.ListenerTab() #important!!!
      #important!!!
        self.listener_splitter.addWidget(self.listener_terminal) # self.badger_terminal here not self.badgerWidget else will will stuck
       
        self.target_widget = QtWidgets.QWidget()
        self.target_layout = QtWidgets.QVBoxLayout(self.target_widget)

        self.form = QtWidgets.QWidget()
        self.listener_ui = badger_session()
        self.listener_ui.setupUi(self.form)

        self.target_layout.addWidget(self.form)
        self.listener_splitter.addWidget(self.target_widget)
   
        self.listenercontainer_layout.addWidget(self.listener_splitter)

        self.badgername = self.desktop_names[self.current_index]
        self.tab_index = self.maintabWidget.addTab(self.listenerWidget, f"{self.badgername}") #improtant not casue tab conflicts
        
        self.maintabWidget.setTabsClosable(True)
        self.maintabWidget.setMovable(True)
        self.maintabWidget.setAcceptDrops(True)

        self.drag_start_pos = None
        # self.detached_window = {}

        self.tab_Bar = self.maintabWidget.tabBar()
        # self.tab_Bar.installEventFilter(self)
        self.index = self.maintabWidget.currentIndex()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_proximity)
        self.timer.start(100)

        if self.tab_Bar:
            print("Tab bar initialized successfully.")
            self.tab_Bar.installEventFilter(self)
            self.tab_Bar.tabBarDoubleClicked.connect(self.on_tab_double_clicked)
            # self.tab_Bar.tabCloseRequested.connect(on_close_tab)
        else:
            print("Tab bar is None.")

        self.maintabWidget.setCurrentIndex(self.tab_index)
        self.close_tab  = self.badger_ui.pushButton #signal the pushbotton to close the tab

        def close_current_tab():
            index = self.maintabWidget.currentIndex()
            if index != 0:
                # self.current_index -= 1
                self.maintabWidget.removeTab(index)
                self.detached_window.pop(index) #using self.maintabWidget.currentIndex() to track current tab to close else you can only close the tab you just created but can't close the previous ones 
        self.close_tab.clicked.connect(close_current_tab)


        self.current_index +=1
        if self.current_index >= len(self.desktop_names):
            self.current_index = 0
        
        self.listener_splitter.setCollapsible(0,False)
        self.listener_splitter.setCollapsible(1,False)
        self.listener_terminal.listener_menu(self.show_listener)

    def on_tab_double_clicked(self):
            index = self.maintabWidget.currentIndex()
    # Handle the double click event on a tab
            print('Double click triggered, index:', index)
            if index != 0:
                self.detach_widget()

    def red_shadow(self,widget1, widget2):
     
        orientation = self.determin_orientation(widget1, widget2)
        orientation
        # overlay = self.Overlay(widget)
        # # overlay.resize(widget.size())
        # overlay.show()
        try:
            if self.separator_created:
                return
            
            self.separator = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal,self.target_widget)
            # self.separator = QtWidgets.QWidget()
            # self.badger_splitter_hol = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal,self.badgerWidget)
            self.separator.setFixedHeight(4)
            self.separator.setStyleSheet("background-color: rgba(255, 0, 0, 180);")
            self.combined_container = QtWidgets.QSplitter(orientation, self.listenerWidget)
            self.combined_container.setCollapsible(0,False)
            self.combined_container.setCollapsible(1,False)
            
            
            layout = QtWidgets.QVBoxLayout()
            layout.setContentsMargins(0,0,0,0)
            layout.addWidget(widget1)
            layout.addWidget(self.separator)
            layout.addWidget(widget2)


            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(800)
            shadow.setColor(QtGui.QColor(255,0,0,180))
            shadow.setOffset(1,1)
            self.target_widget.setGraphicsEffect(shadow)
            # widget2.setGraphicsEffect(shadow)

            self.combined_container = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal,self.listenerWidget)
            self.combined_container.setLayout(layout)
            self.combined_container.setCollapsible(0,False)
            self.combined_container.setCollapsible(1,False)
            self.combined_container.setGraphicsEffect(shadow)


            self.separator_created = True

            return self.combined_container
        except Exception as e:
            print(f"error: {e}")        


    def remove_redshadow(self):

        try:   
             if self.separator_created:
                # self.target_widget.setGraphicsEffect(None)
                # self.combined_container.setGraphicsEffect(None)
                # self.current_index -= 1
                self.separator.deleteLater()  # Delete the separator widget
                self.separator = None
                self.separator_created = False
        except Exception as e:
            print(f"Error removing red shadow: {e}")

    def detach_widget(self):
        detached_form = QtWidgets.QWidget()
        detached_ui = badger_session()  # Assuming `badger_session()` is the UI setup for each tab
        detached_ui.setupUi(detached_form)

        detached_form.hide()
        detached_form.setParent(self.form)


        # Set properties for the new detached form
        self.form.setWindowFlags(
            QtCore.Qt.WindowType.Window |  # Standard window frame to allow resizing and moving
            QtCore.Qt.WindowType.WindowStaysOnTopHint  # Keep the window on top
        )
        self.form.setAcceptDrops(True)
        self.form.setWindowTitle(f"Tab {self.current_index + 1}")  # Update the title for clarity
        self.form.setStyleSheet("""
            QWidget {
                background-color: rgb(30, 30, 30);
                color: #ffffff;
            }
        """)
        self.form.resize(900, 600)
        self.form.show()

        # Increment index to keep track of new tabs
        self.current_index += 1
        self.detached_window[self.current_index] = self.form


    def reattach_widget(self):
        index = self.maintabWidget.currentIndex()
        if index in self.detached_window:

            detached_window = self.detached_window.pop(index)
            
            layout = detached_window.layout()
            widget = layout.itemAt(0).widget()

            if detached_window:
                detached_window.hide()
                detached_window.setParent(self.target_widget)
                detached_window.setWindowFlags(QtCore.Qt.WindowType.Widget)
                self.target_layout.addWidget(detached_window)
                detached_window.show()

            # self.badgercontainer_layout.addWidget(self.form)
                self.badger_splitter.addWidget(self.form)
    
    def check_proximity(self):
        # print(f"Detached windows: {self.detached_window}")
        indicis = list(self.detached_window.keys())
        proximity_threshold = 80

        if not indicis:
            # print("Not enough indicis windows to check proximity.")
            return
        
        print("Checking proximity between detached windows...")
        
        for index in indicis:
            print(f'index if indicies:  {index}')
            window = self.detached_window.get(index)
            if not window:
                continue

            print(f'got window {window}')
    
    # for i in range(len(indicis)):
    #     for j in range(i+1, len(indicis)):
    #         index1 = indicis[i]
    #         index2 = indicis[j]

    #         window1 = self.detached_window[index1]
    #         window2 = self.detached_window[index2]

            try:
                window.updateGeometry()
                self.target_widget.updateGeometry()
                pos1 = window.geometry()
                pos2 = self.target_widget.geometry()

                # if not window1 or not window2:
                #     print(f"Error: One of the windows ({index1} or {index2}) is missing.")
                #     continue
            
            
                print(f"Detached window {index} geometry: {pos1}")
                print(f"Target widget geometry: {pos2}")


                if pos1.height() == 0 or pos2.height() == 0:
                    print("Error: One of the windows has a height of 0. Skipping proximity check.")
                    continue  # Skip this check if height is 0 to avoid errors



                if (abs(pos1.x() - pos2.x()) < proximity_threshold and abs(pos1.y() - pos2.y()) < proximity_threshold):

                    print(f"Windows {index} is  close to {self.form}. Setting red border.")
                    
                    if not self.separator_created:
                        combined_container = self.red_shadow(self.form, window)

                        combined_container.setCollapsible(0,False)
                        combined_container.setCollapsible(1,False)
                        self.badger_splitter.addWidget(combined_container)
                        self.badger_splitter.setCollapsible(0,False)
                        self.badger_splitter.setCollapsible(1,False)
                      
                        break
                    
                    # window1.setStyleSheet("border: 4px solid red; background-color: rgba(255, 0, 0, 50);")
                    # window2.setStyleSheet("border: 4px solid red; background-color: rgba(255, 0, 0, 50);")
                    # # self.combining_widget(window1, window2, index1, index2)
                    # self.red_shadow(self.target_widget)
                    # self.red_shadow(window)
                
                    # window1.update()
                    # window2.update()

                else:
                    self.remove_redshadow()
                    break
                    # self.remove_redshadow(window)


                    # window1.setStyleSheet("border: none; background-color: none;")
                    # window2.setStyleSheet("border: none; background-color: none;")
                    
                    # # Force style update
                    # window1.update()
                    # window2.update()
            except Exception as e:
                print(f"Error in proximity check: {e}") 


    def determin_orientation(self, w1, w2):
        ract1 = w1.geometry()
        ract2 = w2.geometry()

        if abs(ract1.x() - ract2.x()) > abs(ract1.y() - ract2.y()):
            return QtCore.Qt.Orientation.Horizontal
        else:
            return QtCore.Qt.Orientation.Vertical


    def combining_widget(self,w1,w2, index1, index2):

            orientation = self.determin_orientation(w1,w2)

        # if index1 in self.detached_window and index2 in self.detached_window:

            w1 = self.detached_window.pop(index1)
            w2 = self.detached_window.pop(index2)

            widget1 = w1.layout().itemAt(0).widget()
            widget2 = w2.layout().itemAt(0).widget()

            w1.hide()
            w2.hide()

            new_slitter = QtWidgets.QSplitter(orientation)
            new_slitter.addWidget(widget1)
            new_slitter.addWidget(widget2)

            combined_widget = QtWidgets.QWidget()
            combined_layout = QtWidgets.QVBoxLayout(combined_widget)
            combined_layout.addWidget(new_slitter)
            self.maintabWidget.insertTab(index1, combined_widget, f"combined tab {self.index + 1}")

            self.detached_window.pop(index1, None)
            self.detached_window.pop(index2, None)

                
   
    def eventFilter(self, source, event):
                
        if source == self.tab_Bar:
            if event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
                index = self.tab_Bar.tabAt(event.pos())
                if index != 0:
                    print(f"Double click triggered on tab index: {index}")
                    self.detach_widget()
                
                return True
            
            # elif event.type() == QtCore.QEvent.Type.MouseButtonRelease:
    
            #     if event.button() == QtCore.Qt.MouseButton.LeftButton and self.drag_start_pos:
            #         index = self.tab_Bar.tabAt(event.pos())
            #         if index >= 0:
            #              print(f"Mouse release triggered on tab index: {index}")
            #              self.reattach_widget()

            #         indices = list(self.detached_window.keys())
            #         for i in range(len(indices)):
            #             for j in range(i + 1, len(indices)):
            #                 index1 = indices[i]            
            #                 index2 = indices[j]
            #                 if self.check_proximity():
            #                     #  self.reattach_widget()
            #                     self.combining_widget(self.detached_window[index1], self.detached_window[index2],index1, index2)            

            #         self.drag_start_pos = None

            #     return True
                    
        return super().eventFilter(source, event)
            
      
    def apply_dark_theme(self, MainWindow):
            
            # Dark theme style
            dark_style = """
                QMainWindow {
                    background-color: #1B1B1B;
                    color: #ffffff;
                }
        
                QWidget {
                    background-color: #1B1B1B;
                    color: #ffffff;
                }
                QTabWidget::pane {
                
                    border: 1px solid #2e2e2e;
                }
                QTabBar::tab {
                    background-color: rgb(50, 50, 50);
                    padding: 5px;
                    border: 1px solid #2e2e2e;
                }
                QTabBar::tab:selected {
                    background-color: rgb(68, 77, 88);
                }

              
                QTreeWidget {
                
                    background-color: #1B1B1B;
                    border: none;
                    color: #ffffff;
                }
                QGroupBox {
                
                    border: 1px solid #3c3c3c;
                    margin-top: 6px;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 3px;
                }
                QMenuBar {
                    background-color: #2e2e2e;
                    color: #ffffff;
                }
                QMenuBar::item:selected {
                    background-color: #3c3c3c;
                }
                QStatusBar {
                    background-color: #2e2e2e;
                    color: #ffffff;
                }
            """
            MainWindow.setStyleSheet(dark_style)




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    

    MainWindow.show()
    ui.show()
    
    sys.exit(app.exec())