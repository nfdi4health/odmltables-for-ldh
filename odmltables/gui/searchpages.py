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

from odmltables import odml_table
from .pageutils import QIWizardPage, clearLayout, shorten_path


class LoadFilePage(QIWizardPage):
    def __init__(self, parent=None, filename=None):
        super(LoadFilePage, self).__init__(parent)

        if filename is None:
            self.inputfilename = ''
        else:
            self.inputfilename = filename
        self.settings.register('inputfilename', self, useconfig=False)

        # Set up layout
        self.layout = Qtw.QVBoxLayout()
        self.setLayout(self.layout)

    def initializePage(self):

        self.setTitle("Select an input file")
        self.setSubTitle("Select the file you want to search")

        vbox = self.layout

        # Adding input part
        topLabel = Qtw.QLabel(self.tr("Choose a file to load"))
        topLabel.setWordWrap(True)
        vbox.addWidget(topLabel)

        # Add first horizontal box
        self.buttonbrowse = Qtw.QPushButton("Browse")
        self.buttonbrowse.clicked.connect(self.handlebuttonbrowse)
        self.inputfile = Qtw.QLabel(self.inputfilename)
        self.inputfile.setWordWrap(True)
        hbox1 = Qtw.QHBoxLayout()
        hbox1.addWidget(self.buttonbrowse)
        hbox1.addWidget(self.inputfile)

        hbox1.addStretch()
        vbox.addLayout(hbox1)

        vbox.addStretch()


    def handlebuttonbrowse(self):
        dlg = Qtw.QFileDialog()
        dlg.setNameFilters(["%s files (*%s)" % ('odml', '.odml'),
                            "%s files (*%s)" % ('xml', '.xml')])
        fn = self.settings.get_object('inputfilename')
        if fn:
            dlg.selectFile(fn)

        if dlg.exec_():
            self.inputfilename = str(dlg.selectedFiles()[0])

        self.settings.register('inputfilename', self, useconfig=False)
        self.inputfile.setText(shorten_path(self.inputfilename))


    def validatePage(self):

        if ((not self.settings.is_registered('inputfilename')) or
                (not self.settings.get_object('inputfilename'))):
            Qtw.QMessageBox.warning(self, 'Select an input file',
                                    'You need to select an input file to continue.')
            return 0

        elif self.settings.get_object('inputfilename').split('.')[-1] \
                not in ['xls', 'csv', 'odml', 'xml']:
            Qtw.QMessageBox.warning(self, 'Wrong input format',
                                    'The input file has to be an ".xls", ".csv", '
                                    '".odml" or ".xml" file.')
            return 0

        return 1

    def nextId(self):
        if (((self.inputfilename[-5:] != '.odml') or (self.inputfilename[-4:] != '.xml'))):
            return self.wizard().PageSearch



