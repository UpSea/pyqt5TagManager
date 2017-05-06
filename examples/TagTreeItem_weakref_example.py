#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Weakref parent
Версия использования weakref для хранения ссылки на родителя.
Соответственно меняется и остальные обращения к self.parentItem
на self.parentItem() или на вызов self.parent().
Везде!
"""
import weakref


class TagTreeItem:
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    Элемент для дерева, чтобы можно было один вкладывать в другой.
    Будет храниться в treeModel (корневой) или в других TreeItem (обычные).
    '''

    def __init__(self, tag, parentItem=None):
        self.tag = tag
        self.parentItem = weakref.ref(parentItem)
        self.childItems = []
        self.id = 0

    def parent(self):
        return self.parentItem()

    def appendChild(self, item):
        assert isinstance(item, TagTreeItem), 'parentItem must be TagTreeItem'
        print('TagTreeItem.appendChilds')
        item.parentItem = weakref.ref(self)
        self.childItems.append(item)

    def appendChilds(self, items):
        print('TagTreeItem.appendChilds')
        for item in items:
            item.parentItem = weakref.ref(self)
            self.childItems.append(item)

    def insertChild(self, index, data):
        print('TagTreeItem.insertChild')
        data.parentItem = weakref.ref(self)
        self.childItems.insert(index, data)

    def insertChilds(self, index, data):
        print('TagTreeItem.insertChilds')
        for i, element in enumerate(data):
            element.parentItem = weakref.ref(self)
            self.childItems.insert(index+i, element)

    def row(self):
        '''Находим свой номер.
        Мы есть в списке родителя, а у нас ссылка на родителя'''
        parent = self.parent()
        if parent:
            return parent.childItems.index(self)
        return 0
