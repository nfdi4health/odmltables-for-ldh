# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 12:58:23 2016

@author: zehl
"""

import argparse
import sys

from PyQt5.QtWidgets import QApplication

from .searchpages import (LoadFilePage, SearchPage)
from .settings import Settings
from .wizutils import OdmltablesWizard


class SearchWizard(OdmltablesWizard):
    NUM_PAGES = 3

    (PageLoadFile, PageSearch, PageSaveFile) = list(range(NUM_PAGES))

    def __init__(self, parent=None, filename=None):
        super(SearchWizard, self).__init__('Search Wizard', parent)
        settings = Settings(self.settingsfile)

        if isinstance(filename, list):
            filename = filename[0]
        self.setPage(self.PageLoadFile, LoadFilePage(settings, filename))
        #self.setPage(self.PageCustomInputHeader,
         #            CustomInputHeaderPage(settings))
        self.setPage(self.PageSearch, SearchPage(settings))
        #self.setPage(self.PageSaveFile, SaveFilePage(settings))

        self.setStartId(0)

    def _createHelpMsgs(self):
        msgs = {}
        msgs[self.PageLoadFile] = self.tr(
            "Select an input file using the browser"
            " and choose your output file format.")

        # TODO: Add more help info
        msgs[self.NUM_PAGES + 1] = self.tr(
            "Sorry, for this page there is no help available.")
        return msgs


# main ========================================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, nargs=1,
                        help="odml file to load")
    args = parser.parse_args()
    app = QApplication(sys.argv)
    wiz = SearchWizard(filename=args.file)
    wiz.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
