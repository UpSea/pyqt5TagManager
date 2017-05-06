#!/usr/bin/env python
# -*- coding: utf-8 -*-

from TagTreeItem import TagTreeItem
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt


class TagColorHelper:

    def __init__(self):
        self._counter = {}
        self._tags = []
        self._white = QColor(Qt.white)

    def init(self, root):
        assert (root, TagTreeItem), 'root must be an TagTreeItem'
        self.clear()
        self.__walk_over_node(root)
        self._tags = list(self._counter.keys())

    def add_new(self, tag_name):
        assert isinstance(tag_name, str), 'tag_name must be an str'
        _counter = self._counter
        if tag_name not in _counter:
            self._tags.append(tag_name)
        _counter[tag_name] = _counter[tag_name] + 1 if tag_name in _counter else 1

    def rename(self, old_tag_name, new_tag_name):
        assert isinstance(old_tag_name, str), 'old_tag_name must be an str'
        assert isinstance(new_tag_name, str), 'new_tag_name must be an str'
        _counter = self._counter
        if new_tag_name not in _counter:
            self._tags.append(new_tag_name)

        _counter[new_tag_name] = _counter[new_tag_name] + 1 if new_tag_name in _counter else 1
        _counter[old_tag_name] = _counter[old_tag_name] - 1 if old_tag_name in _counter else 0

    def color_for_tag(self, tag_name):
        assert isinstance(tag_name, str), 'tag_name must be an str'
        _counter = self._counter
        if _counter.get(tag_name, 0) > 1:
            # Это был бы лучший путь
            h = self._tags.index(tag_name)
            h = 10 * h
            return QColor.fromHsv(h, 70, 70)
            #Или этот:
            #return QColor.fromHsl(h, 39, 51)
            # c.setRgb(h, 28, 34)
        else:
            return self._white

    def __walk_over_node(self, node):
        '''
        a function called recursively, looking at all nodes beneath node
        Вложенная функция для поиска по вложенным элементам.
        Это фактически поиск по графу, "в глубину".
        Вызывается рекурсивно - сама себя.
        Красиво, но если будет слишком тормозить - переписать с рекурсии на цикл.

        Объявлено здесь, чтобы в других местах не мешало. По факту можно где угодно.
        '''
        # assert(isinstance(node, TreeItem), 'node должен быть объектом типа TreeItem!')
        _counter = self._counter
        tag_name = node.tag_as_str()
        _counter[tag_name] = _counter[tag_name] + 1 if tag_name in _counter else 1
        for child in node.childItems:
            self.__walk_over_node(child)

    def clear(self):
        self._counter.clear()
        self._tags.clear()
