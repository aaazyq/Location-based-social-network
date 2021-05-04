import numpy as np
import pandas as pd
import math
import random

similarity_matrix = ['similarity_smallcate.csv','similarity_bigcate.csv','similarity_time_space.csv','similarity_place.csv']
dis_prefer = pd.read_csv('distance_preference.csv')
checkin_times = pd.read_csv('CheckInTimes.csv')

def simi_user(user, n, matrix_no):
    # find top n similar user
    # return user id

    # read similarity_matrix
    similarity = pd.read_csv(similarity_matrix[matrix_no])
    similarity.index = range(1, len(similarity) + 1)
    # find similar users
    user_row = pd.DataFrame(similarity.loc[user])
    sort = pd.DataFrame.sort_values(user_row, by=user, ascending=False)
    return [int(i) for i in sort[:n].index]


def already_been(user):
    return checkin_times.loc[checkin_times.userId == user]


def candidate_place(user, n, matrix_no):
    s_users = simi_user(user, n, matrix_no)
    candidates = pd.DataFrame(columns=('venueId', 'venueCategory', 'latitude', 'longitude', 'CheckInCount'))
    for i in s_users:
        candidates = candidates.append(checkin_times.loc[checkin_times.userId == i][
                                           ['venueId', 'venueCategory', 'latitude', 'longitude', 'CheckInCount']])
    new = pd.DataFrame(columns=('venueId', 'venueCategory', 'latitude', 'longitude', 'CheckInCount'))
    for i in candidates.venueId.unique():
        temp = candidates[candidates.venueId == i]
        new = new.append(
            {'venueId': i, 'venueCategory': list(temp.venueCategory)[0], 'latitude': list(temp.latitude)[0],
             'longitude': list(temp.longitude)[0], 'CheckInCount': np.sum(temp.CheckInCount)}, ignore_index=True)
    # delete places already been
    already = already_been(user)
    feasible_place = new.loc[~new.venueId.isin(already['venueId'])]
    feasible_place = pd.DataFrame.sort_values(feasible_place, ['CheckInCount'], ascending=False)
    return feasible_place


def distance(lat0, lon0, lat1, lon1):
    return np.sqrt((lat1 - lat0) ** 2 * (111 * np.cos(lat1)) ** 2 + (lon1 - lon0) ** 2 * 111 ** 2)


def recommend(user, topN, neighbours, matrix_no):
    final_choice = pd.DataFrame(columns=('venueId', 'venueCategory', 'latitude', 'longitude', 'distance'))
    dist = dis_prefer.loc[user]
    lat0, lon0, aver = dist.latitude, dist.longitude, dist.avgDistanceTravel
    places = candidate_place(user, neighbours, matrix_no)
    for i in list(places.index):
        if len(final_choice) == topN:
            final_choice.drop(columns=['CheckInCount'], inplace=True)
            final_choice.index = range(1, len(final_choice) + 1)
            return final_choice
        p = places.loc[i]
        lat1 = p.latitude
        lon1 = p.longitude
        km = distance(lat0, lon0, lat1, lon1)
        if km < aver:
            final_choice = final_choice.append(p)
            final_choice.loc[p.name, 'distance'] = km
    if len(final_choice) == 0:
        return 'Can not find any new place to go.'
    else:
        final_choice.drop(columns=['CheckInCount'], inplace=True)
        final_choice.index = range(1, len(final_choice) + 1)
        return final_choice

