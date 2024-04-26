# -*- coding: utf-8 -*-

import copy
import os
import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWizard, QWizardPage
from .projectpages import SelectProjectPage


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


class SaveSelectionPage(QIWizardPage):
    def __init__(self, parent=None):
        super(SaveSelectionPage, self).__init__(parent)

        # Set up layout
        self.layout = Qtw.QVBoxLayout()
        self.setLayout(self.layout)

    def initializePage(self):

        self.setTitle("Summary of Previous Selections")
        self.setSubTitle("Please provide file-paths to save the cleaned generated files to.")

        self.project_label = QLabel('Project: ' + self.settings.project.get_title())
        #self.investigation_label = QLabel('Investigation:') # + self.settings.investigation)
        #self.study_label = QLabel('Study:') # + self.settings.study)

        self.layout.addWidget(self.project_label)
        #self.layout.addWidget(self.investigation_label)
        #self.layout.addWidget(self.study_label)

        self.save_cleaned_odMLFile_button = QPushButton("Save cleaned odML-File")
        self.save_cleaned_odMLFile_button.clicked.connect(self.save_cleaned_odMLFile)
        self.layout.addWidget(self.save_cleaned_odMLFile_button)

        # cleaned odML-File
        self.save_cleaned_odMLSummary_button = QPushButton("Save cleaned odML-Summary")
        self.save_cleaned_odMLSummary_button.clicked.connect(self.save_cleaned_odMLSummary)
        self.layout.addWidget(self.save_cleaned_odMLSummary_button)

        # cleaned odML summary
        
        
    def save_cleaned_odMLSummary(self):
        path, _ = Qtw.QFileDialog.getSaveFileName(self, "Save File", "", ".csv files (*.csv)")
        self.settings.odml_selection.save_private_summary_table(path)
        self.settings.set_private_odml_summary_path(path)
        return

    def save_cleaned_odMLFile(self):
        path, _ = Qtw.QFileDialog.getSaveFileName(self, "Save File", "", ".odml files (*.odml)")
        self.settings.odml_selection.save_private_odml_file(path)
        self.settings.set_private_odml_path(path)
        return


    def validatePage(self):

        # make sure both files have been saved somewhere
        if self.settings.private_odml_path is None:
            return False
        if self.settings.private_odml_summary is None:
            return False


        return True