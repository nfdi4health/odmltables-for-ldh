# -*- coding: utf-8 -*-

import copy
import os
import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWizard, QWizardPage
from .data.data_collection_description import DataCollectionDescription
from .data.collection import Collection
from .ldh_client import create_collection, client
from .client import HttpClient

from .ldh_client import create_entity

from future.utils import iteritems

# Workaround Python 2 and 3 unicode handling.
try:
    unicode = unicode
except NameError:
    unicode = str

from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as Qtw
import PyQt5.QtGui as QtGui

from odmltables import odml_table
from odmltables.gui.pageutils import QIWizardPage, clearLayout, shorten_path


class CollectionPage(QIWizardPage):
    def __init__(self, parent=None):
        super(CollectionPage, self).__init__(parent)
        

    def initializePage(self):

        self.setTitle("Create a Collection")
        self.setSubTitle("Please provide the needed informtion to create a collection.")

        self.entity = Collection(None)

        project_title = self.settings.project.get_title()
        vbox, attribute_dict = self.entity.create_layout(project_title)
        self.attribute_dict = attribute_dict
            
        
        # set everything known about entitiy from apiToken
        self.entity.set_institution(self.settings.institution_id, self.settings.institution_name)
        self.entity.add_member(self.settings.user_id, self.settings.institution_id)
        self.entity.add_project(self.settings.project.id, self.settings.project.get_title())

        self.generateDescription()
        self.setLayout(vbox)



    def generateDescription(self):
        d = DataCollectionDescription(self.settings.odml_selection.transform_to_single_table())
        desc = d.create_subject_description()

        self.attribute_dict["description"].insertPlainText(desc) 
        self.entity.change_attribute_value("description", desc)


    def validatePage(self):

        if create_entity(self.entity, self.attribute_dict):
            self.settings.set_collection(self.entity)
            return True
        else:
            return False
    
    