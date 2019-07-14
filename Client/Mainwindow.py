import sys
import traceback
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPalette, QPixmap, QBrush
from PyQt5.QtWidgets import QLineEdit
from Denglu import Ui_MainWindow
import Zhuce
import Recommend
import Dialog
import Admin
import Bookadd
import pymysql
import socket


# 错误提示对话框
class DialogWindow(QtWidgets.QMainWindow, Dialog.Ui_Dialog):
    def __init__(self, parent=None):
        super(DialogWindow, self).__init__(parent)
        self.setupUi(self)


# 登录窗口
class FirstWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    adminuser = "root"
    adminpassword = "123456"

    def __init__(self, parent=None):
        super(FirstWindow, self).__init__(parent)
        self.setupUi(self)
        self.lineEdit_2.setEchoMode(QLineEdit.Password)

    def get_information(self):
        str_user = self.lineEdit_1.text()
        str_password = self.lineEdit_2.text()
        return str_user, str_password


# 注册窗口
class SecondWindow(QtWidgets.QMainWindow, Zhuce.Ui_MainWindow):
    def __init__(self, parent=None):
        super(SecondWindow, self).__init__(parent)
        self.setupUi(self)

    def get_reginformation(self):
        name = self.lineEdit.text()
        location = self.lineEdit_3.text()
        age = self.lineEdit_4.text()
        password = self.lineEdit_2.text()
        return name, location, age, password

    def register(self):
        URL = "106.14.11.86"
        User = "admin1"
        Password = "123456"
        Database = "bookcrossing"
        name, location, age, password = self.get_reginformation()
        db = pymysql.connect(URL, User, Password, Database, charset='utf8')
        cursor = db.cursor()
        sql = "insert into `BX-Users` values('%s', '%s', '%d', '%s')" % (name, location, int(age), password)
        try:
            cursor.execute(sql)
        except Exception:
            traceback.print_exc()
        finally:
            db.close()


# 管理员添加图书窗口
class BookaddWindow(QtWidgets.QMainWindow, Bookadd.Ui_MainWindow):
    def __init__(self, parent=None):
        super(BookaddWindow, self).__init__(parent)
        self.setupUi(self)

    def add(self):
        global dialogwindow
        URL = "106.14.11.86"
        User = "admin1"
        Password = "123456"
        Database = "bookcrossing"
        db = pymysql.connect(URL, User, Password, Database, charset='utf8')
        cursor = db.cursor()
        isbn = self.lineEdit.text()
        title = self.lineEdit_2.text()
        author = self.lineEdit_3.text()
        publication = self.lineEdit_4.text()
        publisher = self.lineEdit_5.text()
        sql = "insert into `BX-Books` values('%s', '%s', '%s', '%s', '%s')" % (isbn, title, author, publication, publisher)
        try:
            cursor.execute(sql)
            dialogwindow.label.setText("成功")
            dialogwindow.show()
        except Exception:
            traceback.print_exc()
            dialogwindow.label.setText("失败")
            dialogwindow.show()
        finally:
            db.close()


# 管理员窗口
class AdminWindow(QtWidgets.QMainWindow, Admin.Ui_MainWindow):
    def __init__(self, parent=None):
        super(AdminWindow, self).__init__(parent)
        self.setupUi(self)

    def action(self):
        global dialogwindow, bookaddwindow
        URL = "106.14.11.86"
        User = "admin1"
        Password = "123456"
        Database = "bookcrossing"
        db = pymysql.connect(URL, User, Password, Database, charset='utf8')
        cursor = db.cursor()
        user = self.lineEdit_1.text()
        book = self.lineEdit_2.text()
        try:
            # 删除图书
            if self.sender() == self.pushButton:
                sql = "delete from `BX-Book-Ratings` where `ISBN` = '%s'" % book
                cursor.execute(sql)
                sql = "delete from `BX-Books` where `ISBN` = '%s'" % book
                cursor.execute(sql)
                dialogwindow.label.setText("成功")
                dialogwindow.show()
            # 添加图书
            if self.sender() == self.pushButton_2:
                bookaddwindow.show()
                self.close()
            # 删除用户
            if self.sender() == self.pushButton_3:
                sql = "delete from `BX-Book-Ratings` where `User-ID` = '%s'" % user
                cursor.execute(sql)
                sql = "delete from `BX-Users` where `User-ID` = '%s'" % user
                cursor.execute(sql)
                dialogwindow.label.setText("成功")
            # 查询用户书籍评分
            if self.sender() == self.pushButton_4:
                sql = "select `Book-Rating` from `BX-Book-Ratings` where `User-ID` = '%s' and `ISBN` = '%s'" % (user,
                                                                                                                book)
                cursor.execute(sql)
                res = cursor.fetchall()
                ls = list(res)
                self.lineEdit_3.setText(str(ls[0][0]))
        except Exception:
            traceback.print_exc()
            dialogwindow.label.setText("失败")
        finally:
            db.close()


