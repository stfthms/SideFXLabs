# -*- coding: utf-8 -*-
# Copyright: (C) 2014 Bruno Ébé
# Author: Bruno Ébé | contact@brunoebe.com
# License: GNU Lesser General Public License v3.0 | https://www.gnu.org/licenses

"""
Module dealing with the widget's UI.

Copyright: (C) 2014 Bruno Ébé
Author: Bruno Ébé | contact@brunoebe.com
License:
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import

import os
import logging

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtUiTools

try:
    from . import model
    from . import proxymodel
except Exception as e:
    try:
        import model
        import proxymodel
    except (ImportError):
        pass

try:
    from importlib import reload
except ImportError:
    from imp import reload
reload(model)
reload(proxymodel)


class CustomLineEdit(QtWidgets.QLineEdit):
    """docstring for CustomLineEdit."""

    def __init__(self):
        super(CustomLineEdit, self).__init__()

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        self.setText(e.mimeData().text())


class UiLoader(QtUiTools.QUiLoader):
    def __init__(self, baseinstance):
        QtUiTools.QUiLoader.__init__(self, baseinstance)
        self.baseinstance = baseinstance

    def createWidget(self, class_name, parent=None, name=''):
        if parent is None and self.baseinstance:
            return self.baseinstance
        else:
            widget = QtUiTools.QUiLoader.createWidget(self, class_name, parent, name)
            if self.baseinstance:
                setattr(self.baseinstance, name, widget)
            return widget


class MainWidget(QtWidgets.QWidget):

    # create signals
    spreadsheetChanged = QtCore.Signal()

    def __init__(self, appModel, headerNames=None, nodepath="", parent=None):
        """ """
        super(MainWidget, self).__init__(parent)

        # initialize/get the logger
        self._logger = logging.getLogger(__name__)

        # define some variables
        if not headerNames:
            headerNames = ["Name", "Label", "Value", "Tags", "Path", "Show"]

        # define the application model to use
        self._appModel = appModel
        self._logger.debug("%s is using %s application model." % (__name__, self._appModel.name))

        # get the first selected node to build the spreadsheet
        if not nodepath:
            selectedNodes = self._appModel.selection()
            if selectedNodes:
                nodepath = selectedNodes[0]

        # define the model and its proxy model
        self._model = model.Model(self._appModel, headerNames, nodepath)
        self._proxyModel = proxymodel.ProxyModel(self._model)
        self._showname = False
        self._showlabel = True
        self._showdiffonly = False

        # define parent in case this widget is not part of a parent widget
        if not parent:
            self.setParent(self._appModel.mainQtWindow, QtCore.Qt.Window)

        # setup the UI
        self.setup_ui(nodepath)

        # some cosmetics
        self.resize(400, 600)
        self.centerWidget()

    def model():
        """ """
        def fget(self): return self._model
        return locals()
    model = property(**model())

    def showname():
        """ """
        def fget(self): return self._showname
        def fset(self, value):
            self._logger.debug("Set showname to \"%s\"." % value)
            self._showname = value
            self._proxyModel.showname = value # and set the proxymodel's attribute so it's available for filtering
        return locals()
    showname = property(**showname())

    def showlabel():
        """ """
        def fget(self): return self._showlabel
        def fset(self, value):
            self._logger.debug("Set showlabel to \"%s\"." % value)
            self._showlabel = value
            self._proxyModel.showlabel = value # and set the proxymodel's attribute so it's available for filtering
        return locals()
    showlabel = property(**showlabel())

    def showdiffonly():
        """ """
        def fget(self): return self._showdiffonly
        def fset(self, value):
            self._logger.debug("Set showdiffonly to \"%s\"." % value)
            self._showdiffonly = value
            self._proxyModel.showdiffonly = value # and set the proxymodel's attribute so it's available for filtering
        return locals()
    showdiffonly = property(**showdiffonly())

    def centerWidget(self):
        """ Centers the widget on screen. (source: https://stackoverflow.com/a/20244839) """
        frameGm = self.frameGeometry()
        centerPoint = self.parent().geometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def setup_ui(self, nodepath=""):
        """ """
        # build the ui
        # uifile = os.path.join(os.path.dirname(__file__), "ui/widget.ui")
        # UiLoader(self).load(uifile)
        # I could not figure out how to replace a promoted widget in the .ui file with the UiLoader()
        # So I build the entire widget manually

        # build the ui
        self.setWindowTitle(__name__.split(".")[-2].capitalize())

        # create the widgets
        self.uiLineEdit = CustomLineEdit()
        self.uiTableView = QtWidgets.QTableView()
        self.uiVerticalLayout = QtWidgets.QVBoxLayout()

        # configure the layout
        self.setLayout(self.uiVerticalLayout)
        self.uiVerticalLayout.addWidget(self.uiLineEdit)
        self.uiVerticalLayout.addWidget(self.uiTableView)
        self.uiVerticalLayout.setMargin(0)

        # configure the view
        self.uiTableView.setModel(self._proxyModel) # tell the view which model to display
        self.uiTableView.setShowGrid(False)
        self.uiTableView.setTabKeyNavigation(False)
        self.uiTableView.setAlternatingRowColors(True)
        self.uiTableView.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.uiTableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.uiTableView.setWordWrap(False)
        self.uiTableView.horizontalHeader().setStretchLastSection(True)
        self.uiTableView.horizontalHeader().setHighlightSections(True)
        self.uiTableView.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
        self.uiTableView.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        self.uiTableView.horizontalHeader().resizeSection(0, 200)
        self.uiTableView.horizontalHeader().resizeSection(1, 50)
        self.uiTableView.verticalHeader().setVisible(False)
        self.uiTableView.verticalHeader().setHighlightSections(True)
        self.uiTableView.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.uiTableView.verticalHeader().setDefaultSectionSize(16)
        self.uiTableView.verticalHeader().setMinimumSectionSize(10)

        # define a delegate to override the inherited color palette
        delegate = model.MyDelegate(self)
        self.uiTableView.setItemDelegate(delegate)

        # define how the proxy model should sort the view
        self._proxyModel.sort(0, QtCore.Qt.AscendingOrder)

        # add actions
        # self.uiTableView.addAction(self.actionRefresh)

        # define the refresh function to use (choose between self or parent)
        if hasattr(self.parent(), 'refresh'):
            # check whether the parent has a refresh() function and connect it
            refreshFunction = lambda: self.parent().refresh() # I need to use this lambda form to make sure I don't pass extra arguments from signals
        else:
            # otherwise connect the refresh() function of self
            refreshFunction = lambda: self.refresh() # I need to use this lambda form to make sure I don't pass extra arguments from signals

        # connect signals
        self.uiLineEdit.textChanged.connect(lambda: self.spreadsheetChanged.emit())   # a change in node path fields emits spreadsheetChanged
        self.model.dataChanged.connect(lambda: self.spreadsheetChanged.emit())      # a change in the model emits spreadsheetChanged
        self.spreadsheetChanged.connect(refreshFunction)                              # when spreadsheetChanged is triggered, refresh the spreadsheet
        # self.actionRefresh.triggered.connect(refreshFunction)               # when actionRefresh is triggered, refresh the spreadsheet

        # initialize uiLineEdit with the node path
        self.uiLineEdit.setText(nodepath)
        self.showdiffonly = False
        self.showlabel = True

    def closeEvent(self, event):
        """ Redefine closeEvent() function to add some logs and eventually file management before quitting the widget. """
        name = __name__.split('.')[-2].capitalize() # note: [-2] to get the name of the module above .ui
        self._logger.debug("Closing %s..." % (name))
        self.setParent(None)
        event.accept()
        self._logger.info("%s closed." % (name))

    def refresh(self, parmlist=None):
        """ Refresh the spreadsheet.
        It updates the node path and asks the model to refresh """
        # be careful when connecting this function with signals: use 'lambda: self.refresh(args, you, need)'
        # if not, it could pass some extra, unwanted, arguments.
        # for instance 'uiLineEdit.textChanged' will pass the text in the line edit field as parmlist.
        self._logger.debug("Refreshing spreadsheet %s" % self)
        self._model.nodePath = str(self.uiLineEdit.text())
        self._model.refresh(parmlist)
