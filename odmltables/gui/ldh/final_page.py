# -*- coding: utf-8 -*-
from .data.data_file import DataFile


from future.utils import iteritems

from .data.data_collection_description import DataCollectionDescription
from .ldh_client import create_and_upload_data_file, update_project

# Workaround Python 2 and 3 unicode handling.
try:
    unicode = unicode
except NameError:
    unicode = str

import PyQt5.QtWidgets as Qtw

from odmltables.gui.pageutils import QIWizardPage, shorten_path


mng_tags = ["MNG",
                "data collection",
                "data set",
                "dataset",
                "electrophysiology",
                "meta-data",
                "microneurography",
                "odML"]

class FinalPage(QIWizardPage):
    def __init__(self, parent=None):
        super(FinalPage, self).__init__(parent)

        # Set up layout
        self.layout = Qtw.QVBoxLayout()
        self.setLayout(self.layout)




    def fill_entity_layout(self, entity, attribute_dict):

        for key, value in iteritems(attribute_dict):
            if key == "description":
                value.insertPlainText(entity.get_attribute_value(key))
            else:
                value.setText(str(entity.get_attribute_value(key)))
                if key != "start_date" and  key != "end_date" and key != "web_page" and key != "wiki_page" and key != "web_page":
                    value.setReadOnly(True)
            


    def create_summary_data_file(self):
        self.summary_data_file = DataFile( self.settings.project.get_title() + " - Summarized Table of odML Metadata")
        self.summary_data_file.change_description("This DataFile contains a tabular summary of the meta-data of the corresponding data set, based on the Epxeriment and Recording odML-table template. You can use it to browse more detailed information on the Local Data Hub web page. \n \n ------------------------------------------------ \n \n" + self.context_description)
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

        self.setTitle("Summary of Entered Information")
        self.setSubTitle("Please make sure all information entered is correct, edit if necessary. By clicking finish the data will be uploaded to the Local Data Hub.")

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
        file_path_label = Qtw.QLabel(shorten_path(self.settings.private_odml_summary))
        vbox_summary.addWidget(summary_label)
        vbox_summary.addWidget(file_path_label)

        vbox_odml , attribute_dict = self.odml_data_file.create_layout()
        self.odml_attribute_dict = attribute_dict
        odml_label = Qtw.QLabel("Path to private odML File:")
        # TODO turn into clickable link
        odml_path_label =  Qtw.QLabel(shorten_path(self.settings.private_odml_path))
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



    def validatePage(self):

        ok = update_project(self.settings.project, self.project_attribute_dict)
        if not ok:
            print("Update of Project failed")
            return False

        ok = create_and_upload_data_file(self.summary_data_file, self.summary_attribute_dict)
        if ok:
            ok = create_and_upload_data_file(self.odml_data_file, self.odml_attribute_dict)
            if ok:
                return True
            else:
                print("Creation of odML Data File failed")
                return False
        else:
            print("Creation of Summary Data File failed")
            return False