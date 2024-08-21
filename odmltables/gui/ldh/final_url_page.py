# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import re

def shorten_path(path):
    sep = os.path.sep
    if path.count(sep) > 2:
        id = path.rfind(sep)
        id = path.rfind(sep, 0, id)
    else:
        id = 0
    if path == '':
        return path
    else:
        return "...%s" % (path[id:])

class FinalURLPage(QWizardPage):
    def __init__(self, settings, parent=None):
        super(FinalURLPage, self).__init__(parent)
        self.settings = settings
        self.setTitle("Summary of Your Published Data Files<br>")
        self.setSubTitle("Here are the links to your uploaded files and their locations. You can access the files by clicking on the links below.")

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Published URLs Group
        published_group = QGroupBox()
        published_layout = QVBoxLayout()
        published_layout.setSpacing(5)  # Reduce spacing between elements

        published_title = QLabel("Published URLs")
        self._style_header(published_title)
        published_layout.addWidget(published_title)

        # Create labels and adjust style
        self.summary_label = QLabel("Published Summary Data File: <a href='summary_url'>Click here to view the summary file</a>")
        self.odml_label = QLabel("Published odML Data File: <a href='odml_url'>Click here to view the odML file</a>")
        self.project_url_label = QLabel("Project Page: <a href='project_url'>Click here to view the project</a>")

        self._style_label(self.summary_label)
        self._style_label(self.odml_label)
        self._style_label(self.project_url_label)

        published_layout.addWidget(self.project_url_label)
        published_layout.addWidget(self.summary_label)
        published_layout.addWidget(self.odml_label)

        published_group.setLayout(published_layout)
        layout.addWidget(published_group)

        # Dataset Path Group
        dataset_group = QGroupBox()
        dataset_layout = QVBoxLayout()

        dataset_title = QLabel("Dataset Information")
        self._style_header(dataset_title)
        dataset_layout.addWidget(dataset_title)

        self.dataset_path_label = QLabel()
        self._style_label(self.dataset_path_label)
        dataset_layout.addWidget(self.dataset_path_label)

        dataset_group.setLayout(dataset_layout)
        layout.addWidget(dataset_group)

        # Setting the main layout
        self.setLayout(layout)

    def _style_label(self, label):
        """Apply styling to the labels."""
        font = QFont()
        font.setPointSize(11)
        label.setFont(font)
        label.setOpenExternalLinks(True)
        label.setStyleSheet("padding: 3px;")

    def _style_header(self, label):
        """Apply styling to the section headers."""
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        label.setFont(font)
        label.setStyleSheet("margin-bottom: 5px;")

    def initializePage(self):
        super(FinalURLPage, self).initializePage()

        full_text = self.settings.data_set_link_text

        # Use regular expression to extract URL
        url_match = re.search(r'(https?://[^\s]+)', full_text)
        dataset_link = url_match.group(1) if url_match else ""

        # Dataset Path Label
        self.dataset_path_label.setText(
            f'Dataset is available at: <a href="{dataset_link}">Click here to view the dataset</a>'
        )
        self.dataset_path_label.setOpenExternalLinks(True)

        # Published URLs
        summary_url = self.wizard().property('summary_url')
        odml_url = self.wizard().property('odml_url')

        self.summary_label.setText(
            f"Published Summary Data File: <a href='{summary_url}'>Click here to view the summary file</a>"
        )
        self.odml_label.setText(
            f"Published odML Data File: <a href='{odml_url}'>Click here to view the odML file</a>"
        )

        # Generate and display the project URL
        selected_project_id = self.wizard().property('selected_project_id')
        project_url = f"http://localhost:3000/projects/{selected_project_id}"
        self.project_url_label.setText(
            f"Project Page: <a href='{project_url}'>Click here to view the project</a>"
        )
