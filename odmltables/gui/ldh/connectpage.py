# -*- coding: utf-8 -*-

import copy
import os
import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWizard, QWizardPage
from .projectpages import SelectProjectPage
from .ldh_client import check_credentials, get_first_institution_of_user, get_first_user


from future.utils import iteritems

# Workaround Python 2 and 3 unicode handling.
try:
    unicode = unicode
except NameError:
    unicode = str

from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as Qtw

from odmltables import odml_table
from odmltables.gui.pageutils import QIWizardPage, clearLayout, shorten_path


class ConnectPage(QIWizardPage):
    def __init__(self, parent=None):
        super(ConnectPage, self).__init__(parent)

        # Set up layout
        self.layout = Qtw.QVBoxLayout()
        self.setLayout(self.layout)

    def initializePage(self):

        self.setTitle("Connect to the Local Data Hub")
        self.setSubTitle("Please provide the URL and your API token to connect to the Local Data Hub.")

        self.ldh_label = QLabel('Local Data Hub (URL):')
        self.ldh_edit = QLineEdit()
        self.registerField('ldh*', self.ldh_edit)
        self.apitoken_label = QLabel('apiToken:')
        self.apitoken_edit = QLineEdit()
        self.registerField('apitoken*', self.apitoken_edit)
        
        self.layout.addWidget(self.ldh_label)
        self.layout.addWidget(self.ldh_edit)
        self.layout.addWidget(self.apitoken_label)
        self.layout.addWidget(self.apitoken_edit)



    def validatePage(self):

        url = self.ldh_edit.text()
        api_token = self.apitoken_edit.text()

        correct = check_credentials(url, api_token)

        if not correct:
            # TODO make more distinc error messages in future version
            Qtw.QMessageBox.warning(self, 'Invalid Credentials', 'The provided credentials are invalid. Please check again.')
            return False
        else:
            
            self.settings.set_url(url)
            self.settings.set_api_token(api_token)

            # get institution
            id, name = get_first_institution_of_user()
            self.settings.set_institution(id, name)

            # get user of API 
            personal_id = get_first_user()
            self.settings.set_user(personal_id)

            return True