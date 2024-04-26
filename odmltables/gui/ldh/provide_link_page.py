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


class ProvideLinkPage(QIWizardPage):
    def __init__(self, parent=None):
        super(ProvideLinkPage, self).__init__(parent)

        # Set up layout
        self.layout = Qtw.QVBoxLayout()
        self.setLayout(self.layout)

    def initializePage(self):

        self.setTitle("Provide Link to Location of \"heavy\" Data Set")
        self.setSubTitle("Please provide the link to the location the data set described by the odML file is published. E.g. on G-Node.")

        # checkbox with label "The data set is not publicly available. Please contact the authors."
        self.not_public_radio = Qtw.QRadioButton("The data set is not publicly available. Please contact the authors.")
        self.layout.addWidget(self.not_public_radio)

        # checkbox with text edit "Link to data set"
        hbox = Qtw.QHBoxLayout()
        self.link_radio = Qtw.QRadioButton("Link to data set:")
        self.link_edit = QLineEdit()
        hbox.addWidget(self.link_radio)
        hbox.addWidget(self.link_edit)

        self.layout.addLayout(hbox)


    def validatePage(self):

        # Check if either of the radio buttons is selected
        if not self.not_public_radio.isChecked() and not self.link_radio.isChecked():
            Qtw.QMessageBox.critical(self, "Error", "Please select one of the options.")
            return False
        
        # save into settings which radio was selected
        if self.not_public_radio.isChecked():
            self.settings.set_data_set_link_text("The data set is not publicly available. Please contact the authors.")
        else:
            self.settings.set_data_set_link_text("The data set described by this meta-data is avaiable at: " + self.link_edit.text())

        return True