#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Внимание! Чтобы всё работало корректно, все
TagTreeItem должны иметь уникальный идентификатор id!
Иначе работа алгоритмов будет некорректной
"""
import sys
import os
from TagTreeItem import TagTreeItem
try:
    from PyQt5 import QtWidgets, QtSql, QtGui
except:
    from PySide import QtWidgets, QtSql, QtGui


def createSimpleTree():
    root = TagTreeItem('root')
    root.id = 1
    data1 = TagTreeItem('tag1')
    root.id = 2
    data2 = TagTreeItem('tag2')
    root.id = 3
    root.appendChild(data1)
    root.appendChild(data2)
    t1 = TagTreeItem('tag3')
    t1.id = 4
    t2 = TagTreeItem('tag4')
    t1.id = 5
    data2.appendChild(t1)
    data2.appendChild(t2)
    return root


def storeNodes(node, con):
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
        print("Can't execute:{}".format(query.lastError().text()))
    v = query.result().record().value('id')
    print('V={}'.format(v))
    # Take id
    query.prepare("SELECT id FROM Tags WHERE parent_id=:parent_id AND tag_name=:tag_name;")
    query.bindValue(":tag_name", node.tag_as_str())
    query.bindValue(":parent_id", p_id)
    if not query.exec_():
        print("Can't execute:{}".format(query.lastError().text()))
    query.first()
    parent_id = query.value('id')
    node.id = parent_id
    for child in node.childItems:
        print('Child: {}'.format(child.tag_as_str()))
        storeNodes(child, con)
    return None

def loadNodes(con):
    '''Попытка загрузки из БД'''
    def loadNodesForParentId(p_id):
        result = []
        query = QtSql.QSqlQuery(con)
        query.prepare("SELECT id, tag_name FROM Tags WHERE parent_id=:parent_id;")
        p_id = 0
        query.bindValue(":parent_id", p_id)
        if not query.exec_():
            print("Can't execute:{}".format(query.lastError().text()))
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

    def Foo(node, nodes_dct):
        childs = nodes_dct.get(node.id, None)
        if childs is not None:
            node.appendChilds(childs)
            for child in childs:
                Foo(child, nodes_dct)

    query = QtSql.QSqlQuery(con)
    query.prepare("SELECT parent_id FROM Tags order by parent_id;")
    if not query.exec_():
        print("Can't execute:{}".format(query.lastError().text()))
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
    # Если здесь обнаружилась ошибка, значит нужно привести оба id к int
    root = all_nodes[0][0]
    Foo(root, all_nodes)
    return root


def loadNodes2(con):
    '''Попытка "плоской" (загружаем всё в список, и потом формируем дерево) загрузки из БД'''
    def Foo(node, nodes_dct):
        childs = nodes_dct.get(node.id, None)
        if childs is not None:
            node.appendChilds(childs)
            for child in childs:
                Foo(child, nodes_dct)

    from collections import defaultdict
    nodes = defaultdict(list)
    query = QtSql.QSqlQuery(con)
    query.prepare("SELECT id, tag_name FROM Tags;")
    if not query.exec_():
        print("Can't execute:{}".format(query.lastError().text()))
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
    Foo(root, nodes)
    return root

def loadNodesRecursive(con):
    '''Рекурсивная версия загрузки из БД (завершена)'''
    def loadNodesForParentId(p_id):
        result = []
        query = QtSql.QSqlQuery(con)
        query.prepare("SELECT id, tag_name FROM Tags WHERE parent_id=:parent_id;")
        p_id = 0
        query.bindValue(":parent_id", p_id)
        if not query.exec_():
            print("Can't execute:{}".format(query.lastError().text()))
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

    def Foo(node):
        '''Рекурсивная версия обход в глубину'''
        assert isinstance(node, TagTreeItem), 'node должен быть объектом типа TreeItem!'
        childs = loadNodesForParentId(node.id)
        node.appendChilds(childs)
        for child in childs:
            Foo(child)

    # Если здесь обнаружилась ошибка, значит нужно привести оба id к int
    root = loadNodesForParentId(0)[0]
    Foo(root)
    return root

def test(root):
    query = QtSql.QSqlQuery()
    query.prepare("INSERT INTO Tags(id, tag_name, parent_id) VALUES (:id, :tag_name, :parent_id);")
    query.bindValue(":tag_name", root.tag_as_str())
    query.bindValue(":parent_id", 0)
    # query.bindValue(":id", 1)
    if not query.exec_():
        print("Can't execute INSERT")
    # Take id for root
    query.prepare("SELECT id FROM Tags WHERE parent_id=:parent_id AND tag_name=:tag_name;")
    query.bindValue(":tag_name", root.tag_as_str())
    query.bindValue(":parent_id", 0)
    if not query.exec_():
        print("Can't execute SELECT")
    query.first()
    parent_id = query.value('id')
    print('Val: {}'.format(parent_id))

def main():
    fname = 'data.sqlite'
    if os.path.exists(fname):
        os.remove(fname)
    app = QtWidgets.QApplication(sys.argv)
    con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    con.setDatabaseName(fname)
    if not con.open():
        QtGui.QMessageBox.critical(None, QtGui.qApp.tr("Cannot open database"),
                                   QtGui.qApp.tr("Unable to establish a database connection.\n"
                                                 "This example needs SQLite support. Please read "
                                                 "the Qt SQL driver documentation for information "
                                                 "how to build it.\n\n" "Click Cancel to exit."),
                                   QtGui.QMessageBox.Cancel)
    # Тут мы уже открыли БД, и можем читать. По хорошему
    # мы должны учитывать: при раюоте с БД могут произойти ошибки
    try:
        query = QtSql.QSqlQuery()

        query.exec_("create table Tags(id integer primary key autoincrement, tag_name varchar(20), parent_id integer);")

        root = createSimpleTree()
        storeNodes(root, con)
    finally:
        con.close()

    return 0


if __name__ == '__main__':
    sys.exit(main())