# 推荐窗口
class RWindow(QtWidgets.QMainWindow, Recommend.Ui_MainWindow):
    def __init__(self, parent=None):
        super(RWindow, self).__init__(parent)
        self.setupUi(self)
        # user = firstwindow.lineEdit_1.text()
        # self.recommendItem(str(user))

    def raction(self):
        global firstwindow
        URL = "106.14.11.86"
        User = "admin1"
        Password = "123456"
        Database = "bookcrossing"
        db = pymysql.connect(URL, User, Password, Database, charset='utf8')
        cursor = db.cursor()
        book = self.lineEdit_1.text()
        sql_search = "select `ISBN` from `BX-Books` where `Book-Title` = '%s'" % book
        cursor.execute(sql_search)
        bookID = list(cursor.fetchall())
        rating = self.lineEdit_2.text()
        user = firstwindow.lineEdit_1.text()
        sql = "select `Book-Rating` from `BX-Book-Ratings` where `User-ID` = '%s' and `ISBN` = '%s'" % (user, bookID[0][0])
        # 查询
        if self.sender() == self.pushButton:
            try:
                cursor.execute(sql)
                res = cursor.fetchall()
                ls = list(res)
                self.lineEdit_2.setText(str(ls[0][0]))
            except Exception:
                traceback.print_exc()
                self.lineEdit_2.setText("无法查询，可能是您尚未评分")
                dialogwindow.label.setText("失败")
            finally:
                db.close()
        # 修改
        if self.sender() == self.pushButton_2:
            sql = "update `BX-Book-Ratings` set `Book-Rating` = '%d' where `User-ID` = '%s' and `ISBN` = '%s'" \
                  % (int(rating), user, bookID[0][0])
            try:
                cursor.execute(sql)
            except Exception:
                traceback.print_exc()
                dialogwindow.label.setText("失败")
            finally:
                db.close()
        # 返回
        if self.sender() == self.pushButton_3:
            firstwindow.show()
            self.close()
        # 评分
        if self.sender() == self.pushButton_4:
            sql = "insert into `BX-Book-Ratings`(`User-ID`, `ISBN`, `Book-Rating`) values('%s', '%s', '%d')" % (user, bookID[0][0], int(rating))
            try:
                cursor.execute(sql)
            except Exception:
                traceback.print_exc()
                dialogwindow.label.setText("失败")
            finally:
                db.close()

    def recommendItem(self, user_id):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('106.14.11.86', 8000))
        client.sendall(user_id.encode(encoding='utf_8', errors='strict'))
        recommended = client.recv(2048)
        result = recommended.decode(encoding='utf_8', errors='strict')
        self.listWidget.clear()
        # print(type(result))
        # print(result)
        recommendres = result.split('||')
        for i in range(len(recommendres)):
            self.listWidget.addItem("{0}".format(recommendres[i]))
        # self.listWidget.addItem(result)
        client.close()

    # def recommendItem(self, user_id, metric=metric):
    #     self.listWidget.clear()
    #     if (user_id not in ratings_matrix.index.values) or type(user_id) is not str:
    #         self.listWidget.addItem("User id should be a valid integer from this list :\n\n {} ".format(re.sub('[\[\]]', '', np.array_str(ratings_matrix.index.values))))
    #
    #     else:
    #         prediction = []
    #         for i in range(ratings_matrix.shape[1]):
    #             if (ratings_matrix[str(ratings_matrix.columns[i])][user_id] != 0): #not rated already
    #                 prediction.append(predict_itembased(user_id, str(ratings_matrix.columns[i]), ratings_matrix, metric))
    #             else:
    #                 prediction.append(-1) #for already rated items
    #         prediction = pd.Series(prediction)
    #         prediction = prediction.sort_values(ascending=False)
    #         recommended = prediction[:10]
    #         for i in range(len(recommended)):
    #             self.listWidget.addItem("{0}. {1}".format(i+1, books.bookTitle[recommended.index[i]]))


