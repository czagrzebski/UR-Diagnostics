"""
A simple PyQT5 tool for Universal Robot Dashboard Server

Author: Creed Zagrzebski (czagrzebski@gmail.com)
"""
import sys
import socket
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QTextBrowser, QPushButton, QMessageBox, QLabel
from PyQt5 import uic, QtCore
import threading
import time


class URDiagnosticsUI(QMainWindow):
    heartbeat_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super(URDiagnosticsUI, self).__init__()
        uic.loadUi("ui/main.ui", self)
        self.setWindowTitle("UR Diagnostics")
       
        self.__init_socket()

        # bind button events
        self.connectBtn = self.findChild(QPushButton, 'connectBtn')
        self.connectBtn.clicked.connect(self.__connect)
        self.disconnectBtn = self.findChild(QPushButton, 'disconnectBtn')
        self.disconnectBtn.clicked.connect(self.__disconnect)
        self.sendBtn = self.findChild(QPushButton, 'sendBtn')
        self.sendBtn.clicked.connect(self.__send_command)
        
        self.connectionLabel = self.findChild(QLabel, "connectionStatus")
        self.heartbeat_signal.connect(self.connectionLabel.setText)
        
        # TODO: Setup heartbeat to detect connection loss
        # set heartbeat timer 
        # heartbeat_thread = threading.Thread(target=self.__heartbeat)
        # heartbeat_thread.start()

        self.setFixedSize(770, 550)
        self.show()
    

    def __display_error(self, message):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()
        
    def __init_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3000)
        
    def __connect(self):
        # grab address/port from UI input
        ipPort = self.findChild(
            QTextEdit, 'addrTextEdit').toPlainText().split(":")
        
        self.__init_socket()
        try:
            self.sock.connect((ipPort[0], int(ipPort[1])))
            self.__append_message(self.sock.recv(1024).decode())
            self.connectionLabel.setText("Connected")
        except ConnectionError:
            self.__display_error("Connection Refused")

    def __disconnect(self):
        try:
            self.sock.close()
            self.__append_message("Disconnected: Universal Robots Dashboard Server")
            self.connectionLabel.setText("Disconnected")
        except ConnectionError:
            self.__display_error("Connection Refused")

    def __send_command(self):
        input_box = self.findChild(QTextEdit, 'inputTextEdit')
        command = input_box.toPlainText()
        command += "\n"
        input_box.clear()
        try:
            self.sock.send(command.encode())
            data = self.sock.recv(1024)
            self.__append_message(data.decode())
        except ConnectionError:
            self.__display_error("Not connected to server")

    def __heartbeat(self):
        while True:     
            print("Checking heartbeat")
            time.sleep(5000)
            try:
                self.sock.send("version".encode())
                data = self.sock.recv(1024)
                self.__append_message(data.decode())
                self.heartbeat_signal.emit("Connected")
            except ConnectionError:
                self.heartbeat_signal.emit("Disconnected")
     
    
    def __append_message(self, message):
        input_box = self.findChild(QTextBrowser, 'outputConsole')
        input_box.append(f'<span><b>{datetime.now()}</b>: {message}</span>')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = URDiagnosticsUI()
    app.exec_()
