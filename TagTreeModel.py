#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from PyQt5.QtCore import (QModelIndex, QVariant, Qt,
                              QAbstractItemModel,
                              pyqtSlot, pyqtSignal)
except:
    from PySide.QtCore import (QModelIndex, QVariant, Qt,
                          QAbstractItemModel,
                          Slot as pyqtSlot, Signal as pyqtSignal)

from TagTreeItem import TagTreeItem

HORIZONTAL_HEADERS = ("Tag name",)


class TagTreeModel(QAbstractItemModel):
    '''
    a model to display a tag
    '''
    invalidValueSetted = pyqtSignal(str)

    def __init__(self, tree=None, tagValidChecker=None, tagColorHelper=None, parent=None):
        super(TagTreeModel, self).__init__(parent)
        # Создаём корень, вершину иерархии (скорее всего будет невидимой)
        # служебный элемент
        self.rootItem = tree if tree else TagTreeItem("Root")
        # See http://www.qtcentre.org/threads/46896-Hide-Parent-and-show-only-children-in-QTreeView
        # for setRootIndex manually
        #self.rootItem.appendChild(tree)
        self._tag_valid_checker = tagValidChecker
        self._default_tag_name = 'Default tag'
        if tree:
            tagColorHelper.init(tree)
        self._color_helper = tagColorHelper

    def get_tree_root(self):
        return self.rootItem

    def set_tree_root(self, root):
        assert isinstance(root, TagTreeItem), 'root must be TagTreeItem'
        self.rootItem = root
        self._color_helper.clear()
        self._color_helper.init(root)

    def flags(self, index):
        # Чтобы можно было редактировать данные в ячейке
        # по двойному или одинарному клику
        # Запретим перемещать элементы, имеющие наследников
        if self.itemForIndex(index).hasChilds():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDropEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | \
               Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    def columnCount(self, parent=None):
        assert isinstance(parent, QModelIndex), 'index должен быть объектом типа QModelIndex!'
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)

    def data(self, index, role=Qt.DisplayRole):
        assert isinstance(index, QModelIndex), 'index должен быть объектом типа QModelIndex!'
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return item.data(index.column())
        if role == Qt.ToolTipRole:
            return item.data(index.column())
        if role == Qt.BackgroundColorRole and self._color_helper:
            return self._color_helper.color_for_tag(item.tag_as_str())
        return QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        '''Для редактирования'''
        assert isinstance(index, QModelIndex), 'index должен быть объектом типа QModelIndex!'
        if not index.isValid():
            return False
        item = index.internalPointer()
        if self._tag_valid_checker:
            if not self._tag_valid_checker.check(value):
                self.invalidValueSetted.emit(self._tag_valid_checker.message())
                return False
        if self._color_helper:
            self._color_helper.rename(item.tag_as_str(), value)
        flag = item.setData(index.column(), value)
        if flag:
            self.dataChanged.emit(index, index)
            return flag
        return False

    def headerData(self, column, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(HORIZONTAL_HEADERS[column])
        return QVariant()

    def index(self, row, column, parent=None):
        parent = parent if parent else QModelIndex()
        assert isinstance(parent, QModelIndex), 'parent должен быть объектом типа QModelIndex!'
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent1(self, index):
        assert isinstance(index, QModelIndex), 'index должен быть объектом типа QModelIndex!'
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer() #More heavy: self.itemForIndex(index)
        if not node:
            return QModelIndex()
        parentItem = node.parent()
        #if parentItem == self.rootItem:
        if parentItem is None:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    ## Alternate version
    def parent(self, child):
        """The parent index of a given index."""
        node = self.itemForIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent()
        if parent is None:
            return QModelIndex()
        # Two variants of row use and overloading
        # Result are equals (результат и суть обоих подходов идентичны)
        #One way:
        row = parent.row()
        assert row != -1
        return self.createIndex(row, 0, parent)
        #Other way for example
        grandparent = parent.parent()
        if grandparent is None:
            return QModelIndex()
        row = grandparent.row_for_our_child(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)

    def rowCount(self, parent):
        assert isinstance(parent, QModelIndex), ''
        #if parent.column() > 0:
        #    return 0
        if not parent.isValid():
            p_item = self.rootItem
        else:
            p_item = parent.internalPointer()
        if p_item is None:
            return 0
        return p_item.childCount()

    def itemForIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return self.rootItem

    def searchModel_2(self, tag_name):
        '''
        get the modelIndex for a given appointment
        Эта функция добавлена автором только для себя, к 
        '''
        assert isinstance(tag_name, str), 'fname должно быть объектом типа str!'
        # И проверили, чтобы казуса не вышло, и наглядно видим, что получим.

        def searchNode(node):
            '''
            a function called recursively, looking at all nodes beneath node
            Вложенная функция для поиска по вложенным элементам.
            Это фактически поиск по графу, "в глубину".
            Вызывается рекурсивно - сама себя.
            Красиво, но если будет слишком тормозить - переписать с рекурсии на цикл.

            Объявлено здесь, чтобы в других местах не мешало. По факту можно где угодно.
            '''
            # assert(isinstance(node, TreeItem), 'node должен быть объектом типа TreeItem!')
            for child in node.childItems:
                # child.person может быть None
                if child.tag and tag_name == child.tag_as_str():
                    return self.createIndex(child.row(), 0, child)

                if child.childCount() > 0:
                    result = searchNode(child)
                    # Потому, что в худшем случае получаем None
                    if result:
                        return result
            # По хорошему надо возвращать QModelIndex()
            # и потом проверять на isValid()
            # Вот только памяти потребим... так что дешевле None - он памяти не занимает
            return None

        # Начнём поиск с корня self.rootItem
        return searchNode(self.rootItem)

    def find_GivenName_2(self, tag_name):
        '''Более красивая, и возможно даже более быстрая в каких-то случаях'''
        assert isinstance(tag_name, str), 'fname должно быть объектом типа str!'
        index = self.searchModel_2(tag_name)
        if index is not None:
            return index
        return QModelIndex()

    ###  IMPLEMENT QAbstractItemModel
    def insertRow(self, row, parent):
        return self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parentIndex):
        assert isinstance(parentIndex, QModelIndex), 'parentIndex must be an QModelIndex'
        p_item = self.itemForIndex(parentIndex)
        if p_item is None:
            return False
        self.beginInsertRows(parentIndex, row, row + count - 1)
        i = 0
        while i < count:
            self._color_helper.add_new(self._default_tag_name)
            child = TagTreeItem(self._default_tag_name)
            # p_item.insertChild(row+i, child)
            p_item.insertChild(row, child)
            i += 1
        self.endInsertRows()
        return True

    def removeRow(self, row, parentIndex):
        assert isinstance(parentIndex, QModelIndex), ''
        return self.removeRows(row, 1, parentIndex)

    def removeRows(self, row, count, parentIndex):
        assert isinstance(parentIndex, QModelIndex), ''
        # Интересный коммент, возможно рекурсия внутри
        # def removeChild(self, row): была лишней
        # If you remove the row at index.row(), all of its children
        # will be removed automatically.
        self.beginRemoveRows(parentIndex, row, row+count-1)
        p_item = self.itemForIndex(parentIndex)
        for i in range(count):
            p_item.removeChild(row)
        self.endRemoveRows()
        return True

    def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):
        if not sourceParent.isValid() or not destinationParent.isValid():
            return False
        if destinationParent != sourceParent:
            return False
        p_s_item = sourceParent.internalPointer()
        p_d_item = destinationParent.internalPointer()
        self.beginMoveRows(sourceParent, sourceRow, sourceRow + count - 1, destinationParent, destinationChild)
        if p_s_item != p_d_item:
            for i in range(count):
                item = p_s_item.takeChild(sourceRow)
                p_d_item.insertChild(destinationChild+i, item)
        else:
            p_s_item.moveChilds(sourceRow, count, destinationChild)
        self.endMoveRows()
        #self.rowsMoved.emit(sourceParent, sourceRow, sourceRow + count - 1, destinationParent, destinationChild)
        return True

    def moveRow(self, sourceParent, sourceRow, destinationParent, destinationChild):
        return self.moveRows(sourceParent, sourceRow, 1, destinationParent, destinationChild)
    ############################
    # For Drag'n'Drop

    def getSerializedData(self, indexes):
        l = []
        for index in indexes:
            item = index.internalPointer()
            s = item.serialize()
            l.append(s)
        return ';'.join(l)

    def deSerializeData(self, data):
        l = []
        for ser_element in data.split(';'):
            item = TagTreeItem.deserialize(ser_element)
            l.append(item)
        return l

    def supportedDropActions(self):
        return Qt.MoveAction | Qt.CopyAction

    def mimeTypes(self):
        return ['text/xml']

    def mimeData(self, indexes):
        mimedata =super(TagTreeModel, self).mimeData(indexes)
        # The mimedata does not contain anything by default.
        mimedata.setText(self.getSerializedData(indexes))
        return mimedata

    def dropMimeData(self, mimedata, action, row, column, parentIndex):
        if action == Qt.IgnoreAction: return True
        if not mimedata.hasFormat('text/xml'):
            return False
        data = mimedata.text()
        items = self.deSerializeData(data)
        self.insertItems(row, items, parentIndex)
        return True

    def insertItems(self, row, items, parentIndex):
        parent = self.itemForIndex(parentIndex)
        self.beginInsertRows(parentIndex, row, row + len(items) - 1)
        if row == -1:
            parent.appendChilds(items)
        else:
            parent.insertChilds(row, items)
        self.endInsertRows()
        self.rowsInserted.emit(parentIndex, row, row + len(items) - 1)
        return True

    ######################################

    def safe_clear_when_removed(self):
        """Safe remove all data. Call when model deleted.
        Безопасная очистка данных, вызывать при удалении
        модели или закрытии окна/виджета.
        Без этого дерево тегов рискует остаться в памяти 
        (можно, конечно, и по хорошему нужно,
        попробовать сохранять в элементах 
        TagTreeItem ссылку на parent используя weakref.ref)"""
        # Or safe parent  reference in TagTreeItem to weakref.ref
        if self.rootItem is not None:
            self.rootItem.removeSelfWithChildsNodes()
            self.rootItem = None

    @pyqtSlot()
    def resetInternalData(self):
        '''Это могло быть удалено в Qt 5.0, но лучше подстраховаться.'''
        self.safe_clear_when_removed()
        if self._color_helper:
            self._color_helper.clear()

    ####################
    ## Just helpers
    def pathForIndex(self, index):
        """
        Path for index
        :param index: QModelIndex object
        :return: list of strings (str) (tag names)
        """
        assert isinstance(index, QModelIndex), 'index must be an QModelIndex'
        if not index.isValid():
            return []
        path = []
        thisIndex = index
        while thisIndex.isValid():
            path.insert(0, self.data(thisIndex))
            thisIndex = thisIndex.parent()
        return path


    def indexForPath(self, path):
        """
        Index for path
        :param path: list or tuple of str objects (tag names)
        :return: QModelIndex
        """
        assert isinstance(path, (list, tuple)), 'path must be an list ot tuple'

        def _indexForPath(parent, path2):
            if len(path2) == 0:
                return QModelIndex()
            row = 0
            parent_row_count = self.rowCount(parent)
            while row < parent_row_count:
                thisIndex = self.index(row, 0, parent)
                cp = path2[0]
                if self.data(thisIndex) == cp:
                    if len(path2) == 1:
                        return thisIndex
                    thisIndex = _indexForPath(thisIndex, path2[1:])
                    if thisIndex.isValid():
                        return thisIndex
                row += 1
            return QModelIndex()

        return _indexForPath(QModelIndex(), path)

