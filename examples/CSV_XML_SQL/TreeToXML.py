#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from TagTreeItem import TagTreeItem
try:
    from PyQt5 import QtXml
    from PyQt5.QtCore import QFile, QXmlStreamReader, QIODevice, QXmlStreamWriter
except:
    from PySide import QtXml
    from PySide.QtCore import QFile, QXmlStreamReader, QIODevice, QXmlStreamWriter

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


class XmlHandler(QtXml.QXmlDefaultHandler):
    def __init__(self):
        QtXml.QXmlDefaultHandler.__init__(self)
        #self._root = root
        self._item = None
        self._text = ''
        self._error = ''

    def startElement(self, namespace, name, qname, attributes):
        print('<qname: {} name: {}>'.format(qname, type(qname)))
        if qname == 'item':
            tag_name = attributes.value('tag_name')
            item = TagTreeItem(tag_name)
            if self._item is not None:
                self._item.appendChild(item)
            self._item = item
        self._text = ''
        return True

    def endElement(self, namespace, name, qname):
        parent = self._item.parent()
        if parent is not None:
            self._item = parent
        return True

    def characters(self, text):
        self._text += text
        return True

    def fatalError(self, exception):
        print('Parse Error: line {}, column {}:\n  {}'.format(
              exception.lineNumber(),
              exception.columnNumber(),
              exception.message(),
              ))
        self._error = 'Parse Error: line {}, column {}:\n  {}'.format(
              exception.lineNumber(),
              exception.columnNumber(),
              exception.message(),
              )
        return False

    def errorString(self):
        return self._error

    def getTree(self):
        return self._item



def storeNodesRecursive(node, writer):
    '''a function called recursively, looking at all nodes beneath node
    Вложенная функция для поиска по вложенным элементам.
    Это фактически обход по графу, "в глубину". Вызывается рекурсивно - сама себя.
    Красиво, но если будет слишком тормозить - переписать с рекурсии на цикл.
    '''
    assert isinstance(node, TagTreeItem), 'node должен быть объектом типа TreeItem!'
    assert isinstance(writer, QXmlStreamWriter), 'writer должен быть объектом типа QXmlStreamWriter'
    writer.writeStartElement('item')
    writer.writeAttribute('tag_name', node.tag_as_str())
    print('store item: {}'.format(node.tag.tag_as_str()))
    for child in node.childItems:
        storeNodesRecursive(child, writer)
    writer.writeEndElement()


def storeNodesStreamWriter(fname, root):
    assert isinstance(fname, str), ''
    assert isinstance(root, TagTreeItem), ''
    xmlFile = QFile(fname)
    if xmlFile.open(QIODevice.WriteOnly | QIODevice.Text):
        writer = QXmlStreamWriter(xmlFile)
        writer.setAutoFormatting(True)
        writer.writeStartDocument()
        writer.writeStartElement("items")
        storeNodesRecursive(root, writer)
        writer.writeEndElement()
        writer.writeEndDocument()
    xmlFile.close()


def loadNodes(fname):
    '''Попытка "плоской" (загружаем всё в список, и потом формируем дерево) загрузки из БД'''
    if not os.path.exists(fname):
        print('File not exists')
        return None
    xmlFile = QFile(fname)
    source = QtXml.QXmlInputSource(xmlFile)
    handler = XmlHandler()
    reader = QtXml.QXmlSimpleReader()
    reader.setContentHandler(handler)
    reader.setErrorHandler(handler)
    print('prepare parse')
    root = None
    if reader.parse(source):
        print('parse')
        root = handler.getTree()
    else:
        print('error {}'.format(handler.errorString()))
    return root


def loadNodes2(fname):
    '''Load nodes with XML StreamReader'''
    def loadNodesViaStream(reader):
        assert isinstance(reader, QXmlStreamReader)
        _item = None
        while not reader.atEnd():
            reader.readNext()
            if reader.isStartElement():
                if reader.name() == 'item':
                    attributes = reader.attributes()
                    tag_name = attributes.value('tag_name')
                    print('tag name: {}'.format(tag_name))
                    item = TagTreeItem(tag_name)
                    if _item is not None:
                        _item.appendChild(item)
                    _item = item
            elif reader.isEndElement():
                parent = _item.parent()
                if parent is not None:
                    _item = parent
        return _item

    if not os.path.exists(fname):
        print('File not exists')
        return None
    xmlFile = QFile(fname)
    if xmlFile.open(QIODevice.ReadOnly):
        reader = QXmlStreamReader(xmlFile)
        root = loadNodesViaStream(reader)
        if reader.hasError():
            return root
        return root

def Foo(node):
    print('Visit: {}'.format(node.tag_as_str()))
    for child in node.childItems:
        Foo(child)

def main():
    #root = loadNodes('tree1.xml')
    #root = loadNodes2('tree1.xml')
    #Foo(root)
    root = createSimpleTree()
    storeNodesStreamWriter('tree2.xml', root)
    return 0


if __name__ == '__main__':
    sys.exit(main())

