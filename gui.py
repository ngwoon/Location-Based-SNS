import controller
import sys
import os
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic

from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView

login_window = uic.loadUiType("login.ui")[0]
signup_window = uic.loadUiType("signUp.ui")[0]

msgbox = uic.loadUiType("msgbox.ui")[0]

board_window = uic.loadUiType("board.ui")[0]
writeboard_window = uic.loadUiType("writeboard.ui")[0]
showboard_window = uic.loadUiType("showBoard.ui")[0]

global user_id
global nickname
global loc

class LoginWindow(QDialog, login_window):
    def __init__(self, parent=None):
        super().__init__()
        self.id = "None"
        self.pw = "None"
        self.setupUi(self)
        self.show()
        self.confirm.clicked.connect(self.confirmClicked)
        self.signUpCheckbox.stateChanged.connect(self.signUpClicked)
        self.signOutCheckbox.stateChanged.connect(self.signOutClicked)

    def confirmClicked(self):
        self.id = self.idLabel.text()
        self.pw = self.pwLabel.text()
        self.idLabel.clear()
        self.pwLabel.clear()

        self.result = controller.search(self.id, self.pw)

        if self.result['result'] == "success":
            self.loginSuccess = Msgbox()
            self.loginSuccess.label.setText("환영합니다. " + self.id + "님")
            self.loginSuccess.exec_()

            global user_id
            global nickname
            user_id = self.result['user_id']
            nickname = self.result['nickname']
            self.hide()

            self.mainWindow = MainDisplay()

        else:
            self.loginFail = Msgbox()
            self.loginFail.label.setText("로그인 실패")
            self.loginFail.exec_()

    def signUpClicked(self):
        self.hide()
        self.signup = SignUpWindow()

    def signOutClicked(self):
        self.hide()
        #self.signout = SignOutWindow()


