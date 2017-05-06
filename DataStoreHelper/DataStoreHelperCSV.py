#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Внимание! Чтобы всё работало корректно, все
TagTreeItem должны иметь уникальный идентификатор id!
Иначе работа алгоритмов будет некорректной
"""
import os
from TagTreeItem import TagTreeItem
from collections import defaultdict
import csv


class DataStoreHelperCSV:
    def __init__(self, delimeter=';',
                 quotechar='|',
                 quoting=csv.QUOTE_MINIMAL,
                 newline='',
                 fname=None):
        self.__fname = fname
        self.__error = ''
        self.__error_flag = False
        self.__delimeter = delimeter
        self.__quotechar = quotechar
        self.__quoting = quoting
        self.__newline = newline

    def last_error(self):
        return self.__error

    def has_error(self):
        return self.__error_flag

    def reset_error(self):
        self.__error = ''
        self.__error_flag = False

    def load(self, fname=None):
        __fname = fname or self.__fname
        assert isinstance(__fname, str), ''
        if not os.path.exists(fname):
            self.__error = "File don't exists!"
            return None
        try:
            root = None
            with open(__fname, newline='') as csvfile:
                treereader = csv.reader(csvfile,
                                        delimiter=self.__delimeter,
                                        quotechar=self.__quotechar)
                root = self.__loadNodesFlat(treereader)
            return root
        except Exception as e:
            self.__error = str(e)
            self.__error_flag = True
            return None

    def store(self, root, fname=None):
        __fname = fname or self.__fname
        assert isinstance(__fname, str), ''
        try:
            with open(__fname, 'w', newline=self.__newline) as csvfile:
                treewriter = csv.writer(csvfile,
                                        delimiter=self.__delimeter,
                                        quotechar=self.__quotechar,
                                        quoting=self.__quoting)
                self.__storeNodesRecursive(root, treewriter)
            return True
        except Exception as e:
            self.__error = str(e)
            self.__error_flag = True
            return False

    def __storeNodesRecursive(self, node, csv_writer):
        '''a function called recursively, looking at all nodes beneath node
        Вложенная функция для поиска по вложенным элементам.
        Это фактически обход по графу, "в глубину". Вызывается рекурсивно - сама себя.
        Красиво, но если будет слишком тормозить - переписать с рекурсии на цикл.
        '''
        assert isinstance(node, TagTreeItem), 'node должен быть объектом типа TreeItem!'
        p = node.parent()
        if p is None:
            p_id = 0
        else:
            p_id = p.id
        csv_writer.writerow((node.id, node.tag_as_str(), p_id))
        for child in node.childItems:
            self.__storeNodesRecursive(child, csv_writer)
        return None

    def __loadNodesFlat(self, csv_reader):
        '''Попытка "плоской" (загружаем всё в список, и потом формируем дерево) загрузки из БД'''
        def RecursiveAppendFromDict(node, nodes_dct):
            childs = nodes_dct.get(node.id, None)
            if childs is not None:
                node.appendChilds(childs)
                for child in childs:
                    RecursiveAppendFromDict(child, nodes_dct)

        nodes = defaultdict(list)
        for row in csv_reader:
            id = int(row[0])
            tag_name = row[1]
            parent_id = int(row[2])
            node = TagTreeItem(tag_name)
            node.id = id
            node.parent_id = parent_id
            nodes[parent_id].append(node)
        root = nodes[0][0]
        RecursiveAppendFromDict(root, nodes)
        nodes.clear()
        return root
