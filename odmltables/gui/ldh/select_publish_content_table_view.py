import copy
import os
import sys
import subprocess
import pandas as pd

from future.utils import iteritems

# Workaround Python 2 and 3 unicode handling.
try:
    unicode = unicode
except NameError:
    unicode = str

from PyQt5.QtCore import Qt, QModelIndex
import PyQt5.QtWidgets as Qtw
from PyQt5.QtGui import QBrush, QColor, QStandardItemModel, QStandardItem

from .data.odmlwithselection import OdmlTableWithSelection
import odml

#from ldh.odml_table_with_selection import OdmlTableWithSelection
from odmltables.gui.pageutils import QIWizardPage, clearLayout, shorten_path
from PyQt5.QtGui import QStandardItem
#from PyQt5 import pyqtsignal


selected_color = QColor(115, 174, 133)
deselected_color = QColor(211, 116, 116)

class PandasTableModel(QStandardItemModel):
   
    # here it would be pass by value ..... 
    def __init__(self, data, odml_dict: OdmlTableWithSelection, parent=None):
        QStandardItemModel.__init__(self, parent)
        self._data = data

        self.table_item_path_map = {}

        for idx, row in data.iterrows():
            experiment_id = row["General - ExperimentID"]
            recording_id = row["RecordingID"]
            data_col = []

            for column in data.columns:
                section_name = ""
                property_name = ""
                # from recording
                if column.startswith("Recording - "):
                    section_name = column.split(" - ")[1]
                    property_name = column.split(" - ")[2]
                    path = "/Experiments/{}/Recordings/{}/{}:{}".format(experiment_id, recording_id, section_name, property_name)
                elif column == "RecordingID":
                    path = ""
                else:
                    section_name = column.split(" - ")[0]
                    property_name = column.split(" - ")[1]
                    path = "/Experiments/{}/{}:{}".format(experiment_id, section_name, property_name)

                
                
                item = QStandardItem("{}".format(row[column]))
                item.setCheckable(True)
                if column == "RecordingID":
                    item.setCheckable(False)
                
                
                if path:
                    if odml_dict.get_selection(path.strip('/').replace(':', '/')):
                        item.setBackground(QBrush(selected_color)) # green
                        item.setCheckState(Qt.Checked)
                    else:
                        item.setBackground(QBrush(deselected_color)) # red
                        item.setCheckState(Qt.Unchecked)
                else:
                    item.setBackground(QBrush(QColor(255, 255, 255)))

                data_col.append(item)

                if path.strip('/').replace(':', '/') in self.table_item_path_map:
                    self.table_item_path_map[path.strip('/').replace(':', '/')].append(item)
                else:
                    self.table_item_path_map[path.strip('/').replace(':', '/')] = [item]

            self.appendRow(data_col)
            
        #for col in data.list():

        #    data_col = [QStandardItem("{}".format(x)) for x in data[col].values]
        #    self.appendColumn(data_col)
        return
    
    def get_path_table_item_map(self):
        return self.table_item_path_map

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, x, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[x]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[x]
        return None


class SelectContentTableViewPage(QIWizardPage):

    

    def __init__(self, parent=None):
        super(SelectContentTableViewPage, self).__init__(parent)

        self.hbox = Qtw.QVBoxLayout(self)
        self.setLayout(self.hbox)
     


    def initializePage(self):
        #self.update_attributes()

        self.setTitle("Summary Table of cleaned odML file")
        self.setSubTitle("Please confirm, that all sensitive fields have been deselected and edit if necessary.")

        self.df = self.settings.odml_selection.transform_to_single_table()
        self.display_df(self.df)
        self.hbox.addWidget(self.table_view)


    def display_df(self, df):
        # Create the pandas model
        self.model = PandasTableModel(df, self.settings.odml_selection)
        self.path_table_item_map = self.model.get_path_table_item_map()

        self.table_view = Qtw.QTableView()
        self.table_view.setModel(self.model)

        sizePolicy = Qtw.QSizePolicy(Qtw.QSizePolicy.MinimumExpanding, Qtw.QSizePolicy.MinimumExpanding)
        self.table_view.setSizePolicy(sizePolicy)
        self.table_view.setEditTriggers(Qtw.QAbstractItemView.NoEditTriggers)
        self.table_view.show()

        self.model.itemChanged.connect(self.updateCheckedStatus)
        self.table_view.setUpdatesEnabled(True)
        return self.table_view
        

    def updateCheckedStatus(self):
        self.model.blockSignals(True)
        # just redo all checked states for all items 
        for key, item in self.path_table_item_map.items():
            #  if one of them changed -> change checkstate
            changed = False
            for i in item:
                is_selected = (i.checkState() == Qt.CheckState.Checked)
                if not is_selected == self.settings.odml_selection.get_selection(key):
                    # change data model
                    self.settings.odml_selection.set_selection(key, is_selected)
                    changed = True
                    break


            if changed:    
                for j in item:
                    if is_selected:
                        
                        j.setBackground(QBrush(selected_color)) # green
                        j.setCheckState(Qt.Checked)
                    else:
                        j.setBackground(QBrush(deselected_color)) # red
                        j.setCheckState(Qt.Unchecked)

        self.model.blockSignals(False)
        # hacky but works...
        self.hide()
        self.show()
             