def roll(user, topN):
    final_choice = pd.DataFrame(columns=('venueId', 'venueCategory', 'latitude', 'longitude', 'distance'))
    for i in range(topN):
        roll = checkin_times.loc[random.randint(1, 211955)]
        dist = dis_prefer.loc[user]
        lat0, lon0, aver = dist.latitude, dist.longitude, dist.avgDistanceTravel
        lat1 = roll.latitude
        long1 =roll.longitude
        km = distance(lat0, lon0, lat1, long1)
        final_choice = final_choice.append({'venueId': roll.venueId, 'venueCategory': roll.venueCategory, 'latitude': lat1,
             'longitude':long1 , 'distance': km}, ignore_index=True)
    final_choice.index = range(1, len(final_choice) + 1)
    return final_choice

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit , QPushButton ,QMessageBox
import sys
import warnings


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = "Where To Go?"
        self.top = 100
        self.left = 100
        self.width = 700
        self.height = 400

        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon("location.jpg"))
        self.setGeometry(self.top, self.left, self.width, self.height)
        # p = self.palette()
        # p.setColor(self.backgroundRole(), QtGui.QColor(255, 255, 255))
        # self.setPalette(p)
        window_pale = QtGui.QPalette()
        window_pale.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('background3.jpg')))
        self.setPalette(window_pale)

        self.linedit = QLineEdit(self)
        self.linedit.setPlaceholderText("Your User ID")
        self.linedit.setStyleSheet("font-size: 13px;")
        self.linedit.move(50, 30)
        self.linedit.resize(280, 40)

        self.linedit2 = QLineEdit(self)
        self.linedit2.setPlaceholderText("Return N Recommendations")
        self.linedit2.setStyleSheet("font-size: 13px;")
        self.linedit2.move(50, 80)
        self.linedit2.resize(280, 40)

        self.linedit3 = QLineEdit(self)
        self.linedit3.setPlaceholderText("According To How Many Neighbours ")
        self.linedit3.setStyleSheet("font-size: 13px;")
        self.linedit3.move(50, 130)
        self.linedit3.resize(280, 40)

        self.button = QPushButton("Based On Places", self)
        self.button.move(50, 180)
        self.button.resize(280, 40)
        self.button.setStyleSheet("background-color: 	#FFE7BA;font-size: 15px;color:black;font:bold;")
        self.setStyleSheet("QMessageBox {background-color: white;font-size: 14px;}")
        self.button.clicked.connect(self.onClick)

        self.button = QPushButton("Based On Interets", self)
        self.button.move(50, 280)
        self.button.resize(280, 40)
        self.button.setStyleSheet("background-color: 	#FFE7BA;font-size: 15px;color:black;font:bold;")
        self.setStyleSheet("QMessageBox {background-color: white;font-size: 14px;}")
        self.button.clicked.connect(self.onClick2)

        self.button = QPushButton("Based On Track", self)
        self.button.move(50, 230)
        self.button.resize(280, 40)
        self.button.setStyleSheet("background-color: 	#FFE7BA;font-size: 15px;color:black;font:bold;")
        self.setStyleSheet("QMessageBox {background-color: white;font-size: 14px;}")
        self.button.clicked.connect(self.onClick3)

        self.button = QPushButton("Based On Interests (Detailed)", self)
        self.button.move(50, 330)
        self.button.resize(280, 40)
        self.button.setStyleSheet("background-color: 	#FFE7BA;font-size: 15px;color:black;font:bold;")
        self.setStyleSheet("QMessageBox {background-color: white;font-size: 14px;}")
        self.button.clicked.connect(self.onClick4)

        self.button = QPushButton("Leave It To GOD", self)
        self.button.move(370, 30)
        self.button.resize(280, 40)
        self.button.setStyleSheet("background-color: #FFF5EE;font-size: 15px;color:black;font:bold;")
        self.setStyleSheet("QMessageBox {background-color: white;font-size: 14px;}")
        self.button.clicked.connect(self.onClick5)

        self.show()

    def onClick(self):
        user = self.linedit.text()
        topN = self.linedit2.text()
        neighbours = self.linedit3.text()
        try:
            user = int(user)
            topN = int(topN)
            neighbours = int(neighbours)
        except:
            showErrorMessage(self, "Please Input Integers :)")
        if user < 0 or user > 2293:
            showErrorMessage(self, "ID should in [1, 2293]")
        else:
            try:
                place = recommend(user, topN, neighbours, 3)
            except:
                showErrorMessage(self, "Our Codes Get Wrong.[doge]")
            try:
                showMessage(self, place)
            except:
                showErrorMessage(self, "UI Get Wrong.[doge]")

    def onClick2(self):
        user = self.linedit.text()
        topN = self.linedit2.text()
        neighbours = self.linedit3.text()
        try:
            user = int(user)
            topN = int(topN)
            neighbours = int(neighbours)
        except:
            showErrorMessage(self, "Please Input Integers :)")
        if user < 0 or user > 2293:
            showErrorMessage(self, "ID should in [1, 2293]")
        else:
            try:
                place = recommend(user, topN, neighbours, 0)
            except:
                showErrorMessage(self, "Our Codes Get Wrong.[doge]")
            try:
                showMessage(self, place)
            except:
                showErrorMessage(self, "UI Get Wrong.[doge]")

    def onClick3(self):
        user = self.linedit.text()
        topN = self.linedit2.text()
        neighbours = self.linedit3.text()
        try:
            user = int(user)
            topN = int(topN)
            neighbours = int(neighbours)
        except:
            showErrorMessage(self, "Please Input Integers :)")
        if user < 0 or user > 2293:
            showErrorMessage(self, "ID should in [1, 2293]")
        else:
            try:
                place = recommend(user, topN, neighbours, 2)
            except:
                showErrorMessage(self, "Our Codes Get Wrong.[doge]")
            try:
                showMessage(self, place)
            except:
                showErrorMessage(self, "UI Get Wrong.[doge]")

    def onClick4(self):
        user = self.linedit.text()
        topN = self.linedit2.text()
        neighbours = self.linedit3.text()
        try:
            user = int(user)
            topN = int(topN)
            neighbours = int(neighbours)
        except:
            showErrorMessage(self, "Please Input Integers :)")
        if user < 0 or user > 2293:
            showErrorMessage(self, "ID should in [1, 2293]")
        else:
            try:
                place = recommend(user, topN, neighbours, 1)
            except:
                showErrorMessage(self, "Our Codes Get Wrong.[doge]")
            try:
                showMessage(self, place)
            except:
                showErrorMessage(self, "UI Get Wrong.[doge]")

    def onClick5(self):
        user = self.linedit.text()
        topN = self.linedit2.text()
        try:
            user = int(user)
            topN = int(topN)
        except:
            showErrorMessage(self, "Please Input Integers :)")
        if user < 0 or user > 2293:
            showErrorMessage(self, "ID should in [1, 2293]")
        else:
            try:
                place = roll(user, topN)
            except:
                showErrorMessage(self, "Our Codes Get Wrong.[doge]")
            try:
                showMessage(self, place)
            except:
                showErrorMessage(self, "UI Get Wrong.[doge]")

def showMessage(self, place):
    msg = QMessageBox()
    if len(place) == 0:
        msg.about(self, 'Oh No',"""<font color='black'><p><b>No More New Places For You.</b> """)
    else:
        cate = []
        lat = []
        long = []
        dist = []
        for index, row in place.iterrows():
            cate.append(row["venueCategory"])
            lat0 = row["latitude"]
            long0 = row["longitude"]
            dist0 = row["distance"]
            lat.append(round(float(lat0),3))
            long.append(round(float(long0),3))
            dist.append(round(float(dist0),3))
        for i in range(len(cate)):
            msg.about(self, 'Recommendation',
                      """<font color='black'><p><b>Catagory :</b> """ + str(cate[i]) + """</p>
                <p><b>Latitude: </b>""" + str(lat[i]) +
                """<p><b>Longitude: </b>""" + str(long[i])+
                   """<p><b>Distance: </b>""" + str(dist[i])+"""km""")

def showErrorMessage(self, message):
    msg = QMessageBox()
    msg.about(self, 'Something Wrong',
              """<font color='black'><p><b><br/>""" + message)

app = QtCore.QCoreApplication.instance()
if app is None:
    app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec())