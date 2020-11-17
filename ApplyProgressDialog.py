# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ApplyProgressDialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        ProgressDialog.setObjectName("ProgressDialog")
        ProgressDialog.resize(400, 277)
        ProgressDialog.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.gridLayout = QtWidgets.QGridLayout(ProgressDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(ProgressDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(100)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 4)
        self.canelButton = QtWidgets.QPushButton(ProgressDialog)
        self.canelButton.setObjectName("canelButton")
        self.gridLayout.addWidget(self.canelButton, 4, 3, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(ProgressDialog)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 4)
        self.stopButton = QtWidgets.QPushButton(ProgressDialog)
        self.stopButton.setEnabled(False)
        self.stopButton.setObjectName("stopButton")
        self.gridLayout.addWidget(self.stopButton, 4, 2, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(ProgressDialog)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(100)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 4)
        self.continueButton = QtWidgets.QPushButton(ProgressDialog)
        self.continueButton.setEnabled(False)
        self.continueButton.setObjectName("continueButton")
        self.gridLayout.addWidget(self.continueButton, 4, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)

        self.retranslateUi(ProgressDialog)
        QtCore.QMetaObject.connectSlotsByName(ProgressDialog)

    def retranslateUi(self, ProgressDialog):
        _translate = QtCore.QCoreApplication.translate
        ProgressDialog.setWindowTitle(_translate("ProgressDialog", "Progress Dialog"))
        self.label.setText(_translate("ProgressDialog", "Loading..."))
        self.canelButton.setText(_translate("ProgressDialog", "Canel"))
        self.stopButton.setText(_translate("ProgressDialog", "Stop"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("ProgressDialog", "Devices"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("ProgressDialog", "Attributes"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("ProgressDialog", "State"))
        self.continueButton.setText(_translate("ProgressDialog", "Continue"))
