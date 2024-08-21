# -*- coding: utf-8 -*-

import copy
import os
import sys
import subprocess
from future.utils import iteritems
from .investigation_study_pages import SelectInvestigationStudyPage
from .create_entitiy_dialog import CreateEntityDialog
from .data.ldh_entitiy import InstanceType
from .ldh_client import get_all_projects, fetch_project

# Workaround Python 2 and 3 unicode handling.
try:
    unicode = unicode
except NameError:
    unicode = str

from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as Qtw
from odmltables.gui.pageutils import QIWizardPage
from PyQt5 import QtCore, QtWidgets, QtGui

class SelectProjectPage(QIWizardPage):
    def __init__(self, parent=None):
        super(SelectProjectPage, self).__init__(parent)
        self.layout = None
        self.button_group = None
        

    # def update_project_radio_buttons(self):

    #     known_project_ids = [button.project for button in self.button_group.buttons()]

    #     self.projects = get_all_projects()
    #     for id, title in self.projects.items():
    #         if not id in known_project_ids:
    #             radiobutton = Qtw.QRadioButton(title)
    #             radiobutton.project = id
    #             radiobutton.toggled.connect(self.selectProject)
    #             self.button_group.addButton(radiobutton)
    #             self.layout.addWidget(radiobutton)

    #     # resize the page to fit content
    #     self.resize(self.layout.sizeHint())

    def clear_layout(self):
        if self.layout is not None and isinstance(self.layout, Qtw.QLayout):
            while self.layout.count():
                child = self.layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

    def initializePage(self):
        # Ensure the layout is set up correctly
        if not isinstance(self.layout, Qtw.QVBoxLayout):
            self.layout = Qtw.QVBoxLayout()
            self.setLayout(self.layout)
        
        # Clear the existing layout before initializing
        self.clear_layout()
        
        self.projects = get_all_projects()

        self.setTitle("Choose a Project<br>")
        self.setSubTitle("Select an existing project to attach the data or create a new project.")

        self.title_label = Qtw.QLabel("You are involved in the following Projects: \n" + 
                                "Choose the project you want to upload data to or create new project")
        self.layout.addWidget(self.title_label)

        self.grid = QtWidgets.QGridLayout()
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)
        self.layout.addLayout(self.grid)

        self.button_group = QtWidgets.QButtonGroup(self)
        
        for id, title in self.projects.items():
            radiobutton = Qtw.QRadioButton(title)
            radiobutton.project = id
            radiobutton.toggled.connect(self.selectProject)
            self.button_group.addButton(radiobutton)
            self.layout.addWidget(radiobutton)

        self.newproject_button = Qtw.QPushButton("Create New Project")
        self.newproject_button.clicked.connect(self.createProject)
        #self.newproject_button.setDisabled(True)
        self.layout.addWidget(self.newproject_button)
        #self.setLayout(layout)

    def update_project_radio_buttons(self):
        self.initializePage()

    def selectProject(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            project = fetch_project(radioButton.project)
            self.settings.set_project(project)
            # Save the selected project ID to use later in the wizard
            self.wizard().setProperty('selected_project_id', radioButton.project)

    def createProject(self):
        self.w = CreateEntityDialog(self, self.on_dialog_closed, InstanceType.PROJECT)
        self.w.exec_()

    def on_dialog_closed(self, result):
        if result == Qtw.QDialog.Accepted:
            print("Dialog accepted.")
            self.update_project_radio_buttons()
        elif result == Qtw.QDialog.Rejected:
            print("Dialog rejected.")
        else:
            print("Dialog closed.")

    def validatePage(self):
        if self.settings.project is None:
            Qtw.QMessageBox.warning(self, 'No Project selected', 'Please select a project or create a new one.')
            return False
        return True