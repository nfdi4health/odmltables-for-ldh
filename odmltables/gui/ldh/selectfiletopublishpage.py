import sys
import os
import subprocess

import PyQt5.QtGui as Qtg
import PyQt5.QtWidgets as Qtw
from PyQt5.QtCore import QSize, Qt

from odmltables import odml_table, odml_xls_table, odml_csv_table, xls_style
from odmltables.gui.pageutils import QIWizardPage, shorten_path
from odmltables.gui.wizutils import get_graphic_path


class SelectFileToPublishPage(QIWizardPage):
    def __init__(self, parent=None, filenames=None):
        super(SelectFileToPublishPage, self).__init__(parent)

        self.inputfilename = ''
        if filenames:
            if len(filenames) > 0:
                self.inputfilename = filenames[0]

        graphic_path = get_graphic_path()

        # Set up layout
        self.layout = Qtw.QVBoxLayout()
        self.setLayout(self.layout)

        self.setTitle("File Selection<br>")
        self.setSubTitle("Choose the odML file to merge, select the merge mode, and specify the save location.")

        vbox = self.layout

        # setting inputfile variables
        self.settings.set_input_file(self.inputfilename)

        # Adding primary input part
        topLabel = Qtw.QLabel(self.tr("Choose one odml file, that contains all information you want to publish"))
        topLabel.setWordWrap(True)
        vbox.addWidget(topLabel)

        # Add first horizontal box
        self.buttonbrowse1 = self.generate_toolbutton("Browse for odML \n"
                                                      "File to Publish", '')
        self.buttonbrowse1.clicked.connect(self.browse2open, 1)
        self.inputfile = Qtw.QLabel(self.inputfilename)
        self.inputfile.setWordWrap(True)
        hbox1 = Qtw.QHBoxLayout()
        hbox1.addWidget(self.buttonbrowse1)
        hbox1.addWidget(self.inputfile)

        hbox1.addStretch()
        vbox.addLayout(hbox1)
        vbox.addStretch()


    def generate_toolbutton(self, text, graphic_name):
        graphic_path = get_graphic_path()
        button = Qtw.QToolButton()
        button.setText(self.tr(text))
        button.setIcon(Qtg.QIcon(os.path.join(graphic_path, graphic_name)))
        button.setIconSize(QSize(60, 60))
        button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        button.setFixedWidth(200)

        return button


    def browse2open(self):
        sender = self.sender()
        if sender == self.buttonbrowse1:
            input_id = 1
        elif sender == self.buttonbrowse2:
            input_id = 2
        else:
            raise ValueError('Wrong browser.')

        self.expected_extension = '.odml'
        self.accepted_extensions = ['.odml']

        dlg = Qtw.QFileDialog()
        dlg.setNameFilter("odML (*.odml)")
        dlg.setFileMode(Qtw.QFileDialog.AnyFile)
        dlg.setAcceptMode(Qtw.QFileDialog.AcceptOpen)
        dlg.setLabelText(Qtw.QFileDialog.Accept, "Open")
        dlg.setDefaultSuffix(self.expected_extension.strip('.'))

        dir = None
        if self.settings.input_file:
            dir = self.settings.input_file
        if dir:
            dlg.setDirectory(os.path.dirname(dir))

        if dlg.exec_():
            inputname = str(dlg.selectedFiles()[0])
            if ((os.path.splitext(inputname)[1] not in self.accepted_extensions) and
                    (os.path.splitext(inputname)[1] != '')):
                Qtw.QMessageBox.warning(self, 'Wrong file format',
                                        'The input file format is supposed to be "%s",'
                                        ' but you selected "%s"'
                                        '' % (self.accepted_extensions,
                                              os.path.splitext(inputname)[1]))
            else:
                
                self.settings.set_input_file(inputname)


    def validatePage(self):
        return 1

    