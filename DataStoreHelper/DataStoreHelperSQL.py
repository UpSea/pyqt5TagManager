#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Внимание! Чтобы всё работало корректно, все
TagTreeItem должны иметь уникальный идентификатор id!
Иначе работа алгоритмов будет некорректной
"""
try:
    from PyQt5 import QtSql, QtGui
except:
    from PySide import QtSql, QtGui

from collections import defaultdict
from TagTreeItem import TagTreeItem


class DataStoreHelperSQL:
    def __init__(self, fname=None):
        self.__fname = fname
        self.__error = ''
        self.__error_flag = False

    def last_error(self):
        return self.__error

    def has_error(self):
        return self.__error_flag

    def reset_error(self):
        self.__error = ''
        self.__error_flag = False

    def __get_connection(self, fname):
        assert isinstance(fname, str), ''
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName(fname)
        if not con.open():
            self.__error = "Cannot open database"
            self.__error_flag = True
            QtGui.QMessageBox.critical(None, QtGui.qApp.tr("Cannot open database"),
                                       QtGui.qApp.tr("Unable to establish a database connection.\n"
                                                     "This example needs SQLite support. Please read "
                                                     "the Qt SQL driver documentation for information "
                                                     "how to build it.\n\n" "Click Cancel to exit."),
                                       QtGui.QMessageBox.Cancel)
            return None
        # Тут мы уже открыли БД, и можем читать. По хорошему
        # мы должны учитывать: при раюоте с БД могут произойти ошибки
        return con

    def load(self, fname=None):
        __fname = fname or self.__fname
        assert isinstance(__fname, str), ''
        con = None
        root = None
        try:
            con = self.__get_connection(__fname)
            if con is not None:
                root = self.__loadNodesFlatR(con)
        except Exception as e:
            self.__error = str(e)
            self.__error_flag = True
            root = None
        finally:
            if con is not None:
                con.close()
        return root

    def store(self, root, fname=None):
        __fname = fname or self.__fname
        assert isinstance(__fname, str), ''
        con = None
        flag = False
        try:
            con = self.__get_connection(__fname)
            self.__storeNodesRecursive(root, con)
            flag = True
        except Exception as e:
            self.__error = str(e)
            self.__error_flag = True
            flag = False
        finally:
            if con is not None:
                con.close()
        return flag

    def __storeNodesRecursive(self, node, con):
        '''a function called recursively, looking at all nodes beneath node
        Вложенная функция для поиска по вложенным элементам.
        Это фактически обход по графу, "в глубину". Вызывается рекурсивно - сама себя.
        Красиво, но если будет слишком тормозить - переписать с рекурсии на цикл.
        '''
        assert isinstance(node, TagTreeItem), 'node должен быть объектом типа TreeItem!'
        query = QtSql.QSqlQuery(con)
        # Insert node
        query.prepare("INSERT INTO Tags(tag_name, parent_id) VALUES (:tag_name, :parent_id);")
        query.bindValue(":tag_name", node.tag_as_str())
        p = node.parent()
        if p is None:
            p_id = 0
        else:
            p_id = p.id
        query.bindValue(":parent_id", p_id)
        if not query.exec_():
            self.__error = "Can't execute: {}".format(query.lastError().text())
            self.__error_flag = True
        v = query.result().record().value('id')
        # Take id
        query.prepare("SELECT id FROM Tags WHERE parent_id=:parent_id AND tag_name=:tag_name;")
        query.bindValue(":tag_name", node.tag_as_str())
        query.bindValue(":parent_id", p_id)
        if not query.exec_():
            self.__error = "Can't execute: {}".format(query.lastError().text())
            self.__error_flag = True
        query.first()
        parent_id = query.value('id')
        node.id = parent_id
        for child in node.childItems:
            self.__storeNodesRecursive(child, con)
        return None

    def __loadNodes1(self, con):
        '''Попытка загрузки из БД'''

        def loadNodesForParentId(p_id):
            result = []
            query = QtSql.QSqlQuery(con)
            query.prepare("SELECT id, tag_name FROM Tags WHERE parent_id=:parent_id;")
            p_id = 0
            query.bindValue(":parent_id", p_id)
            if not query.exec_():
                self.__error = "Can't execute: {}".format(query.lastError().text())
                self.__error_flag = True
            query.first()
            while query.isValid():
                id = query.value('id')
                tag_name = query.value('tag_name')
                parent_id = query.value('parent_id')
                node = TagTreeItem(tag_name)
                node.id = id
                node.parent_id = parent_id
                result.append(node)
                query.next()
            return result

        def RecursiveAppendFromDict(node, nodes_dct):
            childs = nodes_dct.get(node.id, None)
            if childs is not None:
                node.appendChilds(childs)
                for child in childs:
                    RecursiveAppendFromDict(child, nodes_dct)

        query = QtSql.QSqlQuery(con)
        query.prepare("SELECT parent_id FROM Tags order by parent_id;")
        if not query.exec_():
            self.__error = "Can't execute: {}".format(query.lastError().text())
            self.__error_flag = True
        query.first()
        all_parents_id = set()
        all_nodes = {}
        # Получим список всех родительских идентификаторов
        while query.isValid():
            all_parents_id.add(query.value('parent_id'))
            query.next()
        # Получим словарь: ключ - родительский идентификатор, значение - список элементов
        for p_id in all_parents_id:
            all_nodes[p_id] = loadNodesForParentId(p_id)
        all_parents_id.clear()
        # Если здесь обнаружилась ошибка, значит нужно привести оба id к int
        root = all_nodes[0][0]
        RecursiveAppendFromDict(root, all_nodes)
        all_nodes.clear()
        return root

    def __loadNodesFlatR(self, con):
        '''Попытка "плоской" (загружаем всё в список, и потом формируем дерево) загрузки из БД'''

        def RecursiveAppendFromDict(node, nodes_dct):
            childs = nodes_dct.get(node.id, None)
            if childs is not None:
                node.appendChilds(childs)
                for child in childs:
                    RecursiveAppendFromDict(child, nodes_dct)

        nodes = defaultdict(list)
        query = QtSql.QSqlQuery(con)
        query.prepare("SELECT id, tag_name FROM Tags;")
        if not query.exec_():
            self.__error = "Can't execute: {}".format(query.lastError().text())
            self.__error_flag = True
        query.first()
        while query.isValid():
            id = query.value('id')
            tag_name = query.value('tag_name')
            parent_id = query.value('parent_id')
            node = TagTreeItem(tag_name)
            node.id = id
            node.parent_id = parent_id
            nodes[parent_id].append(node)
            query.next()
        # Если здесь обнаружилась ошибка, значит нужно привести оба id к int
        root = nodes[0][0]
        RecursiveAppendFromDict(root, nodes)
        nodes.clear()
        return root

    def __loadNodesRecursive(self, con):
        '''Рекурсивная версия загрузки из БД (завершена)'''

        def loadNodesForParentId(p_id):
            result = []
            query = QtSql.QSqlQuery(con)
            query.prepare("SELECT id, tag_name FROM Tags WHERE parent_id=:parent_id;")
            p_id = 0
            query.bindValue(":parent_id", p_id)
            if not query.exec_():
                self.__error = "Can't execute: {}".format(query.lastError().text())
                self.__error_flag = True
            query.first()
            while query.isValid():
                id = query.value('id')
                tag_name = query.value('tag_name')
                parent_id = query.value('parent_id')
                node = TagTreeItem(tag_name)
                node.id = id
                node.parent_id = parent_id
                result.append(node)
                query.next()
            return result

        def RecursiveLoad(node):
            '''Рекурсивная версия обход в глубину'''
            assert isinstance(node, TagTreeItem), 'node должен быть объектом типа TreeItem!'
            childs = loadNodesForParentId(node.id)
            node.appendChilds(childs)
            for child in childs:
                RecursiveLoad(child)

        # Если здесь обнаружилась ошибка, значит нужно привести оба id к int
        root = loadNodesForParentId(0)[0]
        RecursiveLoad(root)
        return root


