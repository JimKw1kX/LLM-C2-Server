#!/usr/bin/python3
import os, subprocess,json

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QTreeWidget, 
    QTreeWidgetItem, QTableWidget, QTableWidgetItem, QPushButton, QFormLayout, 
    QLineEdit, QLabel, QFileDialog, QMessageBox,QHeaderView,QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon


class FileBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("File Explorer")
        self.setGeometry(500, 250, 1100, 700)

        # Splitter to divide tree and table views
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        self.setCentralWidget(main_splitter)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(splitter)    

        
        # Directory tree widget
        self.directory_tree = QTreeWidget()
        self.directory_tree.setHeaderLabel("Directories")
        self.directory_tree.itemClicked.connect(self.on_tree_item_click)
        splitter.addWidget(self.directory_tree)

        # File table widget
        self.file_table = QTableWidget(0, 3)
        
        self.file_table.setHorizontalHeaderLabels(["Name", "Size", "Modified"])
        header = self.file_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch) # streach so each header spreads evenly
        
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows) # select the who row instead of one block
        
        splitter.addWidget(self.file_table)

        # splitter.setStretchFactor(5, 5)
        splitter.setStretchFactor(0, 2)  # Tree + Table gets 5/6 of the space
        splitter.setStretchFactor(1, 2)  # Path + Buttons get 1/6

        
        nav_widget = QWidget()
        nav_layout = QFormLayout(nav_widget)
        main_splitter.addWidget(nav_widget)

        # Directory path input and "Go Up" button
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter directory path or navigate through the tree")
        nav_layout.addRow("Path:", self.path_input)

        self.go_up_button = QPushButton("Go Up")
        self.go_up_button.clicked.connect(self.go_up_directory)
        nav_layout.addRow(self.go_up_button)

        # Save file button
        self.save_file_button = QPushButton("&Save")
        self.save_file_button.clicked.connect(self.select_directory_and_save_file)
        nav_layout.addRow(self.save_file_button)

        main_splitter.setStretchFactor(0,5)
        main_splitter.setStretchFactor(1,1)

        # Populate the initial directory tree
        self.populate_directory_tree()

        # Apply custom stylesheet
        self.setStyleSheet(self.load_stylesheet())

    def load_stylesheet(self):
        # Custom dark-themed stylesheet
        return """
        QMainWindow {
            background-color: rgb(20, 20, 20);
            color: #f8f8f2;
        }
        QTreeWidget {
            background-color: rgb(20, 20, 20);
            color: #f8f8f2;
            border: 1px solid rgb(20, 20, 20);
        }
        QTableWidget {
            background-color: rgb(20, 20, 20);
            color: #f8f8f2;
            gridline-color: rgb(20, 20, 20);
            border: 1px solid rgb(20, 20, 20);
        }
        QLineEdit {
            background-color: rgb(20, 20, 20);
            color: #f8f8f2;
            border: 1px solid #6272a4;
        }
        QPushButton {
            background-color: rgb(20, 20, 20);
            color: #f8f8f2;
            border: 1px solid #6272a4;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #6272a4;
        }
        QHeaderView::section {
            background-color: rgb(20, 20, 20);
            color: #f8f8f2;
            border: 1px solid #6272a4;
        }
        """

    def populate_directory_tree(self, path=os.path.expanduser("~")):
        # Set the root path in the tree view
        self.directory_tree.clear()
        root_item = QTreeWidgetItem(self.directory_tree, [path])
        root_item.setIcon(0, QIcon.fromTheme("folder"))
        self.add_subdirectories(root_item, path)
        self.directory_tree.addTopLevelItem(root_item)
        self.directory_tree.expandItem(root_item)

    def add_subdirectories(self, parent_item, path):
        try:
            for entry in os.scandir(path):
                if entry.is_dir():
                    child_item = QTreeWidgetItem(parent_item, [entry.name])
                    child_item.setIcon(0, QIcon.fromTheme("folder"))
                    child_item.setData(0, Qt.ItemDataRole.UserRole, entry.path)
                    parent_item.addChild(child_item)
        except PermissionError as e:
            print(e)
            pass  # Ignore directories without permission access

    def on_tree_item_click(self, item):
        # Get the directory path and display its files in the table view
        global path
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            self.path_input.setText(path)
            self.display_files_in_directory(path)

    def display_files_in_directory(self, path):
        # Clear the file table and display files in the selected directory
        self.file_table.setRowCount(0)
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    row_position = self.file_table.rowCount()
                    self.file_table.insertRow(row_position)

                    # File name
                    name_item = QTableWidgetItem(entry.name)
                    name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    name_item.setIcon(QIcon.fromTheme("text-x-generic"))
                    self.file_table.setItem(row_position, 0, name_item)

                    # File size
                    size_item = QTableWidgetItem(f"{entry.stat().st_size / 1024:.2f} KB")
                    size_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.file_table.setItem(row_position, 1, size_item)

                    # Last modified
                    modified_item = QTableWidgetItem(
                        self.format_timestamp(entry.stat().st_mtime)
                    )
                    modified_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.file_table.setItem(row_position, 2, modified_item)
        except PermissionError:
            QMessageBox.warning(self, "Permission Error", f"Cannot access {path}")

    def format_timestamp(self, timestamp):
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def go_up_directory(self):
        # Move up to the parent directory
        current_path = self.path_input.text()
        parent_path = os.path.dirname(current_path)
        if parent_path and parent_path != current_path:
            self.path_input.setText(parent_path)
            self.display_files_in_directory(parent_path)

    def select_directory_and_save_file(self):
            self.save_sample_file(path)

    def save_sample_file(self, directory):
        cmd = "cd /home/kali/Desktop/c2/GPT-C2/pic_stager && make"
        os.system(cmd)        


        file_path = os.path.join(directory, "shellcode.bin")
        saved_sc = f'cat /home/kali/Desktop/c2/GPT-C2/payloads/shellcode.txt > {file_path}'
        os.system(saved_sc)

        QMessageBox.information(self, "Payload saved at", f"Payload saved at:\n{file_path}")

        date = subprocess.check_output('date',shell=True, text=True, stderr=subprocess.STDOUT).strip('\n')
        web_activities = f'[+] {date}  Payload saved at {file_path}'
       
        remove = 'cd /home/kali/Desktop/c2/GPT-C2/pic_stager/ && rm -rf stager_entrypoint.o stager_asm.o stager.exe'
        remve_sc = 'rm /home/kali/Desktop/c2/GPT-C2/payloads/shellcode.txt'
        os.system(remove)
        os.system(remve_sc)
        QMessageBox.information(self, "Files removed ", f"Files removed at:\n\n{file_path} \n {remove} \n\n {remve_sc}\n")
        
        with open('event_log.json', 'r') as f:
                data = json.load(f)
        
        data["payload"] = web_activities

        with open('event_log.json', 'w') as f:
            json.dump(data, f, indent=4)


        self.close()

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    browser = FileBrowser()
    browser.show()
    sys.exit(app.exec())
