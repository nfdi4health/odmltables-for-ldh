# -*- coding: utf-8 -*-
from .data.data_file import DataFile


from future.utils import iteritems
import re
import os

from .data.data_collection_description import DataCollectionDescription
from .ldh_client import create_and_upload_data_file, update_project

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import PyQt5.QtWidgets as Qtw

from .data.ldh_entitiy import EditableTextBrowser

# Workaround Python 2 and 3 unicode handling.
try:
    unicode = unicode
except NameError:
    unicode = str

from odmltables.gui.pageutils import QIWizardPage, shorten_path


mng_tags = ["MNG",
                "data collection",
                "data set",
                "dataset",
                "electrophysiology",
                "meta-data",
                "microneurography",
                "odML"]

def clearLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            elif item.layout() is not None:
                clearLayout(item.layout())

class FinalPage(QIWizardPage):
    def __init__(self, parent=None):
        super(FinalPage, self).__init__(parent)

        # Set up layout
        self.layout = Qtw.QVBoxLayout()
        self.setLayout(self.layout)



    def fill_entity_layout(self, entity, attribute_dict):
        for key, value in attribute_dict.items():
            if key == "description" and isinstance(value, EditableTextBrowser):
                content = entity.get_attribute_value(key)
                # Replace newlines with <br> for HTML
                content = content.replace('\n', '<br>')
                value.setHtml(content)
            else:
                value.setText(str(entity.get_attribute_value(key)))
                if key not in ["start_date", "end_date", "web_page", "wiki_page"]:
                    value.setReadOnly(True)



    def create_summary_data_file(self):
        self.summary_data_file = DataFile( self.settings.project.get_title() + " - Summarized Table of odML Metadata")
        self.summary_data_file.change_description("This DataFile contains a tabular summary of the meta-data of the corresponding data set, based on the Epxeriment and Recording odML-table template. You can use it to browse more detailed information on the Local Data Hub web page." + self.context_description)
        self.summary_data_file.add_member(self.settings.user_id, self.settings.institution_id)
        self.summary_data_file.add_project(self.settings.project.id, self.settings.project.get_title())
        self.summary_data_file.add_tags(mng_tags)
        self.summary_data_file.set_content_blob(self.settings.private_odml_summary)



    def create_odml_data_file(self):
        self.odml_data_file = DataFile(self.settings.project.get_title() + " - odML Metadata")
        self.odml_data_file.change_description("This DataFile contains an odML-file based on the Experiment and Recording odML-tables template, describing the meta-data of the data set collection. It may not be complete due to anonymization. \n \n ------------------------------------------------ \n \n" + self.context_description)
        self.odml_data_file.add_member(self.settings.user_id, self.settings.institution_id)
        self.odml_data_file.add_project(self.settings.project.id, self.settings.project.get_title())
        self.odml_data_file.add_tags(mng_tags)
        self.odml_data_file.set_content_blob(self.settings.private_odml_path)



    def initializePage(self):
        clearLayout(self.layout)

        self.setTitle("Review and Confirm Data Submission<br>")
        self.setSubTitle("Please verify the accuracy of the information before finalizing. Click 'Next' to upload the data to the Local Data Hub.")

        full_text = self.settings.data_set_link_text

        # Use regular expression to extract URL
        url_match = re.search(r'(https?://[^\s]+)', full_text)
        dataset_link = url_match.group(1) if url_match else ""

        if dataset_link != "":
            self.context_description = "\n \nThe data set described by this meta-data is avaiable at: " + f'<a href="{dataset_link}">Dataset Path</a>' + "\n \n ------------------------------------------------ \n \n	"
        else:
            self.context_description = self.settings.data_set_link_text + "\n \n ------------------------------------------------ \n \n	"
        
        self.context_description += DataCollectionDescription(self.settings.odml_selection.transform_to_single_table()).create_description()
        self.create_summary_data_file()
        # why is this overwritten? 
        self.create_odml_data_file()

        # update description of project
        if self.settings.project.get_description() is None:
            self.settings.project.change_attribute_value("description", "\n \n ------------------------------------------------ \n \n" + self.context_description)
        else:
            self.settings.project.change_attribute_value("description", self.settings.project.get_description() + "\n \n ------------------------------------------------ \n \n" + self.context_description)
        vbox_project, attribute_dict =  self.settings.project.create_layout()
        self.project_attribute_dict = attribute_dict

        #collection = self.settings.collection
        #vbox_collection, attribute_dict = collection.create_layout()
        #self.collection_attribute_dict = attribute_dict

        # TODO add Checkboxes so one of them can be deselected

        vbox_summary, attribute_dict = self.summary_data_file.create_layout()
        self.summary_attribute_dict = attribute_dict
        summary_label = Qtw.QLabel("Path to private summary File:")
        # TODO turn into clickable link
        # file_path_label = Qtw.QLabel(shorten_path(self.settings.private_odml_summary))

        # Clickable label
        # file_path = shorten_path(self.settings.private_odml_summary)
        file_path_label = Qtw.QLabel(f'<a href="{self.settings.private_odml_summary}">{shorten_path(self.settings.private_odml_summary)}</a>')
        file_path_label.setOpenExternalLinks(False)  # Prevents automatic opening of links
        file_path_label.linkActivated.connect(self.open_link)  # Connects to a method to handle link activation

        dataset_summary_label = Qtw.QLabel("The data set described by this meta-data is avaiable at: ")
        dataset_path_label = Qtw.QLabel(f'<a href="{dataset_link}">Dataset Path</a>')
        dataset_path_label.setOpenExternalLinks(True)


        vbox_summary.addWidget(summary_label)
        vbox_summary.addWidget(file_path_label)
        vbox_summary.addWidget(dataset_summary_label)
        vbox_summary.addWidget(dataset_path_label)

        vbox_odml , attribute_dict = self.odml_data_file.create_layout()
        self.odml_attribute_dict = attribute_dict
        odml_label = Qtw.QLabel("Path to private odML File:")
        # TODO turn into clickable link to open the folder the file lies in
        # odml_path_label =  Qtw.QLabel(shorten_path(self.settings.private_odml_path))
        # Get the path from the settings
        private_odml_path = self.settings.private_odml_path

        # Create the clickable label
        odml_path_label = Qtw.QLabel()
        odml_path_label.setText(f'<a href="file://{os.path.dirname(private_odml_path)}">{shorten_path(private_odml_path)}</a>')
        odml_path_label.setOpenExternalLinks(True)  # Enable opening links

        vbox_odml.addWidget(odml_label)
        vbox_odml.addWidget(odml_path_label)

        hbox = Qtw.QHBoxLayout()
        hbox.addLayout(vbox_project)
        #hbox.addLayout(vbox_collection)
        hbox.addLayout(vbox_summary)
        hbox.addLayout(vbox_odml)

        outer_vbox = Qtw.QVBoxLayout()
        outer_vbox.addLayout(hbox)
        self.layout.addLayout(outer_vbox)

        self.fill_entity_layout(self.settings.project, self.project_attribute_dict)
        self.fill_entity_layout(self.summary_data_file, self.summary_attribute_dict)
        self.fill_entity_layout(self.odml_data_file, self.odml_attribute_dict)
        #self.fill_entity_layout(collection, self.collection_attribute_dict)

        pass

    def open_link(self, link):
        QDesktopServices.openUrl(QUrl.fromLocalFile(link))

    def validatePage(self):
        ok = update_project(self.settings.project, self.project_attribute_dict)
        if not ok:
            print("Update of Project failed")
            return False

        ok, summary_url = create_and_upload_data_file(self.summary_data_file, self.summary_attribute_dict)
        if ok:
            ok, odml_url = create_and_upload_data_file(self.odml_data_file, self.odml_attribute_dict)
            if ok:
                # Pass the URLs to the wizard
                self.wizard().setProperty('summary_url', summary_url)
                self.wizard().setProperty('odml_url', odml_url)
                return True
            else:
                print("Creation of odML Data File failed")
                return False
        else:
            print("Creation of Summary Data File failed")
            return False