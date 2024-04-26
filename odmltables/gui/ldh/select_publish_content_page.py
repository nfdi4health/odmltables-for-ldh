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
from PyQt5.QtGui import QBrush, QColor

from .data.odmlwithselection import OdmlTableWithSelection

#from ldh.odml_table_with_selection import OdmlTableWithSelection
from odmltables.gui.pageutils import QIWizardPage, clearLayout, shorten_path

    

class SelectContentPage(QIWizardPage):


    prop_path_tree_item_map = {}


    def __init__(self, parent=None):
        super(SelectContentPage, self).__init__(parent)

        self.odmltreeheaders = ['Content',
                                'Value', 'DataUncertainty', 'DataUnit',
                                'odmlDatatype', 'PropertyName', 'PropertyDefinition',
                                'SectionName', 'SectionType',
                                'SectionDefinition']

        self.setTitle("Select data fields for sharing")
        self.setSubTitle("Use the checkboxes to select the data fields you want to share.")

        self.search_words = []
        self.search_prop_words = {}
        self.prop_names = []
        self.max_searchwords = 3
        self.max_searchtypes = 3
        self.list_results = []

        hbox = Qtw.QVBoxLayout(self)

        # set up Search words
        frame_search = Qtw.QFrame(self)
        frame_search.setFrameShape(Qtw.QFrame.StyledPanel)
        frame_search.setMinimumHeight(600)
        frame_search.setSizePolicy(Qtw.QSizePolicy.Expanding,
                                          Qtw.QSizePolicy.Expanding)
        self.vbox_search = Qtw.QVBoxLayout()
        frame_search.setLayout(self.vbox_search)

        # Title
        searchlabel = Qtw.QLabel('Select Fields to Share')
        searchlabel.setStyleSheet('font: bold; font-size: 14pt')
        self.vbox_search.addWidget(searchlabel)


        ###########################
        # TREE REPRESENTATION FRAME
        frame_treerepresentation = Qtw.QFrame(self)
        frame_treerepresentation.setFrameShape(Qtw.QFrame.StyledPanel)
        vbox_treerepresentation = Qtw.QVBoxLayout()
        frame_treerepresentation.setLayout(vbox_treerepresentation)
        frame_treerepresentation.setSizePolicy(Qtw.QSizePolicy.Expanding,
                                               Qtw.QSizePolicy.Expanding)

        self.odmltree = Qtw.QTreeWidget()
        self.odmltree.setColumnCount(2)
        self.odmltree.setHeaderLabels(self.odmltreeheaders)
        self.odmltree.setSelectionMode(3)
        self.odmltree.setMinimumWidth(500)
        self.odmltree.setSizePolicy(Qtw.QSizePolicy.Expanding,
                                    Qtw.QSizePolicy.Expanding)

        columnwidths = [50] * len(self.odmltreeheaders)
        columnwidths[0:3] = [250, 100, 100]
        [self.odmltree.setColumnWidth(i, w) for i, w in enumerate(columnwidths)]

        vbox_treerepresentation.addWidget(self.odmltree)

        splitterv = Qtw.QSplitter(Qt.Vertical)
        splitterv.addWidget(frame_search)

        splitter2 = Qtw.QSplitter(Qt.Horizontal)
        splitter2.addWidget(splitterv)
        splitter2.addWidget(frame_treerepresentation)

        hbox.addWidget(splitter2)
        self.setLayout(hbox)


    def initializePage(self):
        #self.update_attributes()

        self.load_odml()
        self.odmltree.expandToDepth(0)
        


    # interface in gui (see http://lxml.de/xpathxslt.html)
    def load_odml(self):
        # loading odml file
        self.table = OdmlTableWithSelection()
        self.settings.set_odml_selection(self.table)

        # loading input file
        if os.path.splitext(self.settings.input_file)[1] in ['.odml']:
            self.table.load_from_file(self.settings.input_file)
        else:
            raise ValueError('Unknown input file extension "%s"'
                             '' % os.path.splitext(self.settings.input_file)[1])

        self.update_tree(self.table)


    def update_tree(self, table):
        self.odmltree.clear()
        self.create_sectiontree(self.odmltree, table)
        self.create_proptree(self.odmltree, table)

        self.odmltree.expandToDepth(0)

    def create_sectiontree(self, tree, table):
        sections = {prop['Path'].strip('/').split(':')[0]: ['', '', '', '', '', '',
                                               prop['Path'].split(':')[0].split('/')[-1],
                                               prop['SectionType'],
                                               prop['SectionDefinition']]
                    for prop in table._odmldict}

        self.replace_Nones(sections)
        for sec in sorted(sections):
            sec_names = sec.split('/')
            parent_sec = tree.invisibleRootItem()
            for i in list(range(len(sec_names))):
                child = self.find_child(parent_sec, sec_names[i])
                if child:
                    parent_sec = child
                else:
                    new_sec = Qtw.QTreeWidgetItem(parent_sec, [sec_names[i]] +
                                                  list(sections[sec]))
                    
                    parent_sec = new_sec

    def create_proptree(self, tree, table):

        props = {prop['Path'].strip('/').replace(':', '/'):
                     [prop['Value'],
                      prop['DataUncertainty'],
                      prop['DataUnit'],
                      prop['odmlDatatype'],
                      prop['Path'].split(':')[-1],
                      prop['PropertyDefinition'],
                         '', '', '']
                 for prop in table._odmldict}

        self.replace_Nones(props)

        for prop in props:
            prop_path = prop.split('/')
            parent_sec = tree.invisibleRootItem()
            for i in list(range(len(prop_path))):
                child = self.find_child(parent_sec, prop_path[i])
                if child:
                    parent_sec = child
                else:    
                    values = copy.deepcopy(props[prop][0])
                    tmp_prop = props[prop]
                    prop_name = prop_path[i]
                    if not prop_name in self.prop_names:
                        if tmp_prop[3] in ['string', 'float', 'int', 'url']:
                            self.prop_names.append(prop_name)
                        elif tmp_prop[3] == 'bool':
                            if not prop_name + " (true/false)" in self.prop_names:
                                self.prop_names.append(prop_name + " (true/false)")
                    for val in values:
                        tmp_prop[0] = str(val)
                        # add 
                        if table.get_selection(prop):
                            temp_item = Qtw.QTreeWidgetItem(parent_sec, [prop_name] + tmp_prop)
                            temp_item.setCheckState(0, Qt.CheckState.Checked)
                            self.prop_path_tree_item_map[prop] = temp_item
                        else:
                            temp_item = Qtw.QTreeWidgetItem(parent_sec, [prop_name] + tmp_prop)
                            temp_item.setCheckState(0, Qt.CheckState.Unchecked)
                            self.prop_path_tree_item_map[prop] = temp_item
 
                        
                        prop_name = ''
                        tmp_prop = [''] * len(tmp_prop)

        tree.itemChanged.connect(self.updateCheckedStatus)
            

    def updateCheckedStatus(self):
        # just redo all checked states for all items 
        for key, item in self.prop_path_tree_item_map.items():
            if item.checkState(0) == Qt.CheckState.Checked:
                self.table.set_selection(key, True)
            elif item.checkState(0) == Qt.CheckState.Unchecked:
                self.table.set_selection(key, False)
        self.odmltree.blockSignals(False)
        self.settings.set_odml_selection(self.table)

    def replace_Nones(self, data_dict):
        for value_list in list(data_dict.values()):
            for i in list(range(len(value_list))):
                if value_list[i] == None:
                    value_list[i] = ''

    def find_child(self, tree_sec, child_name):
        i = 0
        result = None
        while i < tree_sec.childCount():
            if tree_sec.child(i).text(0) == child_name:
                result = tree_sec.child(i)
                break
            i += 1

        return result