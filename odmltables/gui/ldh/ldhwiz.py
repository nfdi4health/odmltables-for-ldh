# -*- coding: utf-8 -*-
"""
Created on Thus 14.03.2024

@author: melwes
"""

import argparse
import sys

from PyQt5.QtWidgets import QApplication
from odmltables.gui.settings import Settings
from odmltables.gui.wizutils import OdmltablesWizard
from .connectpage import ConnectPage
from .projectpages import SelectProjectPage
from .investigation_study_pages import SelectInvestigationStudyPage
from .selectfiletopublishpage import SelectFileToPublishPage
from .select_publish_content_page import SelectContentPage
from .select_publish_content_table_view import SelectContentTableViewPage
from .data.ldh_settings import LDHSetting
from .collectionpage import CollectionPage
from .save_selected_page import SaveSelectionPage
from .final_page import FinalPage
from .provide_link_page import ProvideLinkPage

class LDHWizard(OdmltablesWizard):
    NUM_PAGES = 8

    (ConnectPage, SelectProjectPage, #SelectInvestigationStudyPage, 
     SelectFileToPublishPage, SelectContentPage, 
     SelectContentTableViewPage, SaveSelectionPage, #CollectionPage, 
     ProvideLinkPage,
     FinalPage
     ) = list(range(NUM_PAGES))

    def __init__(self, parent=None):
        super(LDHWizard, self).__init__('Connect Wizard', parent)
        settings = LDHSetting()

        self.setWizardStyle(self.ModernStyle)
        self.setOption(self.HaveHelpButton, True)

         #            CustomInputHeaderPage(settings))
        self.setPage(0, ConnectPage(settings))
        self.setPage(1, SelectProjectPage(settings))
        #self.setPage(2, SelectInvestigationStudyPage(settings))
        self.setPage(2, SelectFileToPublishPage(settings))
        self.setPage(3, SelectContentPage(settings))
        self.setPage(4, SelectContentTableViewPage(settings))
        self.setPage(5, SaveSelectionPage(settings))
        #self.setPage(6, CollectionPage(settings))
        self.setPage(6, ProvideLinkPage(settings))
        self.setPage(7, FinalPage(settings))
        #self.setPage(self.PageSaveFile, SaveFilePage(settings))

        self.setStartId(0)

    def _createHelpMsgs(self):
        msgs = {}
        #msgs[self.ConnectPage] = self.tr(
        #    "Choose the Local Data hub you want to connect with"
        #    " and log in with your odMLtables user.")

        # TODO: Add more help info
        #msgs[self.NUM_PAGES + 1] = self.tr(
         #   "Get the ")
        return msgs


# main ========================================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, nargs=1,
                        help="odml file to load")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    wiz = LDHWizard(filename=args.file)
    wiz.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()