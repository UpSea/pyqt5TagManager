#!/usr/bin/env python
# -*- coding: utf-8 -*-

from TagTreeItem import TagTreeItem
try:
    from PyQt5.QtGui import QColor
    from PyQt5.QtCore import Qt
except:
    from PySide.QtGui import QColor
    from PySide.QtCore import Qt


class TagColorHelper2:

    def __init__(self):
        self._counter = {}
        self._colors_dct = {}
        self._white = QColor(Qt.white)
        self._colors = (QColor(Qt.red), QColor(Qt.green), QColor(Qt.blue),
                        QColor(Qt.cyan), QColor(Qt.magenta), QColor(Qt.yellow),
                        QColor(Qt.lightGray), QColor(Qt.gray),
                        #QColor(Qt.darkRed), QColor(Qt.darkGreen), QColor(Qt.darkBlue),
                        #QColor(Qt.darkCyan), QColor(Qt.darkMagenta), QColor(Qt.darkYellow),
                        #QColor(Qt.darkGray)
                        )
        self._counter_i = 0
        self._max_index = len(self._colors)

    def _get_new_uniq(self):
        c = self._counter_i
        self._counter_i = (c + 1) % self._max_index
        return c

    def init(self, root):
        assert (root, TagTreeItem), 'root must be an TagTreeItem'
        self.clear()
        self.__walk_over_node(root)

    def add_new(self, tag_name):
        assert isinstance(tag_name, str), 'tag_name must be an str'
        _counter = self._counter
        if tag_name in _counter:
            c = _counter[tag_name]
            _counter[tag_name] = c + 1
            if c == 1:
                self._colors_dct[tag_name] = self._get_new_uniq()
        else:
            _counter[tag_name] = 1

    def rename(self, old_tag_name, new_tag_name):
        assert isinstance(old_tag_name, str), 'old_tag_name must be an str'
        assert isinstance(new_tag_name, str), 'new_tag_name must be an str'
        _counter = self._counter
        if old_tag_name in _counter:
            c = _counter[old_tag_name]
            _counter[old_tag_name] = c - 1
            _colors_dct = self._colors_dct
            if c == 1 and old_tag_name in _colors_dct:
                _colors_dct.pop(old_tag_name)
        else:
            _counter[old_tag_name] = 0
        self.add_new(new_tag_name)

    def color_for_tag(self, tag_name):
        assert isinstance(tag_name, str), 'tag_name must be an str'
        _counter = self._counter
        if _counter.get(tag_name, 0) > 1:
            # Это был бы лучший путь
            # h = self._tags.index(tag_name)
            # h = 10 * h
            #return QColor.fromHsv(h, 1, 1)
            #Или этот:
            #return QColor.fromHsl(h, 39, 51)
            # c.setRgb(h, 28, 34)
            # But...
            index = self._colors_dct[tag_name]
            return self._colors[index]
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
        tag_name = node.tag_as_str()
        self.add_new(tag_name)
        for child in node.childItems:
            self.__walk_over_node(child)

    def clear(self):
        self._counter.clear()
        self._colors_dct.clear()
        self._counter_i = 0
