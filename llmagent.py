#!/usr/bin/python3
import subprocess
from PyQt6.QtWidgets import QApplication
from c2front5 import Ui_MainWindow, badgerterminal
import sys
# class MainWindow(QtWidgets.QMainWindow):

#     def __init__(self):
#         super().__init__()
commands = [
                    """cat /etc/os-release | grep '^PRETTY_NAME=' | awk -F '"' '{print $2}'""",       # OS Version
                    "date",                      # System Date & Time
                    "ifconfig ens33 | grep 'inet ' | awk '{print $2}'",
                    "uname -i"
            ]


os = subprocess.run(commands[0],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
date = subprocess.run(commands[1],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
ip = subprocess.run(commands[2],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
Arc = subprocess.run(commands[3],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

elements = ["127.0.0.1", ip.stdout.strip(), "x-0", os.stdout.strip(), "LLM" , date.stdout.strip() , "1364" , "9068" , "C:\\Windows\\system32\\LLM-Agent.exe", Arc.stdout.strip(), Arc.stdout.strip() , "Direct", "NULL"]
# print('elements\n')


app = QApplication(sys.argv)
main_window = Ui_MainWindow()



def update_badger_terminal(elements):
    badger_terminal_instance = badgerterminal()

    badger_terminal_instance.add_bagders(elements)
    # print(f'added badger tab: \n{elements}')
    # print(f'badger dict: \n {badger_terminal_instance.badger_dict}')
    # print(f'badger num: \n {badger_terminal_instance.badger_num}')
    # sys.exit(app.exec())

for i in range(1):
    update_badger_terminal(elements)