class SearchPage(QIWizardPage):
    def __init__(self, parent=None):
        super(SearchPage, self).__init__(parent)

        self.odmltreeheaders = ['Content',
                                'Value', 'DataUncertainty', 'DataUnit',
                                'odmlDatatype', 'PropertyName', 'PropertyDefinition',
                                'SectionName', 'SectionType',
                                'SectionDefinition']

        self.setTitle("Search your data")
        self.setSubTitle("Specify terms to search your "
                         "odmltables structure.")

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
        searchlabel = Qtw.QLabel('Search')
        searchlabel.setStyleSheet('font: bold; font-size: 14pt')
        self.vbox_search.addWidget(searchlabel)



        # set up search frame for words
        self.groupbox_searchwords = Qtw.QGroupBox(self.tr('Search Words'))
        self.groupbox_searchwords.setStyleSheet('QGroupBox {border: 1px solid '
                                               'gray; '
                                               'border-radius: 5px; '
                                               #'margin-top: '
                                               '0.5em}'
                                               'QGroupBox::title {'
                                               'subcontrol-origin: margin;'
                                               'left: 10px;'
                                               'padding: 0 3px 0 3px;}')

        self.grid_searchwords = Qtw.QGridLayout()
        self.grid_searchwords.setSizeConstraint(Qtw.QLayout.SetMinimumSize)
        self.groupbox_searchwords.setLayout(self.grid_searchwords)

        self.grid_searchwords.addWidget(Qtw.QLabel('Word'), 0, 1)

        add_button = Qtw.QPushButton('+')
        add_button.setFixedWidth(30)
        add_button.clicked.connect(self.update_searchwords)
        self.grid_searchwords.addWidget(add_button, 1, 0)

        self.vbox_search.addWidget(self.groupbox_searchwords)

        # START SEARCH BUTTON WORDS
        self.groupbox_applybutton = Qtw.QGroupBox()
        start_search_button = Qtw.QPushButton('Start Word Search')
        start_search_button.clicked.connect(self.start_search)
        vbox_startbutton = Qtw.QVBoxLayout()
        self.groupbox_applybutton.setLayout(vbox_startbutton)
        vbox_startbutton.addWidget(start_search_button)
        self.vbox_search.addWidget(self.groupbox_applybutton)

        self.vbox_search.addStretch()


        #### search types and word
        self.groupbox_searchprops = Qtw.QGroupBox(self.tr('Search Properties and Words'))
        self.groupbox_searchprops.setStyleSheet('QGroupBox {border: 1px solid '
                                                'gray; '
                                                'border-radius: 5px; '
                                                # 'margin-top: '
                                                '0.5em}'
                                                'QGroupBox::title {'
                                                'subcontrol-origin: margin;'
                                                'left: 10px;'
                                                'padding: 0 3px 0 3px;}')

        self.grid_searchprops = Qtw.QGridLayout()
        self.grid_searchprops.setSizeConstraint(Qtw.QLayout.SetMinimumSize)
        self.groupbox_searchprops.setLayout(self.grid_searchprops)

        self.grid_searchprops.addWidget(Qtw.QLabel('Word and Property'), 0, 1)

        add_button_prop = Qtw.QPushButton('+')
        add_button_prop.setFixedWidth(30)
        add_button_prop.clicked.connect(self.update_searchprops)
        self.grid_searchprops.addWidget(add_button_prop, 1, 0)

        self.vbox_search.addWidget(self.groupbox_searchprops)

        # START SEARCH BUTTON PROPS
        self.groupbox_applybutton_props = Qtw.QGroupBox()
        start_search_button_props = Qtw.QPushButton('Start Property Search')
        start_search_button_props.clicked.connect(self.start_search_props)
        vbox_startbutton_props = Qtw.QVBoxLayout()
        self.groupbox_applybutton_props.setLayout(vbox_startbutton_props)
        vbox_startbutton_props.addWidget(start_search_button_props)
        self.vbox_search.addWidget(self.groupbox_applybutton_props)

        self.vbox_search.addStretch()


        self.bresetsearch = Qtw.QPushButton('Reset search')
        self.bresetsearch.clicked.connect(self.remove_searchresults)
        self.vbox_search.addWidget(self.bresetsearch)# vbox_searchedwords

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

        self.groupbox_searchwords.setFixedHeight(235)

        self.grid_searchwords.itemAtPosition(1, 0).widget().click()

    def initializePage(self):
        #self.update_attributes()

        self.load_odml()

        self.settings.register('search', self.search_words)

        self.list_results = []

        self.odmltree.expandToDepth(0)

    def update_searchprops(self):
        sender = self.sender()
		# search for max 3 property + term combinations 
		# in a search 
        nattributes = 3
        idx = self.grid_searchprops.indexOf(sender)
        location = self.grid_searchprops.getItemPosition(idx)

        # in case of full line -> remove line
        if self.grid_searchprops.itemAtPosition(location[0], location[1] + 1):
            # deleting row
            tbr = [self.grid_searchprops.itemAtPosition(location[0], location[
                1] + i).widget() for i in list(range(3))]
            for widget in tbr:
                self.grid_searchprops.removeWidget(widget)
                widget.deleteLater()

            # moving lower widgets upward
            for row_id in list(range(location[0] + 1, nattributes + 1)):
                for col_id in list(range(nattributes)):
                    item = self.grid_searchprops.itemAtPosition(row_id, col_id)
                    widget = item.widget() if hasattr(item, 'widget') else None
                    if widget:
                        widx = self.grid_searchprops.indexOf(widget)
                        wloc = self.grid_searchprops.getItemPosition(widx)

                        self.grid_searchprops.removeWidget(widget)
                        self.grid_searchprops.addWidget(widget, wloc[0] - 1, wloc[1])

            #self.update_enabled_keys()

        # in case of an empty line -> add line
        else:
            # moving add button
            widx = self.grid_searchprops.indexOf(sender)
            wloc = self.grid_searchprops.getItemPosition(widx)
            if wloc[0] < self.max_searchwords + 1:
                self.grid_searchprops.removeWidget(sender)
                self.grid_searchprops.addWidget(sender, wloc[0] + 1, wloc[1])

                # adding row
                removebutton = Qtw.QPushButton('-')
                removebutton.setFixedWidth(30)
                removebutton.clicked.connect(self.update_searchprops)
                self.grid_searchprops.addWidget(removebutton, *wloc)


                keycb = Qtw.QComboBox()
                keycb.addItems(self.prop_names)
                #keycb.currentIndexChanged.connect(self.update_enabled_keys)

                self.grid_searchprops.addWidget(keycb, wloc[0], wloc[1] + 1)
                self.grid_searchprops.addWidget(Qtw.QLineEdit(), wloc[0],
                                                wloc[1] + 2)
            else:
                Qtw.QMessageBox.warning(self, 'Too many search words',
                                        'You can not define more than %s '
                                        'search words.' % (self.max_searchwords))

        self.layout().invalidate()



    def update_searchwords(self):
        sender = self.sender()
        nattributes = self._get_number_of_search_words()
        idx = self.grid_searchwords.indexOf(sender)
        location = self.grid_searchwords.getItemPosition(idx)

        # in case of full line -> remove line
        if self.grid_searchwords.itemAtPosition(location[0], location[1] + 1):
            # deleting row
            tbr = [self.grid_searchwords.itemAtPosition(location[0], location[
                1] + i).widget() for i in list(range(2))]
            for widget in tbr:
                self.grid_searchwords.removeWidget(widget)
                widget.deleteLater()

            # moving lower widgets upward
            for row_id in list(range(location[0] + 1, nattributes + 1)):
                for col_id in list(range(3)):
                    item = self.grid_searchwords.itemAtPosition(row_id, col_id)
                    widget = item.widget() if hasattr(item, 'widget') else None
                    if widget:
                        widx = self.grid_searchwords.indexOf(widget)
                        wloc = self.grid_searchwords.getItemPosition(widx)

                        self.grid_searchwords.removeWidget(widget)
                        self.grid_searchwords.addWidget(widget, wloc[0] - 1, wloc[1])

        # in case of an empty line -> add line
        else:
            # moving add button
            widx = self.grid_searchwords.indexOf(sender)
            wloc = self.grid_searchwords.getItemPosition(widx)
            if wloc[0] < self.max_searchwords + 1:
                self.grid_searchwords.removeWidget(sender)
                self.grid_searchwords.addWidget(sender, wloc[0] + 1, wloc[1])

                # adding row
                removebutton = Qtw.QPushButton('-')
                removebutton.setFixedWidth(30)
                removebutton.clicked.connect(self.update_searchwords)
                self.grid_searchwords.addWidget(removebutton, *wloc)

                self.grid_searchwords.addWidget(Qtw.QLineEdit(), wloc[0],
                                                wloc[1] + 1)

            else:
                Qtw.QMessageBox.warning(self, 'Too many search words',
                                        'You can not define more than %s '
                                        'search words.' % (self.max_searchwords))

        self.layout().invalidate()


    def _get_number_of_search_words(self):
        i = 1
        while self.grid_searchwords.itemAtPosition(i, 1):
            i += 1
        return i


    def _get_number_of_search_prop_words(self):
        i = 1
        while self.grid_searchprops.itemAtPosition(i, 2):
            i += 1
        return i

    def clear_input_search_words(self):
        for i in reversed(range(self.grid_searchwords.count())):
            curr_widget = self.grid_searchwords.itemAt(i).widget()
            if isinstance(curr_widget, Qtw.QLineEdit):
                self.grid_searchwords.itemAt(i).widget().setText('')

    def clear_input_search_props(self):
        for i in reversed(range(self.grid_searchprops.count())):
            curr_widget = self.grid_searchprops.itemAt(i).widget()
            if isinstance(curr_widget, Qtw.QLineEdit):
                self.grid_searchprops.itemAt(i).widget().setText('')


    def start_search(self):
		# start free text search by adding terms to search_words 
		# list and some error handling
        if len(self.list_results) > 0:
            Qtw.QMessageBox.warning(self, 'Error', \
                                    'The last search is still shown as a result.' \
                                    ' Please reset first before starting a new search.')
        else:
            self.search_words = []

            for i in list(range(1, self._get_number_of_search_words())):
                word = self.grid_searchwords. \
                    itemAtPosition(i, 1).widget().text()
                if not word == "":
                    if word not in self.search_words:
                        self.search_words.append(word)
                        continue
                    else:
                        Qtw.QMessageBox.warning(self, 'Word already exists',
                                                "The word already exists.")
                else:
                    Qtw.QMessageBox.warning(self, 'Error', 'There is an empty line.'\
                                        " Please enter a search word in each row to continue with search.")
                    self.search_words = []
                    return


            if len(self.search_words) < 1:
                Qtw.QMessageBox.warning(self, 'Error',\
                                        'There are no search words. ' \
                                        'Please enter a search word to start the search.')
            else:
                self.run_all_search_words()


    def start_search_props(self):
		# start search by adding properties and values
		# to search_prop_words dict and some error handling
        if len(self.list_results) > 0:
            Qtw.QMessageBox.warning(self, 'Error', \
                                    'The last search is still shown as a result.' \
                                    ' Please reset first before starting a new search.')
        else:
            self.search_prop_words = {}

            for i in list(range(1, self._get_number_of_search_prop_words())):
                prop = self.grid_searchprops.itemAtPosition(i, 1). \
                    widget().currentText()
                word = self.grid_searchprops. \
                    itemAtPosition(i, 2).widget().text()
                if not word == "":
                    if word not in self.search_prop_words:
                        self.search_prop_words[prop] = word
                        continue
                    else:
                        Qtw.QMessageBox.warning(self, 'Word already exists',
                                                "The word already exists.")
                else:
                    Qtw.QMessageBox.warning(self, 'Error', 'There is an empty line.'\
                                        " Please enter a search word in each row to continue with search.")
                    self.search_prop_words = {}
                    return


            if len(self.search_prop_words) < 1:
                Qtw.QMessageBox.warning(self, 'Error',\
                                        'There are no search words. ' \
                                        'Please enter a search word to start the search.')
            else:
                self.run_all_search_props()

    def remove_searchresults(self):
        self.search_words.clear()
        self.list_results = []
        self.clear_input_search_words()
        self.clear_input_search_props()
        self.update_tree(self.table)


    def run_all_search_words(self):
        # keeping filtered_table object and not substituting whole object to
        # be able to retrieve data from registered object
        self.searched_table._odmldict = copy.deepcopy(self.table._odmldict)


        for word in self.search_words:
            self.run_single_search(word)
        self.update_tree(self.searched_table)

    def run_single_search(self, search_word):
		# call odml_table function
        if self.searched_table == None:
            self.searched_table = copy.deepcopy(self.table)

        try:
            search_result = self.searched_table.search(self.search_words)
            self.search_words.remove(search_word)
        except Exception as e:
            message = e.message if hasattr(e, 'message') else (str(e))
            Qtw.QMessageBox.warning(self, 'Search Warning', message)
            raise e
        self._show_search_results(search_result)
        self.update_tree(self.searched_table)
        #self.search_words = []

    def run_all_search_props(self):

        self.searched_table_prop._odmldict = copy.deepcopy(self.table._odmldict)
        search_prop_words_copy = dict(self.search_prop_words)
        for prop in search_prop_words_copy:
            self.run_single_search_prop(prop, self.search_prop_words[prop])
        searched_table_prop_complete = self._show_complete_search_tree(self.searched_table_prop)
        self.update_tree(searched_table_prop_complete)


    def run_single_search_prop(self, search_prop, search_word):
		# call odml_table function
        if self.searched_table_prop == None:
            self.searched_table_prop = copy.deepcopy(self.table)

        try:
            search_result = self.searched_table_prop.search_prop(self.search_prop_words)
            self.search_prop_words.pop(search_prop)
        except Exception as e:
            message = e.message if hasattr(e, 'message') else (str(e))
            Qtw.QMessageBox.warning(self, 'Search Warning', message)
            raise e
        self._show_search_results(search_result)
        self.update_tree(self.searched_table_prop)

    # internal check
    def _show_search_results(self, search_result):
        self.list_results.append([result for result in search_result])

    def _show_complete_search_tree(self, search_table):
		# show complete experiment and not only entries
		# that contain the search terms 
        new_table = copy.deepcopy(self.table)
        if not search_table == None:
            exp_names_list = []
            for dic in search_table._odmldict:
                if len(dic["Path"].split('/')) > 4:
                    exp_names_list.append((dic["Path"].split('/')[4]))
                else:
                    exp_names_list.append((dic["Path"].split('/')[2]))
            experiment_names = list(set(exp_names_list))
        complete_dic = self.table._odmldict
        for entry in complete_dic:
            try:
                tmp_exp_name = entry["Path"].split('/')[4]
            except IndexError:
                tmp_exp_name = entry["Path"].split('/')[2]
            if not tmp_exp_name in experiment_names:
                new_table._odmldict.remove(entry)
            else:
                continue
        return new_table

    # TODO: check if this can also be done via XPath + provide xpath
    # interface in gui (see http://lxml.de/xpathxslt.html)
    def load_odml(self):
        # loading odml file
        self.table = odml_table.OdmlTable()
        self.settings.get_object('inputfilename')

        # loading input file
        if os.path.splitext(self.settings.get_object('inputfilename'))[1] == '.xls':
            self.table.load_from_xls_table(self.settings.get_object('inputfilename'))
        elif os.path.splitext(self.settings.get_object('inputfilename'))[1] == '.csv':
            self.table.load_from_csv_table(self.settings.get_object('inputfilename'))
        elif os.path.splitext(self.settings.get_object('inputfilename'))[1] in ['.odml', '.xml']:
            self.table.load_from_file(self.settings.get_object('inputfilename'))
        else:
            raise ValueError('Unknown input file extension "%s"'
                             '' % os.path.splitext(self.settings.get_object('inputfilename'))[1])

        self.update_tree(self.table)

        self.searched_table = copy.deepcopy(self.table)
        self.searched_table_prop = copy.deepcopy(self.table)
        self.settings.register('filtered_table', self.searched_table, useconfig=False)

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
                      prop['PropertyDefinition'], '', '', '']
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
                        Qtw.QTreeWidgetItem(parent_sec, [prop_name] + tmp_prop)
                        prop_name = ''
                        tmp_prop = [''] * len(tmp_prop)

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

