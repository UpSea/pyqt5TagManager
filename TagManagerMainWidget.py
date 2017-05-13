#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

try:
    from PyQt5.QtCore import (QModelIndex, Qt, pyqtSlot, QSettings,
                              QPoint, QSize, QItemSelectionModel)
    from PyQt5.QtGui import QFont
    from PyQt5.QtWidgets import (QPushButton, QFontDialog,
                                 QWidget, QAbstractItemView,
                                 QApplication, QStyle,
                                 QTreeView, QHBoxLayout, QVBoxLayout, QMenu, QAction,
                                 QFileDialog, QMessageBox)
except:
    from PySide.QtCore import (QModelIndex, Qt, Slot as pyqtSlot, QSettings,
                              QPoint, QSize, QItemSelectionModel)
    from PySide.QtGui import QFont
    from PySide.QtWidgets import (QPushButton, QFontDialog,
                                 QWidget, QAbstractItemView,
                                 QApplication, QStyle,
                                 QTreeView, QHBoxLayout, QVBoxLayout, QMenu, QAction,
                                 QFileDialog, QMessageBox)

from ColorHelper.TagColorHelper import TagColorHelper
from ColorHelper.TagColorHelper2 import TagColorHelper2
from TagTreeItem import TagTreeItem
from TagTreeModel import TagTreeModel
from TagValidChecker import TagValidChecker

SETTINGS_LAST_FILENAME = 'settings/last_filename'
SETTINGS_WINDOW_SIZE = 'settings/window_size'
SETTINGS_WINDOW_POS = 'settings/window_pos'
SETTINGS_WINDOW_FONT_SIZE = 'settings/window_font_size'
SETTINGS_WINDOW_FONT_FAMILY = 'settings/window_font_family'

def get_store_helper_for_fname(fname):
    """Get helper for store or load tree data. Fabric method."""
    assert isinstance(fname, str), 'fname must ba an str!'
    helper = None
    if fname.endswith('.xml'):
        from DataStoreHelper.DataStoreHelperXML import DataStoreHelperXML
        helper = DataStoreHelperXML(fname)
    elif fname.endswith('.db') or fname.endswith('.sqlite'):
        from DataStoreHelper.DataStoreHelperSQL import DataStoreHelperSQL
        helper = DataStoreHelperSQL(fname)
    elif fname.endswith('.csv'):
        from DataStoreHelper.DataStoreHelperCSV import DataStoreHelperCSV
        helper = DataStoreHelperCSV(fname)
    return helper


def process_filename(fname):
    assert isinstance(fname, (str, None)), 'fname must ba an str or None!'
    if fname is None or fname != '':
        return fname
    elif fname.endswith('.xml'):
        return fname
    elif fname.endswith('.db') or fname.endswith('.sqlite'):
        return fname
    elif fname.endswith('.csv'):
        return fname
    return '{}.xml'.format(fname)


