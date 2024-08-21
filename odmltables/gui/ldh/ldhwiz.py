# -*- coding: utf-8 -*-
"""
Created on Thus 14.03.2024

@author: melwes
"""

import argparse
import sys

from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import QRect, QSize
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
from .final_url_page import FinalURLPage

class LDHWizard(OdmltablesWizard):
    NUM_PAGES = 9

    (ConnectPage, SelectProjectPage, #SelectInvestigationStudyPage, 
     SelectFileToPublishPage, SelectContentPage, 
     SelectContentTableViewPage, SaveSelectionPage, #CollectionPage, 
     ProvideLinkPage,
     FinalPage, FinalURLPage
     ) = list(range(NUM_PAGES))

    def __init__(self, parent=None):
        super(LDHWizard, self).__init__('Local Data Hub', parent)
        settings = LDHSetting()

        self.setWizardStyle(self.ModernStyle)
        self.setOption(self.HaveHelpButton, True)

        # Set a fixed size for the entire wizard and disable resizing
        self.setFixedSize(800, 600)  # Adjust the size as necessary

        self.centerOnScreen()

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
        self.setPage(8, FinalURLPage(settings))

        self.setStartId(0)

        # Connect signal to resize method
        self.currentIdChanged.connect(self.adjustWindowSize)

    def centerOnScreen(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        x = int((screen.width() - size.width()) / 2)
        y = int((screen.height() - size.height()) / 2)
        self.move(x, y)

    def adjustWindowSize(self, id):
        # List of page IDs that should be maximized
        pages_to_maximize = [3, 4, 7]
        if id in pages_to_maximize:
            screen = QDesktopWidget().screenGeometry()
            self.setFixedSize(screen.width()-30, screen.height()-210)
            self.move(0, 0)  # Move to the top-left corner
        else:
            # Revert to the default fixed size
            self.setFixedSize(800, 600)
        
        self.centerOnScreen()


    def _createHelpMsgs(self):
        msgs = {}
        msgs[self.ConnectPage] = self.tr(
            "Enter the Local Data Hub (URL) for NFDI4HEALTH.\n"
            "Example: http://localhost:3000/ (for Local)\n"
            "Enter the API Token generated for access."
        )
        msgs[self.SelectProjectPage] = self.tr(
            "Select an existing project or create a new one."
        )
        msgs[self.SelectFileToPublishPage] = self.tr(
            "Browse and select an odML (Open MetaData Markup Language) file."
        )
        msgs[self.SelectContentPage] = self.tr(
            "Select the fields for final data extraction and preparation."
        )
        msgs[self.SelectContentTableViewPage] = self.tr(
            "View a summary and make further selections for data extraction."
        )
        msgs[self.SaveSelectionPage] = self.tr(
            "Save the output as an odML file and CSV."
        )
        msgs[self.ProvideLinkPage] = self.tr(
            "If the dataset is publicly published, please provide a link to it."
        )
        msgs[self.FinalPage] = self.tr(
            "View and edit the final summary or report of the entered information."
        )
        msgs[self.FinalURLPage] = self.tr(
            "View the URLs to the published files."
        )
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