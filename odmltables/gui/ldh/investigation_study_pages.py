# -*- coding: utf-8 -*-

import copy
import os
import sys
import subprocess
from future.utils import iteritems
from .create_entitiy_dialog import CreateEntityDialog
from .data.ldh_entitiy import InstanceType

# Workaround Python 2 and 3 unicode handling.
try:
    unicode = unicode
except NameError:
    unicode = str

from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as Qtw
from odmltables.gui.pageutils import QIWizardPage
from PyQt5 import QtCore, QtWidgets, QtGui
from .selectfiletopublishpage import SelectFileToPublishPage

class SelectInvestigationStudyPage(QIWizardPage):
    def __init__(self, parent=None):
        super(SelectInvestigationStudyPage, self).__init__(parent)
        self.setMinimumHeight(650)
        

    def initializePage(self):

        self.layout = Qtw.QVBoxLayout()
        self.setLayout(self.layout)
        
        self.studies = []

        self.setTitle("Select Investigation and Study")

        self.title_label = Qtw.QLabel("Your Project is involved in the following Investigations: \n" + 
                                "Choose the investigation you want to upload data to or create new investigation")
        self.layout.addWidget(self.title_label)

        self.grid = QtWidgets.QGridLayout()
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)
        self.layout.addLayout(self.grid)

        self.investigation_vBox = Qtw.QVBoxLayout()
        self.investigation_group=Qtw.QButtonGroup(self.investigation_vBox) 
        self.investigation_group.setExclusive(True)
        for investigation in self.investigations:
            radiobutton = Qtw.QRadioButton(investigation)
            radiobutton.investigation = investigation
            radiobutton.toggled.connect(self.selectInvestigation)
            self.investigation_group.addButton(radiobutton)
            self.investigation_vBox.addWidget(radiobutton)
        self.layout.addLayout(self.investigation_vBox)
        
        self.newinvestigation_button = Qtw.QPushButton("Create New Investigation")
        self.newinvestigation_button.clicked.connect(self.createInvestigation)
        self.layout.addWidget(self.newinvestigation_button)

        # layout for studies 
        # TODO hide labels
        self.study_title_label = Qtw.QLabel("Your Investigation is involved in the following Studies: \n" + 
                                "Choose the study you want to upload data to or create a new study")
        self.layout.addWidget(self.study_title_label)
        self.study_title_label.hide()
        self.study_vBox = Qtw.QVBoxLayout()
        self.layout.addLayout(self.study_vBox)

        self.create_study_button = Qtw.QPushButton("Create new Study")
        self.create_study_button.clicked.connect(self.createStudy)
        self.layout.addWidget(self.create_study_button)
        self.create_study_button.hide()
        self.layout.addStretch()


    def selectInvestigation(self):
        self.studies = []

        radioButton = self.sender()
        if radioButton.isChecked():
            print("Investigation is %s" % (radioButton.investigation))
        # TODO save investigation for later
        
        self.study_title_label.show()
        self.create_study_button.show()

        # TODO request associated studies
        if radioButton.investigation == "Investigation A":
            self.studies = ["Study 1", "Study 2", "Study 3"]
        else:
            self.studies = ["Study A", "Study B", "Study C", "Study D"]

        # TODO clear study radio buttons
        for i in reversed(range(self.study_vBox.count())): 
            widgetToRemove = self.study_vBox.itemAt(i).widget()
            # remove it from the layout list
            self.study_vBox.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

        self.study_group=Qtw.QButtonGroup(self.study_vBox) 
        self.study_group.setExclusive(True)
        for study in self.studies:
            radiobutton = Qtw.QRadioButton(study)
            radiobutton.study = study
            radiobutton.toggled.connect(self.selectStudy)
            self.study_group.addButton(radioButton)
            self.study_vBox.addWidget(radiobutton)
        self.layout.addLayout(self.study_vBox)

        self.wizard().adjustSize()



    def selectStudy(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            print("Study is %s" % (radioButton.study))
        # TODO

    def on_investigation_dialog_closed(self, result):
        if result == Qtw.QDialog.Accepted:
            print("Dialog accepted.")
            # TODO reload projects
        elif result == Qtw.QDialog.Rejected:
            print("Dialog rejected.")
        else:
            print("Dialog closed.")

    def on_study_dialog_closed(self, result):
        if result == Qtw.QDialog.Accepted:
            print("Dialog accepted.")
            # TODO reload projects
        elif result == Qtw.QDialog.Rejected:
            print("Dialog rejected.")
        else:
            print("Dialog closed.")

    def createInvestigation(self):
        self.w = CreateEntityDialog(self, self.on_investigation_dialog_closed, InstanceType.INVESTIGATION)
        self.w.exec_()

    def createStudy(self):
        self.w = CreateEntityDialog(self, self.on_study_dialog_closed,  InstanceType.STUDY)
        self.w.exec_()

    def validatePage(self):
        return True

    def nextId(self):
            # TODO 
            return self.wizard().SelectFileToPublishPage
    
    