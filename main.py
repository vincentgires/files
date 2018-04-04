#!/usr/bin/env python3

'''
TODO
    - items as class instead of dict?
    - sort folder first and sort other columns

MODES (tab to switch?):
    - normal: navigation arrow + hjkl / action with keys
    - word navigation

FEATURES:
    - bookmarks
    - filter
    - custom actions (shortcut "a", right clic, or toolbar)
    - terminal or shell execution
    - copy cut paste
    - preview on last column (text, image, video, sound)
    - sort folder before files
    - middle mouse navigation
'''

import sys
import os
from pathlib import Path
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from enum import IntEnum
from pwd import getpwuid

class TableColumn(IntEnum):
    NAME = 0
    SIZE = 1
    MODIFIED = 2
    PERMISSIONS = 3
    OWNER = 4
    TYPE = 5

class PathItem():
    name = None
    size = None
    modified = None
    permissions = None
    owner = None
    itemtype = None
    
    def __init__(self):
        pass

def get_items_from_directory(dirpath):

    if not os.path.isdir(dirpath):
        return None
        
    if not os.access(dirpath, os.R_OK):
        print('No right access')
        return None
        
    items = []
    for i in os.listdir(dirpath):
        fullpath = os.path.join(dirpath, i)
        
        if not os.path.exists(fullpath):
            continue
        
        stat = os.stat(fullpath)
        
        if os.path.isfile(fullpath):
            size = stat.st_size
            itemtype = 'file'
        
        elif os.path.isdir(fullpath):
            if os.access(fullpath, os.R_OK):
                nbr_items = len(os.listdir(fullpath))
                text = 'items' if nbr_items > 1 else 'item'
                size = '{} {}'.format(nbr_items, text)
            
            else:
                size = '?'
            itemtype = 'folder'
        
        item = PathItem()
        item.name = i
        item.fullpath = fullpath
        item.size = size
        item.modified = stat.st_mtime
        item.permissions = stat.st_mode
        item.owner = getpwuid(stat.st_uid).pw_name
        item.itemtype = itemtype
        items.append(item)
        
    return items

def sort_files(items, folder_first=True, sort_attr='name'):
    
    if folder_first:
        folders = list(filter(lambda x: x.itemtype=='folder', items))
        folders.sort(key=lambda x: getattr(x, 'name'))
        files = list(filter(lambda x: x.itemtype!='folder', items))
        files.sort(key=lambda x: getattr(x, 'name'))
        items = folders + files
        
    else:
        items.sort(key=lambda x: getattr(x, 'name'))
    
    return items

class FileManager():
    
    def __init__(self):
        
        self.files_model = FilesModel()
        self.files_model.set_dirpath(os.path.expanduser('~'))
        self.files_view = FilesView()
        self.files_view.setModel(self.files_model)
        self.files_view.setSortingEnabled(True)
        self.files_view.sortByColumn(TableColumn.NAME.value,
                                     QtCore.Qt.AscendingOrder)
        
        self.path_widget = PathWidget()
        self.path_widget.path_edit.setText(os.path.expanduser('~'))
        self.path_widget.path_edit.editingFinished.connect(self.changed_path)
        
        self.main_widget = MainWidget()
        self.main_widget.path_widget = self.path_widget
        self.main_widget.files_widget = self.files_view
        self.main_widget.init_ui()
        self.main_widget.show()
    
    def changed_path(self):
        path = self.path_widget.path_edit.text()
        self.files_model.set_dirpath(path)


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.path_widget = None
        self.files_widget = None
        
    def init_ui(self):
        self.resize(750, 450)
        self.setWindowTitle('File Manager')
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.path_widget)
        layout.addWidget(self.files_widget)
        self.setLayout(layout)
        

class PathWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.path_edit = QtWidgets.QLineEdit('')
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.path_edit)
        self.setLayout(layout)


class FilesModel(QtCore.QAbstractTableModel):
    dirpath = str()
    items = list()
    
    def __init__(self, parent=None):
        super().__init__()
    
    def flags(self, index):
        row = index.row()
        column = index.column()
        if column == TableColumn.NAME:
            return (
                    QtCore.Qt.ItemIsEditable |
                    QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsSelectable
            )
        else:
            return (
                    QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsSelectable
            )
    
    def rowCount(self, index):
        return len(self.items)
    
    def columnCount(self, index):
        return 6
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                
                if section == TableColumn.NAME:
                    return 'Name'
                
                elif section == TableColumn.SIZE:
                    return 'Size'
                
                elif section == TableColumn.MODIFIED:
                    return 'Modified'
                
                elif section == TableColumn.PERMISSIONS:
                    return 'Permissions'
                
                elif section == TableColumn.OWNER:
                    return 'Owner'
                
                elif section == TableColumn.TYPE:
                    return 'Type'
        
    def data(self, index, role):
        row = index.row()
        column = index.column()
        
        if role == QtCore.Qt.EditRole:
            
            if column == TableColumn.NAME:
                return self.items[row].name
        
        if role == QtCore.Qt.DisplayRole:
            
            if column == TableColumn.NAME:
                return self.items[row].name
            
            elif column == TableColumn.SIZE:
                return self.items[row].size
            
            elif column == TableColumn.PERMISSIONS:
                return self.items[row].permissions
            
            elif column == TableColumn.MODIFIED:
                date = self.items[row].modified
                date = datetime.fromtimestamp(date)
                date = date.strftime('%Y-%m-%d %H:%M')
                return date
            
            elif column == TableColumn.OWNER:
                return self.items[row].owner
            
            elif column == TableColumn.TYPE:
                return self.items[row].itemtype
    
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        row = index.row()
        column = index.column()
        
        if role == QtCore.Qt.EditRole:
            
            if column == TableColumn.NAME:
                self.items[row].name = value
                self.dataChanged.emit(index, index)
                return True
            
        return False
    
    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        print(type(column))
        if column == TableColumn.NAME:
            self.items = sort_files(self.items)
        #else:
            #items.sort(key=lambda x: x['name'])
        
        if order == QtCore.Qt.DescendingOrder:
            self.items.reverse()
        
        self.layoutChanged.emit()
    
    def set_dirpath(self, dirpath):
        items = get_items_from_directory(dirpath)
        if items:
            self.set_items(items)
    
    def set_items(self, items):
        self.beginResetModel()
        self.items = items
        self.endResetModel()


class FilesView(QtWidgets.QTableView):
    
    def __init__(self, parent=None):
        super(FilesView, self).__init__(parent)
        self.verticalHeader().hide()
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    
    def showHeaderMenu( self, point ):
        print('showHeaderMenu')
        column = self.ui.tree.header().logicalIndexAt(point.x())

        # show menu about the column
        menu = QMenu(self)
        menu.addAction('Hide Column')

        menu.popup(header.mapToGlobal(pos))
    
    def contextMenuEvent(self, event):
        print('contextMenu')
        selection_model = self.selectionModel()
        indexes = selection_model.selection().indexes()
        index = indexes[-1]
        
        row = index.row()
        column = index.column()
        data = index.data()
        
        if column == 0:
            menu = QtWidgets.QMenu(self)
            mark_action = menu.addAction('Mark')
            mark_action.setCheckable(True)
            checked = False
            mark_action.setChecked(checked)
            action = menu.exec_(self.mapToGlobal(event.pos()))
            
            if action == mark_action:
                print(indexes, 'are marked')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    fm = FileManager()
    sys.exit(app.exec())
