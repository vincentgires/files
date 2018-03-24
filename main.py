#!/usr/bin/env python3

'''
MODES (tab to switch?):
    - normal: navigation arrow + hjkl / action with keys
    - word navigation

FEATURES:
    - bookmarks
    - filter
    - custom actions (right click or toolbar)
    - terminal or shell execution
    - copy cut paste
    - preview on last column (text, image, video, sound)
    - sort folder before files
    - middle mouse navigation
'''

import sys
import os
import pathlib

from PyQt5 import QtCore, QtGui, QtWidgets


class FileManager():
    
    def __init__(self):
        self.files_model = FilesModel()
        self.files_model.set_dirpath(os.path.expanduser('~'))
        self.files_view = FilesView()
        self.files_view.setModel(self.files_model)
        self.files_view.show()
        
        #self.path_widget = PathWidget()
        #self.path_widget.show()
        #self.path_widget.path_edit.setText(os.path.expanduser('~'))
        #self.path_widget.path_edit.editingFinished.connect(self.changed_path)
    
    def changed_path(self):
        path = self.path_widget.path_edit.text()
        self.files_model.set_dirpath(path)


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
        if column == 0:
            return (
                    QtCore.Qt.ItemIsEditable |
                    QtCore.Qt.ItemIsEnabled |
                    QtCore.Qt.ItemIsSelectable
                )
        else:
            return QtCore.Qt.ItemIsEnabled
    
    def rowCount(self, index):
        return len(self.items)
    
    def columnCount(self, index):
        return 5
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                if section == 0:
                    return 'Name'
                elif section == 1:
                    return 'Size'
                elif section == 2:
                    return 'Modified'
                elif section == 3:
                    return 'Permissions'
                elif section == 4:
                    return 'Owner'
        
    def data(self, index, role):
        row = index.row()
        column = index.column()
        
        if role == QtCore.Qt.EditRole:
            if column == 0:
                return self.items[row]['name']
        
        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return self.items[row]['name']
            elif column == 1:
                return self.items[row]['size']
    
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        row = index.row()
        column = index.column()
        
        if role == QtCore.Qt.EditRole:
            if column == 0:
                self.items[row]['name'] = value
                self.dataChanged.emit(index, index)
                return True
            
        return False
    
    def set_dirpath(self, dirpath):
        
        if os.path.isdir(dirpath):
            if os.access(dirpath, os.R_OK):
                list_items = os.listdir(dirpath)
                list_items.sort()
                
                items = []
                for i in list_items:
                    
                    path = os.path.join(dirpath, i)
                    if os.path.isfile(path):
                        stat = os.stat(path)
                        size = os.path.getsize(path)
                    elif os.path.isdir(path):
                        nbr_items = len(os.listdir(path))
                        text = 'items' if nbr_items > 1 else 'item'
                        size = '{} {}'.format(nbr_items, text)
                    else:
                        size = '--'
                        
                    items.append(
                        {
                            'name':i,
                            'size':size,
                            
                        }
                    )
                
                self.set_items(items)
                
            else:
                print('No right access')
    
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