def check(window1, window2, window3):
    global firstwindow, adminwindow
    user, password = firstwindow.get_information()
    if user == firstwindow.adminuser and password == firstwindow.adminpassword:
        adminwindow.show()
        firstwindow.close()
        return
    if login():
        window2.recommendItem(user)
        window2.show()
        # window2.recommend_list()
        window1.close()
    else:
        window3.show()


def login():
    global firstwindow, dialogwindow
    URL = "106.14.11.86"
    User = "admin1"
    Password = "123456"
    Database = "bookcrossing"
    str_user, str_password = firstwindow.get_information()
    db = pymysql.connect(URL, User, Password, Database, charset='utf8')
    cursor = db.cursor()
    sql = "select `User-ID`, `Password` from `BX-Users` where `User-ID` = '%s'" % str_user
    try:
        db.ping(reconnect=True)
        cursor.execute(sql)
        res = cursor.fetchall()
        l = list(res)
        if str_user == l[0][0] and str_password == l[0][1]:
            return True
        elif str_user == l[0][0] and str_password != l[0][1]:
            dialogwindow.error_message(0, 1)
            return False
        elif len(l) == 0:
            dialogwindow.error_message(1, 0)
            return False
    except Exception:
        traceback.print_exc()
        dialogwindow.error_message(1, 0)
        return False
    finally:
        db.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    firstwindow = FirstWindow()
    secondwindow = SecondWindow()
    rwindow = RWindow()
    dialogwindow = DialogWindow()
    adminwindow = AdminWindow()
    bookaddwindow = BookaddWindow()


    # 从登陆跳到注册
    firstwindow.pushButton_2.clicked.connect(secondwindow.show)
    firstwindow.pushButton_2.clicked.connect(firstwindow.close)

    # 从注册返回登录
    secondwindow.pushButton_2.clicked.connect(firstwindow.show)
    secondwindow.pushButton_2.clicked.connect(secondwindow.close)

    # 登录界面确定身份
    firstwindow.pushButton_1.clicked.connect(lambda: check(firstwindow, rwindow, dialogwindow))

    # 推荐界面返回登录界面
    rwindow.pushButton_3.clicked.connect(firstwindow.show)
    rwindow.pushButton_3.clicked.connect(rwindow.close)

    # 错误提示对话框弹出返回登录界面
    dialogwindow.pushButton.clicked.connect(dialogwindow.close)

    # 注册信息
    secondwindow.pushButton.clicked.connect(secondwindow.register)
    secondwindow.pushButton.clicked.connect(firstwindow.show)
    secondwindow.pushButton.clicked.connect(secondwindow.close)

    # 管理员界面返回注册界面
    adminwindow.pushButton_5.clicked.connect(firstwindow.show)
    adminwindow.pushButton_5.clicked.connect(adminwindow.close)

    # 管理员添加图书
    bookaddwindow.pushButton.clicked.connect(bookaddwindow.add)
    bookaddwindow.pushButton_2.clicked.connect(adminwindow.show)
    bookaddwindow.pushButton_2.clicked.connect(bookaddwindow.close)

    # 管理员返回登录界面
    adminwindow.pushButton_5.clicked.connect(firstwindow.show)
    adminwindow.pushButton_5.clicked.connect(adminwindow.close)

    # 管理员操作
    adminwindow.pushButton.clicked.connect(adminwindow.action)
    adminwindow.pushButton_2.clicked.connect(adminwindow.action)
    adminwindow.pushButton_3.clicked.connect(adminwindow.action)
    adminwindow.pushButton_4.clicked.connect(adminwindow.action)

    # 推荐界面
    rwindow.pushButton.clicked.connect(rwindow.raction)
    rwindow.pushButton_2.clicked.connect(rwindow.raction)
    rwindow.pushButton_3.clicked.connect(rwindow.raction)
    rwindow.pushButton_4.clicked.connect(rwindow.raction)

    firstwindow.setWindowTitle("Book Recommend System")
    secondwindow.setWindowTitle("Book Recommend System")
    rwindow.setWindowTitle("Book Recommend System")
    adminwindow.setWindowTitle("Book Recommend System")
    bookaddwindow.setWindowTitle("Book Recommend System")
    palette = QPalette()
    palette.setBrush(QPalette.Background, QBrush(QPixmap("images/background.jpg")))
    firstwindow.setPalette(palette)
    secondwindow.setPalette(palette)
    rwindow.setPalette(palette)
    adminwindow.setPalette(palette)
    bookaddwindow.setPalette(palette)
    # firstwindow.resize(600, 534)
    firstwindow.show()
    sys.exit(app.exec_())


