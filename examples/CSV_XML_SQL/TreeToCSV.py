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
import csv


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


def storeNodes(node, csv_writer):
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
        storeNodes(child, csv_writer)
    return None

def loadNodes2(csv_reader):
    '''Попытка "плоской" (загружаем всё в список, и потом формируем дерево) загрузки из БД'''

    def Foo(node, nodes_dct):
        childs = nodes_dct.get(node.id, None)
        if childs is not None:
            node.appendChilds(childs)
            for child in childs:
                Foo(child, nodes_dct)

    from collections import defaultdict
    nodes = defaultdict(list)
    for row in csv_reader:
        id = int(row[0])
        tag_name = row[1]
        parent_id = int(row[2])
        node = TagTreeItem(tag_name)
        node.id = id
        node.parent_id = parent_id
        nodes[parent_id].append(node)
    root=nodes[0][0]
    Foo(root, nodes)
    return root

def main():
    fname = 'Tree.csv'
    if os.path.exists(fname):
        os.remove(fname)
    root = createSimpleTree()
    with open(fname, 'w', newline='') as csvfile:
        treewriter = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        storeNodes(root, treewriter)

    with open(fname, newline='') as csvfile:
        treereader = csv.reader(csvfile, delimiter=';', quotechar='|')
        root = loadNodes2(treereader)
    return 0


if __name__ == '__main__':
    sys.exit(main())