class TagManager(QWidget):
    def __init__(self, parent=None):
        super(TagManager, self).__init__(parent)
        # For save delete C++ backend
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Set data
        self._tag_checker = TagValidChecker()
        self._color_helper = TagColorHelper2()
        self._last_fname = os.getcwd() # Last opened file name
        self._file_filters = "XML (*.xml);;CSV (*.csv);;SQLITE (*.sqlite *.db)"
        # Create GUI
        self.createGUI()
        self.load_settings()
        # Auto load last tag file
        if os.path.exists(self._last_fname) and os.path.isfile(self._last_fname):
            self._helper_load_from_file_to_model(self._last_fname)

    def createGUI(self):
        root = TagManager.createSimpleTree()

        model = TagTreeModel(root, self._tag_checker, self._color_helper, parent=self)
        model.invalidValueSetted.connect(self.invalidValueSettedByUserToTreeViewModel)
        #model.dataChanged.connect(dataChanged)

        self.setMinimumSize(300, 150)
        self.setWindowTitle('My Tag Manager')
        layout = QVBoxLayout(self)
        ## Menu Layout
        menu_layout = QHBoxLayout(self)
        but_save = QPushButton('Save', self)
        but_save.setIcon(QApplication.style().standardIcon(QStyle.SP_DialogSaveButton))
        menu_layout.addWidget(but_save)
        but_save.clicked.connect(self.but_save_clicked)

        but_load = QPushButton('Load', self)
        but_load.setIcon(QApplication.style().standardIcon(QStyle.SP_DirOpenIcon))
        menu_layout.addWidget(but_load)
        but_load.clicked.connect(self.but_load_clicked)

        but_new_f = QPushButton('New tag collections', self)
        but_new_f.setIcon(QApplication.style().standardIcon(QStyle.SP_FileIcon))
        but_new_f.setToolTip('New tag collections')
        menu_layout.addWidget(but_new_f)
        but_new_f.clicked.connect(self.but_new_tree_clicked)
        layout.addLayout(menu_layout)
        ## Menu Layout END

        tv = QTreeView(self)
        tv.setDragDropMode(QAbstractItemView.InternalMove)
        tv.setDragEnabled(True)
        tv.setAcceptDrops(True)
        tv.setDropIndicatorShown(True)
        tv.setContextMenuPolicy(Qt.CustomContextMenu)
        tv.customContextMenuRequested.connect(self.customContextMenuRequestedForTreeView)

        tv.setModel(model)
        #tv.setAlternatingRowColors(True)
        layout.addWidget(tv)
        self._widget_tv = tv

        but = QPushButton('Remove Selected', self)
        but.setIcon(QApplication.style().standardIcon(QStyle.SP_TrashIcon))
        layout.addWidget(but)
        but.clicked.connect(self.but_remove_clicked)

        but_add = QPushButton('Add', self)
        layout.addWidget(but_add)
        but_add.clicked.connect(self.but_add_clicked)

        but_font = QPushButton('Set Font', self)
        layout.addWidget(but_font)
        but_font.clicked.connect(self.but_font_dialog_clicked)
        self.layout().deleteLater() # Remove default layout
        self.setLayout(layout)

    def _helper_set_font(self, font):
        assert isinstance(font, QFont), 'font must be an QFont'
        self.setStyleSheet("font-size:{}pt;font-family:{};".format(font.pointSize(), font.family()))
        self.setFont(font)

    def load_settings(self):
        """
        See https://evileg.com/ru/post/219/
        :return: 
        """
        settings = QSettings()
        self._last_fname = settings.value(SETTINGS_LAST_FILENAME, self._last_fname, type=str)
        # Store Window size and position
        self.resize(settings.value(SETTINGS_WINDOW_SIZE, self.size(), type=QSize))
        self.move(settings.value(SETTINGS_WINDOW_POS, self.pos(), type=QPoint))
        # Load current Font
        font_size = settings.value(SETTINGS_WINDOW_FONT_SIZE, 14, type=int)
        font_family = settings.value(SETTINGS_WINDOW_FONT_FAMILY, "Arial", type=str)
        font = QFont(font_family, font_size)
        self._helper_set_font(font)

    def store_settings(self):
        settings = QSettings()
        settings.setValue(SETTINGS_LAST_FILENAME, self._last_fname)
        # Load Window size and position
        settings.setValue(SETTINGS_WINDOW_SIZE, self.size())
        settings.setValue(SETTINGS_WINDOW_POS, self.pos())
        # Store Font
        font = self.font()
        settings.setValue(SETTINGS_WINDOW_FONT_SIZE, font.pointSize())
        settings.setValue(SETTINGS_WINDOW_FONT_FAMILY, font.family())
        # Sync t disk
        settings.sync()

    @staticmethod
    def createSimpleTree():
        """Create simple example tree for example"""
        root0 = TagTreeItem('A')
        root = TagTreeItem('root')
        root0.appendChild(root)
        data1 = TagTreeItem('tag1')
        data2 = TagTreeItem('tag2')
        root.appendChild(data1)
        root.appendChild(data2)
        data2.appendChild(TagTreeItem('tag3'))
        data2.appendChild(TagTreeItem('tag4'))
        return root0

    def closeEvent(self, event):
        """Вызывается при закрытии окна (виджета)
        Override Qt C++ function"""
        #safe remove model elements from memory!
        answ = QMessageBox.question(self, "Quite",
                                    'Do you want to exit?\nUnsaved data will be lost!',
                                    QMessageBox.Ok | QMessageBox.No)
        if answ == QMessageBox.No:
            event.ignore()
            return
        self._widget_tv.model().safe_clear_when_removed()
        self.store_settings()
        event.accept()

    @pyqtSlot()
    def but_remove_clicked(self):
        """Button Clicked Remove from tree"""
        print('=== but_remove_clicked')
        _tv = self._widget_tv
        index = _tv.currentIndex()
        _tv.model().removeRow(index.row(), index.parent())
        _tv.selectionModel().setCurrentIndex(QModelIndex(), QItemSelectionModel.NoUpdate)

    @pyqtSlot()
    def but_add_clicked(self):
        """Button Clicked Add new to tree"""
        _tv = self._widget_tv
        model = _tv.model()
        index = _tv.currentIndex()
        if not index:
            index = QModelIndex()
        model.insertRow(0, index)

    @pyqtSlot()
    def but_save_clicked(self):
        """Button Clicked Save to file"""
        fname = self._last_fname
        fname = QFileDialog.getSaveFileName(self, 'Save file', fname,
                                            self._file_filters)[0]
        fname = process_filename(fname)
        if fname is not None and fname != '':
            if os.path.exists(fname):
                answ = QMessageBox.question(self, "Warning!",
                                            'File {} already exists! Do you want to owerwrite?'.format(fname),
                                            QMessageBox.Ok | QMessageBox.No)
                if answ == QMessageBox.No:
                    return
            self._last_fname = fname
            helper = get_store_helper_for_fname(fname)
            if helper is None:
                QMessageBox.warning(self, "Warning!",
                                        "File {} can't be open (no format helper (decoder))".format(fname),
                                        QMessageBox.Ok)
                return
            model = self._widget_tv.model()
            root = model.get_tree_root()
            if helper.store(root) is False:
                print(helper.last_error())
                QMessageBox.warning(self, "Warning!",
                                    helper.last_error(),
                                    QMessageBox.Ok)
            print(helper.last_error())

    def _helper_load_from_file_to_model(self, fname):
        """Helper for load from files (2 used)"""
        assert isinstance(fname, str), 'fname must be an str!'
        helper = get_store_helper_for_fname(fname)
        if helper is None:
            QMessageBox.warning(self, "Warning!",
                                "File {} can't be open (no format helper (decoder))".format(fname),
                                QMessageBox.Ok)
            return
        root = helper.load(fname)
        if helper.has_error():
            print(helper.last_error())
            QMessageBox.warning(self, "Warning!",
                                helper.last_error(),
                                QMessageBox.Ok)
        else:
            model = self._widget_tv.model()
            new_model = TagTreeModel(root, self._tag_checker, self._color_helper, parent=self)
            new_model.invalidValueSetted.connect(self.invalidValueSettedByUserToTreeViewModel)
            self._widget_tv.setModel(new_model)
            model.safe_clear_when_removed()
            model.deleteLater()

    @pyqtSlot()
    def but_load_clicked(self):
        """Button Clicked Load from file"""
        fname = self._last_fname
        fname = QFileDialog.getOpenFileName(self, 'Open file', fname, self._file_filters)[0]
        if fname is not None and fname != '':
            self._last_fname = fname
            self._helper_load_from_file_to_model(fname)

    @pyqtSlot()
    def but_new_tree_clicked(self):
        """Button create new Tree tag collection"""
        answ = QMessageBox.question(self, "New tag collections",
                                    'All unsaved data will be lost!\nDo you want to continue?',
                                    QMessageBox.Ok | QMessageBox.No)
        if answ == QMessageBox.No:
            return
        root = TagManager.createSimpleTree()
        model = self._widget_tv.model()
        new_model = TagTreeModel(root, self._tag_checker, self._color_helper, parent=self)
        new_model.invalidValueSetted.connect(self.invalidValueSettedByUserToTreeViewModel)
        self._widget_tv.setModel(new_model)
        model.safe_clear_when_removed()
        model.deleteLater()

    @pyqtSlot()
    def but_font_dialog_clicked(self):
        """Button for set Font"""
        font, ok = QFontDialog.getFont(self.font())
        if ok:
            self._helper_set_font(font)

    @pyqtSlot(str)
    def invalidValueSettedByUserToTreeViewModel(self, message):
        QMessageBox.warning(self, 'Invalid data!', message, QMessageBox.Ok)

    @pyqtSlot(QPoint)
    def customContextMenuRequestedForTreeView(self, pos):
        menu = QMenu(self)
        removeAction = QAction("Remove", self)
        removeAction.triggered.connect(self.but_remove_clicked)
        newAction = QAction("Add new", self)
        newAction.triggered.connect(self.but_add_clicked)
        menu.addAction(removeAction)
        menu.addAction(newAction)
        menu.popup(self._widget_tv.viewport().mapToGlobal(pos))
