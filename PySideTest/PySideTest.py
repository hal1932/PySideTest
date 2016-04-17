# coding: utf-8
import sys
import os
import urllib2
from PySide import QtCore, QtGui

sys.path.append(os.path.join("D:", "Python27", "lib", "site-packages"))
import twitter

import twitterKeys as keys


gMayaApp = None
try:
    import shiboken
    import maya.OpenMayaUI as omui
    gMayaApp = shiboken.wrapInstance(long(omui.MQtUtil.mainWindow()), QtGui.QWidget)
except:
    pass


class AnimatableLabel(QtGui.QLabel):

    def __init__(self, parent=None):
        super(AnimatableLabel, self).__init__(parent)
        self.__movie = None
        self.__animated = False

    def setFile(self, filepath, width=-1, height=-1):
        if filepath is None:
            movie = self.__movie
        else:
            movie = QtGui.QMovie(filepath)
            self.__movie = movie

        self.setFrameNumber(0)

        if movie.frameCount() == 1:
            pix = self.currentPixmap()
            if width > 0 and height > 0:
                pix = pix.scaled(width, height)
            self.setPixmap(pix)
        else:
            if width > 0 and height > 0:
                movie.setScaledSize(QtCore.QSize(width, height))
                # 一度でも再生しないとscaledSizeが反映されない
                self.startMovie()
                self.stopMovie()

            self.setMovie(movie)

    def animated(self):
        return self.__animated

    def frameCount(self):
        return self.__movie.frameCount()

    def startMovie(self, frameNumber=-1):
        if self.frameCount() == 1:
            return
        self.setFrameNumber(frameNumber)
        self.__movie.start()
        self.__animated = True

    def stopMovie(self):
        if self.frameCount() == 1:
            return
        self.__movie.stop()
        self.__animated = False

    def setFrameNumber(self, frameNumber):
        if self.frameCount() == 1:
            frameNumber = 0
        if frameNumber >= 0:
            self.__movie.jumpToFrame(frameNumber)

    def currentPixmap(self):
        return self.__movie.currentPixmap()

    def setSize(self, width, height):
        self.setFile(None, width, height)


class TwitterIconLabel(AnimatableLabel):

    def __init__(self, parent=None):
        super(TwitterIconLabel, self).__init__(parent)
        self.setMouseTracking(True)

    def enterEvent(self, e):
        if not self.animated():
            self.startMovie()

    def leaveEvent(self, e):
        if self.animated():
            self.stopMovie()


class PostWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(PostWidget, self).__init__(parent)

    def setupUi(self, item=None):
        self.__layout = QtGui.QHBoxLayout()
        self.__layout.setContentsMargins(5, 5, 5, 5)

        self.__iconLabel = TwitterIconLabel()
        self.__layout.addWidget(self.__iconLabel)

        self.__textLayout = QtGui.QVBoxLayout()

        self.__infoLayout = QtGui.QHBoxLayout()
        self.__name = QtGui.QLabel()
        self.__screenName = QtGui.QLabel()
        self.__createdAt = QtGui.QLabel()
        self.__infoLayout.addWidget(self.__name)
        self.__infoLayout.addSpacing(10)
        self.__infoLayout.addWidget(self.__screenName)
        self.__infoLayout.addSpacing(30)
        self.__infoLayout.addWidget(self.__createdAt)
        self.__infoLayout.addStretch()
        self.__textLayout.addLayout(self.__infoLayout)

        self.__text = QtGui.QLabel("textaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.__text.setWordWrap(True)
        self.__textLayout.addWidget(self.__text)
        self.__layout.addLayout(self.__textLayout)

        self.setLayout(self.__layout)

        if not item is None:
            self.setItem(item)

    def sizeHint(self):
        return QtCore.QSize(400, 100)

    def setItem(self, item):
        self.__name.setText(item["name"])
        self.__screenName.setText(item["screen_name"])
        self.__text.setText(item["text"])
        self.__createdAt.setText(item["created_at"])
        self.__iconLabel.setFile(item["icon"], 48, 48)

class MyListWidget(QtGui.QListWidget):

    def __init__(self, parent=None):
        baseClass = super(MyListWidget, self)
        baseClass.__init__(parent)
        self.setSizeHint(baseClass.sizeHint())

    def setSizeHint(self, sizeHint):
        self.__sizeHint = sizeHint

    def sizeHint(self):
        return self.__sizeHint


def main():
    '''
    api = twitter.Api(keys.CONSUMER_KEY, keys.CONSUMER_SECRET, keys.ACCESS_TOKEN, keys.ACCESS_TOKEN_SECRET)
    statuses = api.GetHomeTimeline()

    data = []
    for status in statuses:
        user = status.user
        data.append({
           "name": user.name,
           "screen_name": user.screen_name,
           "text": status.text,
           "created_at": status.relative_created_at,
           "icon_url": user.profile_image_url,
           })

    for item in data:
        filepath = os.path.join(os.getcwd(), "icons", item["screen_name"] + "." + item["icon_url"].split(".")[-1])
        with open(filepath, "wb") as dst:
            iconData = urllib2.build_opener().open(item["icon_url"]).read()
            dst.write(iconData)
        item["icon"] = filepath
    '''
    data = []
    import glob
    for icon in glob.glob(os.path.join(os.getcwd(), "icons", "*")):
        id, _ = os.path.splitext(os.path.basename(icon))
        data.append({
            "name": "name_" + id,
            "screen_name": "screen_" + id,
            "text": "text_" + id,
            "created_at": "created_" + id,
            "icon": icon,
            })

    global gMayaApp
    localApp = None
    if gMayaApp is None:
        localApp = QtGui.QApplication(sys.argv)

    view = MyListWidget()
    for item in data:
        itemWidget = PostWidget()
        itemWidget.setupUi(item)
        listItem = QtGui.QListWidgetItem(view)
        listItem.setSizeHint(itemWidget.sizeHint())
        view.setItemWidget(listItem, itemWidget)

    frameMargin = view.frameWidth() * 2
    clientWidth = view.sizeHintForColumn(0) + frameMargin
    clientHeight = view.sizeHintForRow(0) * 5 + frameMargin
    view.setSizeHint(QtCore.QSize(clientWidth, clientHeight))
    view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    window = QtGui.QMainWindow()
    window.setCentralWidget(view)
    window.show()

    if not localApp is None:
        sys.exit(localApp.exec_())

    return window

if __name__ == '__main__':
    window = main()
