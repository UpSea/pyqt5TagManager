#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from PyQt5.QtCore import QVariant
except:
    from PySide.QtCore import QVariant


class TagTreeItem:
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    Элемент для дерева, чтобы можно было один вкладывать в другой.
    Будет храниться в treeModel (корневой) или в других TreeItem (обычные).
    '''

    def __init__(self, tag, parentItem=None):
        #assert isinstance(parentItem, (TagTreeItem, None)), 'parentItem must be TagTreeItem'
        assert isinstance(tag, (str, None)), 'tag must be str or None'
        self.tag = tag
        self.parentItem = parentItem
        self.childItems = []
        self.id = 0

    def tag_as_str(self):
        """Helper for color helper"""
        return self.tag

    def appendChild(self, item):
        assert isinstance(item, TagTreeItem), 'parentItem must be TagTreeItem'
        item.parentItem = self
        self.childItems.append(item)

    def appendChilds(self, items):
        for item in items:
            item.parentItem = self
            self.childItems.append(item)

    def insertChild(self, index, data):
        data.parentItem = self
        self.childItems.insert(index, data)

    def insertChilds(self, index, data):
        for i, element in enumerate(data):
            element.parentItem = self
            self.childItems.insert(index+i, element)

    def removeChild(self, row):
        # Конец функции  removeChildsNodes, но продоложение  removeNodeWithChildsModel.
        if row >= len(self.childItems) or row < 0:
            return
        child = self.childItems.pop(row)
        # Альтернатива
        # self.childItems[:row]+self.childItems[row+1:]
        TagTreeItem.removeNodeWithChildsNodes(child)

    def takeChild(self, row):
        """Take child and remove from parent"""
        if row >= len(self.childItems) or row < 0:
            return
        return self.childItems.pop(row)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def hasChilds(self):
        return len(self.childItems) > 0

    def moveChild(self, sourceRow, destRow):
        c = self.childItems
        t = c.pop(sourceRow)
        c.insert(destRow, t)
        return True

    def moveChilds(self, sourceRow, count, destRow):
        childs = self.childItems
        t = sourceRow + count
        addition = childs[sourceRow:t]
        array = childs[:sourceRow] + childs[t:]
        self.childItems = array[:destRow] + addition + array[destRow:]

    def columnCount(self):
        return 1

    def data(self, column):
        if self.tag is None:
            # Обрабатываем случай, когда наш элемент корневой
            # вершина иерархии
            if column == 0:
                return QVariant()
            if column == 1:
                return QVariant("")
        else:
            # Обычный, вложенный элемент
            if column == 0:
                return QVariant(self.tag)
        # Возвращаем на всякий случай, страховка
        return QVariant()

    def setData(self, column, data):
        if self.tag is None:
            return False
        else:
            # Обычный, вложенный элемент
            if column == 0:
                self.tag = data
                return True
        # Возвращаем на всякий случай, страховка
        return False

    def parent(self):
        return self.parentItem

    def row(self):
        '''Находим свой номер.
        Мы есть в списке родителя, а у нас ссылка на родителя'''
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

    def row_for_our_child(self, child_node):
        '''Индекс нашего потомка, особенно эффективен, если пересмотреть догику работы'''
        assert isinstance(child_node, TagTreeItem), 'child_node must be TagTreeItem'
        return self.childItems.index(child_node)

    def serialize(self):
        return self.tag

    def __repr__(self):
        return "< class 'TagTreeItem.TagTreeItem' {}>".format(repr(self.tag))

    def __str__(self):
        return str(self.tag)

    def __del__(self):
        print('Deleted TagTreeItem')

    @staticmethod
    def deserialize(data):
        assert isinstance(data, str), 'data must be str!'
        return TagTreeItem(data)

    @staticmethod
    def removeNodeWithChildsNodes(node):
        '''a function called recursively, looking at all nodes beneath node
        Вложенная функция для поиска по вложенным элементам.
        Это фактически обход по графу, "в глубину". Вызывается рекурсивно - сама себя.
        Красиво, но если будет слишком тормозить - переписать с рекурсии на цикл.

        Объявлено здесь, чтобы в других местах не мешало. По факту можно где угодно.
        '''
        assert isinstance(node, TagTreeItem), 'node должен быть объектом типа TreeItem!'
        for child in node.childItems:
            if child.childCount() > 0:
                TagTreeItem.removeNodeWithChildsNodes(child)
                # Начинается «обратный ход» из рекурсии (если не путаю — ведь вложенный
                # вызов removeChildsNodes уже завершился
                # Удаляем «вложенный элемент» где-то здесь
        node.childItems.clear()
        parent = node.parent()
        if parent is not None:
            # without this, removeChild raise error: node not in parent.childItems
            if node in parent.childItems:
                parent.childItems.remove(node)
        node.parentItem = None
        node.tag = None
        # Возможно присвоение None было лишним, но лучше лишнии операции, чем утечка
        return None

    def removeSelfWithChildsNodes(self):
        '''a function called recursively, looking at all nodes beneath node
        Вложенная функция для поиска по вложенным элементам.
        Это фактически обход по графу, "в глубину". Вызывается рекурсивно - сама себя.
        Красиво, но если будет слишком тормозить - переписать с рекурсии на цикл.

        Объявлено здесь, чтобы в других местах не мешало. По факту можно где угодно.
        '''
        TagTreeItem.removeNodeWithChildsNodes(self)
