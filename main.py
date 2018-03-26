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
from pathlib import Path
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets

TABLE_COLUMN = {
    'name':0,
    'size':1,
    'modified':2,
    'permissions':3,
    'owner':4
}

def get_items_from_directory(dirpath):
    path = Path(dirpath)

    if not path.is_dir():
        return None
        
    if not os.access(dirpath, os.R_OK):
        print('No right access')
        return None
        
    items = []
    for i in path.iterdir():
        if not i.exists():
            continue
        
        fullpath = i.absolute().as_posix()
        stat = i.stat()
        
        
        if i.is_file():
            size = stat.st_size
        
        elif i.is_dir():
            if os.access(fullpath, os.R_OK):
                nbr_items = len(list(i.iterdir()))
                text = 'items' if nbr_items > 1 else 'item'
                size = '{} {}'.format(nbr_items, text)
            
            else:
                size = '?'
        
        items.append(
            {
                'name':i.name,
                'size':size,
                'modified':stat.st_mtime,
                'permissions':stat.st_mode,
                'owner':i.owner()
            }
        )
        
    return items


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
        if column == TABLE_COLUMN['name']:
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
                
                if section == TABLE_COLUMN['name']:
                    return 'Name'
                
                elif section == TABLE_COLUMN['size']:
                    return 'Size'
                
                elif section == TABLE_COLUMN['modified']:
                    return 'Modified'
                
                elif section == TABLE_COLUMN['permissions']:
                    return 'Permissions'
                
                elif section == TABLE_COLUMN['owner']:
                    return 'Owner'
        
    def data(self, index, role):
        row = index.row()
        column = index.column()
        
        if role == QtCore.Qt.EditRole:
            
            if column == TABLE_COLUMN['name']:
                return self.items[row]['name']
        
        if role == QtCore.Qt.DisplayRole:
            
            if column == TABLE_COLUMN['name']:
                return self.items[row]['name']
            
            elif column == TABLE_COLUMN['size']:
                return self.items[row]['size']
            
            elif column == TABLE_COLUMN['permissions']:
                return self.items[row]['permissions']
            
            elif column == TABLE_COLUMN['modified']:
                date = self.items[row]['modified']
                date = datetime.fromtimestamp(date)
                date = date.strftime('%Y-%m-%d %H:%M')
                return date
            
            elif column == TABLE_COLUMN['owner']:
                return self.items[row]['owner']
    
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        row = index.row()
        column = index.column()
        
        if role == QtCore.Qt.EditRole:
            
            if column == TABLE_COLUMN['name']:
                self.items[row]['name'] = value
                self.dataChanged.emit(index, index)
                return True
            
        return False
    
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
