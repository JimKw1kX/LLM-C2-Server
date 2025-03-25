from PyQt6 import QtCore, QtWidgets
import subprocess, os
from PyQt6.QtWidgets import QCompleter, QLineEdit
import html
from PyQt6 import QtCore, QtGui, QtWidgets
from output import *
import argparse
import socket
import shared
# from c2front5 import Ui_MainWindow
# ui = Ui_MainWindow.ListenerTab

"""
TS is here

"""


class badger_session(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

             
    def setupUi(self, Form):
        
        self.command_history = []
        self.history_index = -1
        
        Form.setObjectName("Form")
        Form.resize(1600, 900)

        self.commandSignal = QtCore.pyqtSignal(str) # commnad signal from c2fron5

        # Main vertical layout for the form
        self.mainLayout = QtWidgets.QVBoxLayout(Form)
        self.mainLayout.setObjectName("mainLayout")

        # GroupBox containing the entire content (dynamically stretching)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")

        # Layout inside the main groupBox
        self.groupBoxLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.groupBoxLayout.setObjectName("cmd")

        # Top header
        self.headerLine = QtWidgets.QLabel(self.groupBox)
        self.headerLine.setText("x64 | 1364@x-0 | Desktop-11111")
        self.headerLine.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.headerLine.setObjectName("headerLine")
        self.groupBoxLayout.addWidget(self.headerLine)

        # Row 1 - C2 commands and "X" button
        self.row1Layout = QtWidgets.QHBoxLayout()
        self.commandLabel = QtWidgets.QLabel(self.groupBox)
        self.commandLabel.setText("Command     $")
        self.commandLabel.setObjectName("commandLabel")
        self.row1Layout.addWidget(self.commandLabel)
        self.commandLabel.setStyleSheet("color:#00ff00;")

        self.commandLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.commandLineEdit.setPlaceholderText("Enter your command here")
        self.commandLineEdit.setObjectName("commandLineEdit")
        self.row1Layout.addWidget(self.commandLineEdit)


        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setText("X")
        self.pushButton.setObjectName("Close_Tab")
        # self.pushButton.clicked.connect(lambda: c2front5.Ui_MainWindow.close_tab(c2front5.Ui_MainWindo))
        self.row1Layout.addWidget(self.pushButton)
        self.groupBoxLayout.addLayout(self.row1Layout)


        # Row 2 - Sentinel $ and dropdown
        self.row2Layout = QtWidgets.QHBoxLayout()
        self.sentinelLabel = QtWidgets.QLabel(self.groupBox)
        self.sentinelLabel.setText("LLM Prompt $")
        self.sentinelLabel.setObjectName("sentinelLabel")
        self.row2Layout.addWidget(self.sentinelLabel)
        self.sentinelLabel.setStyleSheet("color:#00ff00;")


        self.sentinelLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.sentinelLineEdit.setPlaceholderText("Enter your GPT Prompts")
        self.sentinelLineEdit.setObjectName("sentinelLineEdit")
        self.row2Layout.addWidget(self.sentinelLineEdit)
        
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.addItem("Domain $")
        self.comboBox.setObjectName("comboBox")
        self.row2Layout.addWidget(self.comboBox)


        self.groupBoxLayout.addLayout(self.row2Layout)

        # Spacer to allow the remaining content to stretch
        self.groupBoxLayout.addStretch()

        self.outputContainer = QtWidgets.QWidget(self.groupBox)

        # Set the background image on the container
        self.outputContainer.setStyleSheet("""
                                           
        QTextEdit {
        selection-background-color:  #8B0000;  /* Change highlight color to red */
        }
        
        QMainWindow {
                    background-color: rgb(20, 20, 20);
                    color: #ffffff;
                }

        QWidget {
              background-color: rgb(20, 20, 20);  /* Dark background color */
            selection-background-color:  #8B0000;  /* Change highlight color to red */
                                           
        color: white;  /* Text color */
        border: 2px solid gray;
        border-radius: 5px;
        margin-top: 20px;
        padding: 10px;
        font-weight: bold;
        selection-background-color:  #8B0000;
        background-image: url('n6.png');  /* Path to the edited image */
        background-position: center;  /* Center the image */
        background-repeat: no-repeat;  /* Do not repeat the image */
        background-origin: border;
        opacity: 0.8; 
        }

        #                                       QWidget::title {
        # subcontrol-origin: margin;
        # subcontrol-position: top center; /* Title alignment */
        # padding: 5px;
        """)
        
             #  Output text box for displaying command output
        self.outputTextBox = QtWidgets.QTextEdit(self.outputContainer)
        self.outputTextBox.setReadOnly(True)  # Make it read-only
        self.outputTextBox.setStyleSheet("background: transparent;") 
        self.outputTextBox.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        # self.outputTextBox.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        # self.outputTextBox.verticalScrollBar().setValue(self.outputTextBox.verticalScrollBar().maximum())
        scroll_bar = self.outputTextBox.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())
        self.outputTextBox.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.outputTextBox.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)


        self.outputContainerLayout = QtWidgets.QVBoxLayout(self.outputContainer)
        self.outputContainerLayout.addWidget(self.outputTextBox)
        # self.outputContainerLayout.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        # self.outputContainerLayout.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        self.prebuilt_commands = {
            'help': 'echo "Available commands: help, date, who, ifconfig, ps, clear, sysinfo"',
            'date': 'date;timedatectl',
            'who': 'who',
            'ifconfig': 'ifconfig',
            'ps': 'COLUMNS=2000 ps aef --forest',
            'clear': 'clear',
            'sysinfo': 'cat /etc/os-release;uname -r;nvidia-smi;lscpu',
            'compiler' : 'nasm -v; g++ --version;gcc --version',                   # NASM Version
            'llm':['python3', '-u','output.py']             # NASM Version
        }

        self.completer = QCompleter(self.prebuilt_commands)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.CompletionMode.InlineCompletion)
        
        self.commandLineEdit.setCompleter(self.completer)
        self.sentinelLineEdit.setCompleter(self.completer)
        self.commandLineEdit.installEventFilter(self)
        self.commandLineEdit.returnPressed.connect(lambda: self.execute_cmd()) # important , using lambda to make each returnPressed unique when creating a new tab so command will not only work on the most recent tab
        self.sentinelLineEdit.returnPressed.connect(lambda: self.execute_cmd()) # Use Lambda or functools.partial: By using lambda or partial, you can pass the unique QLineEdit instance to the execute_cmd function for each tab. This way, when returnPressed is triggered, the correct QLineEdit will be passed, ensuring no overwriting.

        self.groupBoxLayout.addWidget(self.outputContainer,stretch=1)
        self.mainLayout.addWidget(self.groupBox)
        self.mainLayout.setStretch(0, 1)
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    class commandworker(QtCore.QObject):
        outputReady = QtCore.pyqtSignal(str)
        finished = QtCore.pyqtSignal()
    
        def __init__(self, command):
            super().__init__()
            self.command = shared.command
            self._is_running = True

        def run(self):
            print(f'recived command {self.command}')

            result = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) 
            output_buffer = ""
            word_count = 0
            word_per_line = 80

            while True:
                output = result.stdout.read(1)
                if output == '' and result.poll() is not None:
                    break

                if output:
                      output_buffer += output
                      if output == ' ':
                        escape_output = html.escape(output_buffer.strip())
                        self.outputReady.emit(escape_output + ' ')
                        output_buffer = ""
                        # word_count +=1

                        if word_count >= word_per_line:
                            self.outputReady.emit('\n')
                            # word_count = 0

            self.finished.emit()
        
        def stop(self):
            self._is_running = False
    
    def execute_cmd(self):
        Buf = 2024
           

        
        
        # cmd = command.recv(Buf).decode()
        # Get the text from commandLineEdit
        self.command_text = self.commandLineEdit.text().lower().strip()
        sentinelcommand = self.sentinelLineEdit.text().lower().strip()
        
        if self.command_text: #need to put   self.command_history.append(self.command_text) and  self.history_index = len(self.command_history) to store the full command with args
            print(f"Command received: {self.command_text}")
            shared.command.send(self.command_text.encode())

            self.command_history.append(self.command_text)
            self.history_index = len(self.command_history)
            print(f'self.command_history has: {self.command_history}')
        
        elif sentinelcommand:
            print(f"Sentinel received: {sentinelcommand}")
            self.command_history.append(sentinelcommand)
            self.history_index = len(self.command_history)
            print(f'self.command_history has: {self.command_history}')
            shared.command.send(sentinelcommand.encode())

        
        
        self.outputTextBox.setTextColor(QtCore.Qt.GlobalColor.green)
        date = subprocess.run('date', stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

        parts = self.command_text.split()
        self.command_text = parts[0] if parts else '' #parts[0] == 'python3', '-u', 'output.py' defined in the lists the throw remaining arguments after 
        args = parts[1:]

        if self.command_text in self.prebuilt_commands:  # Check if there is a text input
            self.command_text_execute = self.prebuilt_commands[self.command_text]
            prebuid_cmd = str(self.command_text_execute)
            if shared.command is not None:
                shared.command.send(prebuid_cmd.encode())

            try:
                if self.command_text == 'llm':
                  
                    if len(args) != 2 or not all(arg.isdigit() for arg in args):
                        self.outputTextBox.append(f"<b style='color:#00ff00;font-weight:bold;'> {date.stdout} [input] Jim => {self.command_text}</b><br>")
                        self.outputTextBox.append(f"<b style='color:red;font-weight:bold;'> Usage: llm [num loops] [num tokens]</b><br>")
                        self.outputTextBox.append(f"<b style='color:red;font-weight:bold;'>        E.g: llm 2 100</b>")
                        scroll_bar = self.outputTextBox.verticalScrollBar()
                        scroll_bar.setValue(scroll_bar.maximum())
                   
                        return
                    
                    self.command_text_execute = self.prebuilt_commands[self.command_text] + args 
                    self.outputTextBox.append(f"<b style='color:#00ff00;font-weight:bold;'> {date.stdout} [input] Jim => {self.command_text}</b><br>")
                    self.outputTextBox.append(f"<b style='color:#00ff00;font-weight:bold;'> {self.command_text_execute} is running......</b>")
                    self.outputTextBox.append("<br>+---------------------------------------------------------------------------------------------------+<br>")  # Add a separator
                    
                    self.thread = QtCore.QThread()
                    self.worker = self.commandworker(self.command_text_execute)
                    self.worker.moveToThread(self.thread)

                    self.worker.outputReady.connect(self.run_command_live_output)
                    self.thread.started.connect(self.worker.run)
                    self.thread.finished.connect(self.on_thread_finished)

                    self.worker.finished.connect(self.thread.quit)
                    self.worker.finished.connect(self.worker.deleteLater)
                    self.thread.finished.connect(self.thread.deleteLater)
                    
                    self.thread.start()

                    scroll_bar = self.outputTextBox.verticalScrollBar()
                    scroll_bar.setValue(scroll_bar.maximum())
                   

                else :
                    result = shared.command.recv(Buf).decode()   
                    # result = subprocess.run(self.command_text_execute,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                    # command_output = result.stdout if result.stdout else result.stderr
                    command_output = html.escape(result)

                    self.outputTextBox.append(f"<b style='color:#00ff00;font-weight:bold;'> {date.stdout} [input] Jim => {self.command_text}</b>")
                    self.outputTextBox.append("<br>+---------------------------------------------------------------------------------------------------+<br>")  # Add a separator
                    self.outputTextBox.append(f"<pre style='color: white; font-weight:bold;'>{command_output}</pre>")
                    self.outputTextBox.append("<br>+---------------------------------------------------------------------------------------------------+")  # Add a separator
                    # self.outputTextBox.append(current_output  + new_output) # remove this else when you on top the scoll bar wont goto the bottom
                    scroll_bar = self.outputTextBox.verticalScrollBar()
                    scroll_bar.setValue(scroll_bar.maximum())
                    
            except Exception as e:
                # print(f"Error executing command: {e}")
                self.outputTextBox.append(f"<pre style='color: red;'>Error: {str(e)}</pre>")
                
            self.commandLineEdit.clear()

        elif sentinelcommand in self.prebuilt_commands:  # Check if there is a text input
                sentinelcommand_excute = self.prebuilt_commands[sentinelcommand]
                try:
                    # Run the command
                    result = subprocess.run(sentinelcommand_excute, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    date = subprocess.run('date', shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
                    # Prepare the output
                    command_output = result.stdout if result.stdout else result.stderr

                    self.outputTextBox.append(f"<b style='color:#00ff00;font-weight:bold;'> {date.stdout} [input] Jim => {sentinelcommand}</b>")
                    self.outputTextBox.append("<br>+---------------------------------------------------------------------------------------------------+<br>")  # Add a separator
                    self.outputTextBox.append(f"<pre style='color: white;font-weight:bold;'>{command_output}</pre>")
                    self.outputTextBox.append("<br>+---------------------------------------------------------------------------------------------------+")  # Add a separato
                    scroll_bar = self.outputTextBox.verticalScrollBar()
                    scroll_bar.setValue(scroll_bar.maximum())
                    # self.outputTextBox.verticalScrollBar().setValue(self.outputTextBox.verticalScrollBar().maximum())
                except Exception as e:
                    print(f"Error executing command: {e}")

                self.sentinelLineEdit.clear()



    def on_thread_finished(self):
        if self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
        self.outputTextBox.append("<br>+---------------------------------------------------------------------------------------------------+")  # Add a separator
        self.outputTextBox.append(f"<b style='color:red;font-weight:bold;'> {self.command_text_execute} has finished.....<br>")


    def run_command_live_output(self,text):
        if text == '\n':
            self.outputTextBox.append('')
        else:
            self.outputTextBox.moveCursor(QtGui.QTextCursor.MoveOperation.End)
            self.outputTextBox.insertPlainText(f"{text} ")
            # self.outputTextBox.insertPlainText(f"<pre style='color: white;font-weight:bold;'>{text}</pre>")
    
        scroll_bar = self.outputTextBox.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())


    def eventFilter(self, source, event):
        if source == self.commandLineEdit:
            if event.type() == QtCore.QEvent.Type.KeyPress:
                key = event.key()

                if key == QtCore.Qt.Key.Key_Up:
                    self.show_previous_cmd()
                    return True
                elif key == QtCore.Qt.Key.Key_Down:
                    self.show_next_cmd()
                    return True
                
        return super().eventFilter(source, event)


    def show_previous_cmd(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.commandLineEdit.setText(self.command_history[self.history_index])
        elif self.history_index == 0:
            self.commandLineEdit.setText(self.command_history[0])
    
    def show_next_cmd(self):
        if self.history_index < len(self.command_history) -1:
            self.history_index +=1
            self.commandLineEdit.setText(self.command_history[self.history_index])
        else:
            self.commandLineEdit.clear()
            self.history_index = len(self.command_history)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

    
    # def handle_sockedt(self):
    #     global command
    #     global addr 
        
    #     command, addr = self.server_socket.accept()
    #     return addr
        
    # def print_event(self , cmd):
    #         from c2 import Ui_MainWindow
    #         self.ui = Ui_MainWindow()
    #         self.ui.setupUi(self)
                
    #         try:
    #             # listener_tab = Ui_MainWindow.ListenerTab()
    #             # result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
    #             # Append each result to the event log
    #             self.ui.event_log_widget.append(f"<b style='color:#00ff00;'>Command : </b> {cmd}<br><pre style='color: #00ff00;'></pre><br>")
    #             self.ui.web_activity_widget.append(f"<b style='color:#00ff00;'>Command : </b> {cmd}<br><pre style='color: #00ff00;'></pre><br>")
    #         except subprocess.CalledProcessError as e:
    #             # If command fails, print the error message
    #             self.ui.web_activity_widget.append(f"Command: {cmd}\nError: {e.output}\n")


    # def ts(self):
    #     from c2front5 import Ui_MainWindow
    #     import json
    #     ui = Ui_MainWindow()
    #     from c2 import MainWindow

    #     evnet= MainWindow()
        

    #     commands = [
    #                 """cat /etc/os-release | grep '^PRETTY_NAME=' | awk -F '"' '{print $2}'""",       # OS Version
    #                 "date",                      # System Date & Time
    #                 "ifconfig ens33 | grep 'inet ' | awk '{print $2}'",
    #                 "uname -i"
    #         ]

    #     ip = subprocess.run(commands[2],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #     ip  = str(ip.stdout.strip())
    #     # print(ip)
    #     date = subprocess.check_output(commands[1],shell=True, text=True, stderr=subprocess.STDOUT).strip('\n')

    #     port = 8080
        
    #     self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #     # global info1
        
    #     self.server_socket.bind((ip, port))
    #     self.server_socket.listen(1)
    #     global command
    #     command, addr = self.server_socket.accept()
        
    #     # global info
    #     # addr = self.handle_sockedt(self)

    #     self.info1= f' {date} [!] Received connection from LLM-agent {addr}'
    #     self.info = f' {date} [+] Started Listening {ip}:{addr}'

        
        
    #     print(self.info1)
    #     print(self.info)

    #     evnet.print_event(self.info1)
    #     evnet.print_event(self.info)

        

    #     with open('event_log.json', 'w') as f:

    #         josn_data = json.dumps({
    #             "info1": self.info1,
    #             "info": self.info,
                
    #         },indent=4)

    #         f.write(josn_data)


        
    
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = badger_session()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())