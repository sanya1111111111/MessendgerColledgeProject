import pymysql
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer
import sys, re
from PyQt5.QtWidgets import QSizePolicy, QFrame, QInputDialog
class Ui(QtWidgets.QWidget):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("super.ui",self)
        self.setMinimumSize(900,600)
        self.message_dialog = QtWidgets.QMessageBox()
        self.error_dialog = QtWidgets.QErrorMessage()

        self.layerCont.setCurrentIndex(0)
        self.Reg_but.clicked.connect(self.toCreate)
        self.password_reset_button.clicked.connect(self.toReset)
        self.back_but.clicked.connect(self.toSign)
        self.name_but.clicked.connect(self.toSign)
        self.settings_button_2.clicked.connect(self.toSettings)
        self.logout_button.clicked.connect(self.toSign)
        self.settings_back.clicked.connect(self.toChat)
        self.create_button.clicked.connect(self.createUser)
        self.sign_in_button.clicked.connect(self.signdef)
        self.send_button.clicked.connect(self.sendMessage)
        self.newmessage_Button_2.clicked.connect(self.addFile)
        self.add_contact_button.clicked.connect(self.addContact)
        self.exit_but.clicked.connect(self.exit)
        self.Search_Edit.textChanged.connect(self.searchContact)
        self.searchedContact = ""

        self.messageTimer = QTimer()
        self.messageTimer.timeout.connect(self.displayMessages)

        self.contactTimer = QTimer()
        self.contactTimer.timeout.connect(self.addContactsToList)

        self.fileBI = None

        self.show()
    def signdef(self):
        try:
            connection = pymysql.connect(host='sql11.freesqldatabase.com',port=3306,user='sql11672679',password='5j1cAxNMdR',database='sql11672679',cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE email = %s AND password = %s",(self.login_edit.text(),self.password_edit.text()))
                id =cursor.fetchall()
                if len(id) > 0:
                    self.login = self.login_edit.text()
                    self.password = self.password_edit.text()
                    self.id = id[0]["id"]
                    print(self.id)
                    self.toChat()
                    self.contactTimer.start(10000)
                else:
                    self.error_dialog.showMessage("Неверный логин или пароль")

        except Exception as ex:
            print("Connection refused...")
            print(ex)
            self.error_dialog.showMessage("Ошибка!")
        finally:
            connection.close()

    def exit(self):
        exit()

    def searchContact(self):
        self.searchedContact = self.Search_Edit.text()
        print(self.searchedContact)

    def sendMessage(self):

        try:
            connection = pymysql.connect(host='sql11.freesqldatabase.com',port=3306,user='sql11672679',password='5j1cAxNMdR',database='sql11672679',cursorclass=pymysql.cursors.DictCursor)
            try:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT into message(user1, user2, text, attachedFile)  VALUES (%s, %s, %s, %s);",(self.id, self.targetContact, self.sender_textEdit_2.toPlainText(),self.fileBI))
                    self.fileBI = None
                    print("Message created")
                    connection.commit()
            finally:
                connection.close()
        except Exception as ex:
            print("Connection refused...")
            print(ex)
            self.error_dialog.showMessage("Ошибка!")


    def addContact(self):
        contact, ok = QInputDialog.getText(window, 'Добавление контакта', 'Введите логин контакта:')
        if not ok: return
        try:
            connection = pymysql.connect(host='sql11.freesqldatabase.com',port=3306,user='sql11672679',password='5j1cAxNMdR',database='sql11672679',cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                cursor.execute("INSERT into contact(user1, user2)  VALUES (%s, (select id from users where email = %s));", (self.id, contact))
                connection.commit()
        except Exception as ex:
            print("Connection refused...")
            print(ex)
            self.error_dialog.showMessage("Ошибка!\n Проверьте правильность ввода.")
        finally:
            connection.close()

    def addContactsToList(self):
        self.clear_layout(self.Contacts_layout)
        try:
            connection = pymysql.connect(host='sql11.freesqldatabase.com',port=3306,user='sql11672679',password='5j1cAxNMdR',database='sql11672679',cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                id = []
                login = []
                if len(self.searchedContact) > 0:
                    cursor.execute("SELECT email, id FROM contact join users ON user2 = id WHERE user1 = %s and email = %s", (self.id, self.searchedContact))
                else:
                    cursor.execute("SELECT email, id FROM contact join users ON user2 = id WHERE user1 = %s", (self.id))
                for i in cursor.fetchall():
                    id.append(i["id"])
                    login.append(i["email"])
                if len(self.searchedContact) > 0:
                    cursor.execute("SELECT email, id FROM contact join users ON user1 = id WHERE user2 = %s and email = %s", (self.id, self.searchedContact))
                else:
                    cursor.execute("SELECT email, id FROM contact join users ON user1 = id WHERE user2 = %s", (self.id))
                for i in cursor.fetchall():
                    id.append(i["id"])
                    login.append(i["email"])
                print(login, id)
                layout = QtWidgets.QVBoxLayout()
                for i in range(len(id)):
                    print(i)
                    self.Contacts_layout = self.addContactToList(login[i],id[i],self.Contacts_layout)
                space = QtWidgets.QSpacerItem(40, 200, QSizePolicy.Expanding)
                self.Contacts_layout.addItem(space)
        except Exception as ex:
            print("Connection refused...")
            print(ex)
            self.error_dialog.showMessage("Ошибка!")
        finally:
            connection.close()

    def addFile(self):
        text, ok = QInputDialog.getText(window, 'Добавление файла', 'Введите путь к файлу:')
        if ok:
            try:
                with open(text, 'rb') as file:
                    self.fileBI = file.read()
            except: self.error_dialog.showMessage("Ошибка ввода файла")

    def addContactToList(self, login, id, lay):
        a = QtWidgets.QPushButton()
        a.setText(login)
        a.clicked.connect(lambda: self.switchContact(id,login))
        lay.addWidget(a,alignment= Qt.AlignTop)
        return lay
    def addMessageToList(self,mes):
        a = QtWidgets.QLabel()
        a.setText(mes['text'])
        a.setWordWrap(True)
        a.setFrameShape(QFrame.Panel)
        b = QtWidgets.QHBoxLayout()
        if mes['user1'] == self.id:
            b.addItem(QtWidgets.QSpacerItem(200, 10, QSizePolicy.Expanding))
            a.setStyleSheet('background-color:#008B8B;')
            if mes['attachedFile']:
                c = QtWidgets.QPushButton()
                c.setText("Получить файл")
                c.clicked.connect(lambda: self.recordFile(mes['attachedFile']))
                b.addWidget(c)
            b.addWidget(a)
        else:
            b.addWidget(a)
            if mes['attachedFile']:
                c = QtWidgets.QPushButton()
                c.setText("Получить файл")
                c.clicked.connect(lambda: self.recordFile(mes['attachedFile']))
                b.addWidget(c)
            b.addItem(QtWidgets.QSpacerItem(8000, 10, QSizePolicy.Expanding))
        return b
    def recordFile(self, file1):
        text, ok = QInputDialog.getText(window, 'Получение файла', 'Введите путь к файлу в который будет записан полученный файл:')
        if ok:
            try:
                with open(text, 'wb') as file:
                    file.write(file1)
            except Exception as e:
                self.error_dialog.showMessage("Ошибка ввода файла"+str(e))
    def switchContact(self,id,login):
        if self.messageTimer.isActive():
            self.messageTimer.stop()
        self.targetContact = id
        self.chatNameLabel_2.setText(login)
        self.messageTimer.start(10000)
        self.displayMessages()
    def clear_layout(self,layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            sublayout = item.layout()
            if widget:
                layout.removeWidget(widget)
                widget.deleteLater()
            elif sublayout:
                self.clear_layout(sublayout)
    def displayMessages(self):
        self.clear_layout(self.Messages_layout)
        try:
            connection = pymysql.connect(host='sql11.freesqldatabase.com',port=3306,user='sql11672679',password='5j1cAxNMdR',database='sql11672679',cursorclass=pymysql.cursors.DictCursor)
            print("successfully connected...")
            print("#" * 20)

            try:
                with connection.cursor() as cursor:
                    SentMessages = []
                    ReceivedMessages = []
                    cursor.execute("SELECT id, text, user1, attachedFile FROM message WHERE user1 = %s and user2 = %s", (self.id, self.targetContact))
                    for i in cursor.fetchall():
                        SentMessages.append(i)
                    cursor.execute("SELECT id, text, user1, attachedFile FROM message WHERE user1 = %s and user2 = %s", (self.targetContact, self.id))
                    for i in cursor.fetchall():
                        ReceivedMessages.append(i)
                    Messages = SentMessages + ReceivedMessages
                    Messages = sorted(Messages, key=lambda x: x['id'])
                    #print(Messages)
                    for i in Messages:

                        self.Messages_layout.addLayout(self.addMessageToList(i))
                    space = QtWidgets.QSpacerItem(40, 10000, QSizePolicy.Expanding)
                    self.Messages_layout.addItem(space)
                    #self.messageArea_2.setLayout(layout)

            finally:
                connection.close()
        except Exception as ex:
            print("Connection refused...")
            print(ex)
            self.error_dialog.showMessage("Ошибка!")
    def createUser(self):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not (re.fullmatch(regex, self.login_edit1.text())):
            self.error_dialog.showMessage("Email введён некорректно")
            return
        if(len(self.password_edit1.text())< 8):
            self.error_dialog.showMessage("Пароль ввёдён некорректно. \n Минимальная длина пароля: 8 символов.")
            return
        try:
            connection = pymysql.connect(host='sql11.freesqldatabase.com',port=3306,user='sql11672679',password='5j1cAxNMdR',database='sql11672679',cursorclass=pymysql.cursors.DictCursor)
            print("successfully connected...")
            print("#" * 20)
            try:
                with connection.cursor() as cursor:
                    cursor.execute("INSERT into users(password, email)  VALUES ('{0}', '{1}');".format(self.password_edit1.text(),self.login_edit1.text() ))
                    print("user {0} inserted".format(self.login_edit1.text()))
                    connection.commit()
                    self.error_dialog.showMessage("Пользователь добавлен")
            finally:
                connection.close()
        except Exception as ex:
            print("Connection refused...")
            print(ex)
            self.error_dialog.showMessage("Ошибка!")
    def toCreate(self):
        self.layerCont.setCurrentIndex(1)
    def toReset(self):
        self.layerCont.setCurrentIndex(2)
    def toSign(self):
        self.contactTimer.stop()
        self.layerCont.setCurrentIndex(0)
    def toChat(self):
        self.addContactsToList()
        self.layerCont.setCurrentIndex(3)
    def toSettings(self):
        self.layerCont.setCurrentIndex(4)
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()