class SignUpWindow(QWidget, signup_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 중복검사 체크하는 변수
        self.idChecked = False
        self.nickChecked = False

        self.idCheckButton.clicked.connect(self.idBtnClicked)
        self.nickCheckButton.clicked.connect(self.nickBtnClicked)
        self.signUpButton.clicked.connect(self.signUpBtnClicked)
        self.show()

    def idBtnClicked(self):
        if controller.checkDuplication(self.idLineEdit.text(), 0):
            self.idChecked = True
            if self.idChecked and self.nickChecked:
                self.signUpButton.setEnabled(True)

            self.nodup = Msgbox()
            self.nodup.setWindowTitle("Success")
            self.nodup.label.setText("사용 가능한 ID입니다!")
            self.nodup.exec_()
        else:
            self.idChecked = False
            self.signUpButton.setEnabled(False)

            self.dup = Msgbox()
            self.dup.setWindowTitle("Fail")
            self.dup.label.setText("이미 사용 중인 ID입니다")
            self.dup.exec_()

    def nickBtnClicked(self):
        if controller.checkDuplication(self.nickLineEdit.text(), 1):
            self.nickChecked = True
            if self.idChecked and self.nickChecked:
                self.signUpButton.setEnabled(True)

            self.nodup = Msgbox()
            self.nodup.setWindowTitle("Success")
            self.nodup.label.setText("사용 가능한 닉네임입니다!")
            self.nodup.exec_()
        else:
            self.nickChecked = False
            self.signUpButton.setEnabled(False)

            self.dup = Msgbox()
            self.dup.setWindowTitle("Fail")
            self.dup.label.setText("이미 사용 중인 닉네임입니다")
            self.dup.exec_()

    def signUpBtnClicked(self):
        self.result = controller.checkUserInfo(self.idLineEdit.text(), self.pwLineEdit.text(), self.emailLineEdit.text(), self.phoneLineEdit.text())
        self.infoMsgbox = Msgbox()
        if self.result[0] == False:
            self.infoMsgbox.setWindowTitle("Fail")
            if self.result[1] == -1:
                self.infoMsgbox.label.setText("아이디가 너무 길거나 짧습니다")
            elif self.result[1] == -2:
                self.infoMsgbox.label.setText("비밀번호가 너무 길거나 짧습니다")
            elif self.result[1] == -3:
                self.infoMsgbox.label.setText("비밀번호는 영문과 숫자를 혼용해 주세요")
            elif self.result[1] == -4:
                self.infoMsgbox.label.setText("잘못된 이메일 형식")
            elif self.result[1] == -5:
                self.infoMsgbox.label.setText("잘못된 전화번호 길이")
            else:
                self.infoMsgbox.label.setText("잘못된 전화번호 형식")

            self.infoMsgbox.exec_()

        else:
            self.infoMsgbox.setWindowTitle("Success")
            self.infoMsgbox.label.setText("회원가입 성공")
            controller.signUp(self.idLineEdit.text(), self.pwLineEdit.text(), self.nickLineEdit.text(), self.nameLineEdit.text(), self.emailLineEdit.text(), self.phoneLineEdit.text())

            self.hide()
            self.login = LoginWindow()
            #self.login.exec_()


class MainDisplay(QMainWindow, QObject, board_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.showlist.clicked.connect(self.showClicked)
        self.write.clicked.connect(self.writeClicked)
        self.refresh.clicked.connect(self.refreshClicked)
        self.signals = controller.Signals()
        self.signals.map_refreshed.connect(self.load)

        #이 부분에 처음 html화면 띄우는 init 코드가 와야함
        global loc
        loc= {"latitude" : 0.0, "longitude" : 0.0}
        self.getLocThread = threading.Thread(target=controller.getLocation, args=(loc, self.signals))
        self.getLocThread.start()
        self.show()


    #폴더 내 html파일을 webEngineView에 등록하고 show
    @pyqtSlot()
    def load(self):
        self.map.load(QUrl.fromLocalFile(
            os.path.split(os.path.abspath(__file__))[0] + r'\map.html'
        ))
        self.map.show()
    def showClicked(self):
        self.showBoardWindow = showBoard()
    def writeClicked(self):
        self.writeBoardWindow = WriteBoard()
    def refreshClicked(self):
        global loc
        self.getLocThread = threading.Thread(target=controller.getLocation, args=(loc, self.signals))
        self.getLocThread.start()


class WriteBoard(QWidget, writeboard_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.locInfoCheckBox.stateChanged.connect(self.checkBoxClicked)
        self.submitButton.clicked.connect(self.submitButtonClicked)
        self.show()

    def submitButtonClicked(self):
        global user_id, nickname, loc
        
        #문제 해결 필요
        enrollthread = threading.Thread(target=controller.enrollBoard, args=(user_id, self.titleTextLabel.text(), self.contentTextLabel.toPlainText(), self.categoryComboBox.currentText(), loc['longitude'], loc['latitude'],))
        enrollthread.start()
        self.hide()

    def checkBoxClicked(self):
        if self.locInfoCheckBox.isChecked():
            self.submitButton.setEnabled(True)
        else:
            self.submitButton.setEnabled(False)

class showBoard(QWidget, showboard_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.searchButton.clicked.connect(self.searchButtonClicked)
        self.show()

    def searchButtonClicked(self):
        global loc
        self.content = self.searchTextLabel.text()
        self.category = self.categoryComboBox.currentText()
        self.distance = self.distanceComboBox.currentText()
        self.boundary = self.boundaryComboBox.currentText()

        self.searchTextLabel.clear()

        # self.searchThread = threading.Thread(target=controller.searchBoard, args=(self.content, self.category, self.distance, self.boundary, loc['latitude'], loc['longitude']))
        # self.searchThread.start()

class Msgbox(QDialog, msgbox):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.confirm.clicked.connect(self.hide)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginWindow = LoginWindow()
    app.exec_()
