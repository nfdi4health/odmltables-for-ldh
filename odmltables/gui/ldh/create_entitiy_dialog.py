# -*- coding: utf-8 -*-

import copy
import os
import sys
import subprocess
from future.utils import iteritems

# Workaround Python 2 and 3 unicode handling.
try:
    unicode = unicode
except NameError:
    unicode = str

from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as Qtw
from odmltables.gui.pageutils import QIWizardPage
from PyQt5 import QtCore, QtWidgets, QtGui
from .data.ldh_entitiy import InstanceType, instanceTypeToString
from .data.project import Project
from .data.investigation import Investigation
from .data.study import Study
from .data.ldh_entitiy import Attribute

from .ldh_client import create_project, create_entity



class CreateEntityDialog(Qtw.QDialog):


    def __init__(self, selectPage, callbac_function, instanceType: InstanceType):
        super().__init__()
        self.originPage = selectPage
        self.entity = self.helper_create_Entitiy(instanceType)
        self.instanceType = instanceTypeToString(instanceType)
        self.setWindowTitle("Create " + self.instanceType)
        self.initUI()
        self.finished.connect(callbac_function)

    def helper_create_Entitiy(self, instanceType):
        if instanceType == InstanceType.PROJECT:
            return Project(None)
        if instanceType == InstanceType.INVESTIGATION:
            return Investigation(None, None)
        if instanceType == InstanceType.STUDY:
            return Study(None, None)


    def initUI(self):

        
        institution_name = self.originPage.settings.institution_name
        if self.originPage.settings.project is not None:
            project_title = self.originPage.settings.project.get_title()
        else:
            project_title = ""

        vbox, attribute_dict = self.entity.create_layout(project_title=project_title, institution_name=institution_name)
        self.attribute_dict = attribute_dict

            
        # set everything known about entitiy from apiToken
        self.entity.set_institution(self.originPage.settings.institution_id, self.originPage.settings.institution_name)
        self.entity.add_member(self.originPage.settings.user_id, self.originPage.settings.institution_id)


        self.commit_button = Qtw.QPushButton("Create " + self.instanceType)
        self.commit_button.clicked.connect(self.createEntitiy)

        vbox.addWidget(self.commit_button)


        self.setWindowTitle('Create New ' + self.instanceType)
        self.setLayout(vbox)

    def createEntitiy(self,):
        if create_entity(self.entity, self.attribute_dict):
            self.originPage.settings.set_project(self.entity)
            self.accept()
        else: 
            self.reject()
