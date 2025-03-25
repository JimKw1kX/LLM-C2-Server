#!/usr/bin/python3

import subprocess
from PyQt6.QtWidgets import QApplication
import sys,socket,json
import threading
import shared
# from c2front5 import Ui_MainWindow
commands = [
                    """cat /etc/os-release | grep '^PRETTY_NAME=' | awk -F '"' '{print $2}'""",       # OS Version
                    "date",                      # System Date & Time
                    "ifconfig ens33 | grep 'inet ' | awk '{print $2}'",
                    "uname -i"
            ]



ip = subprocess.run(commands[2],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
ip  = str(ip.stdout.strip())

port = 8080
Buf = 2024




class TS():

        def __init__(self):
                self.server_socket = None

        def handle_socket(self):
                # global self.command
                self.address = None              
                while True:
                        try:
                             shared.command, self.addr = self.server_socket.accept()
                             print(f"[!] Received connection from {self.addr}")
                             self.address = self.addr
                             info1= f'[!] {self.date}  Received LLM-agent.exe connection from {self.address} '
                             info = f'[+] {self.date}  Started Listening {ip}:{self.port}'

                             print(info1)
                             print(info)

                             with open('event_log.json', 'w') as f:

                                josn_data = json.dumps({
                                        "info1": info1,
                                        "info": info,
                                        
                                },indent=4)

                                f.write(josn_data)
                
                
                
                        except Exception as e:
                                print(e)
                                

         



        def ts(self):
                # from c2front5 import Ui_MainWindow
                # import json
                # ui = Ui_MainWindow()
                # from c2 import MainWindow

                

                commands = [
                        """cat /etc/os-release | grep '^PRETTY_NAME=' | awk -F '"' '{print $2}'""",       # OS Version
                        "date",                      # System Date & Time
                        "ifconfig ens33 | grep 'inet ' | awk '{print $2}'",
                        "uname -i"
                ]

                ip = subprocess.run(commands[2],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                ip  = str(ip.stdout.strip())
                # print(ip)
                self.date = subprocess.check_output(commands[1],shell=True, text=True, stderr=subprocess.STDOUT).strip('\n')

                self.port = 8080
                
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # global info1
                
       
                self.server_socket.bind((ip, port))
                self.server_socket.listen(1)

                print(f'listening {ip}:{port} for incoming traffics.......')
              
                # global info
                # addr = self.handle_sockedt(self)

                ts = threading.Thread(target=self.handle_socket)
                ts.daemon = True
                ts.start()
               

# if __name__ == '__main__':
#       ts = TS()
#       ts.ts()