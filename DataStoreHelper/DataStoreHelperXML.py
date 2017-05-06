#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from PyQt5.QtCore import QFile, QXmlStreamReader, QIODevice, QXmlStreamWriter
except:
    from PySide.QtCore import QFile, QXmlStreamReader, QIODevice, QXmlStreamWriter

import os
from TagTreeItem import TagTreeItem


class DataStoreHelperXML:
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

    def load(self, fname=None):
        __fname = fname or self.__fname
        assert isinstance(__fname, str), ''
        if not os.path.exists(__fname):
            self.__error = 'File not exists'
            self.__error_flag = True
            return None
        try:
            xmlFile = QFile(__fname)
            root = None
            if xmlFile.open(QIODevice.ReadOnly):
                try:
                    reader = QXmlStreamReader(xmlFile)
                    root = self.__loadNodesViaStream(reader)
                    if reader.hasError():
                        self.__error = reader.errorString()
                        self.__error_flag = True
                except Exception as e:
                    self.__error = str(e)
                    self.__error_flag = True
                finally:
                    xmlFile.close()
            return root
        except Exception as e:
            self.__error = str(e)
            self.__error_flag = True
            return None

    def store(self, root, fname=None):
        __fname = fname or self.__fname
        assert isinstance(__fname, str), ''
        assert isinstance(root, TagTreeItem), ''
        try:
            xmlFile = QFile(__fname)
            if xmlFile.open(QIODevice.WriteOnly | QIODevice.Text):
                try:
                    writer = QXmlStreamWriter(xmlFile)
                    writer.setAutoFormatting(True)
                    writer.writeStartDocument()
                    writer.writeStartElement("items")
                    self.__storeNodesRecursive(root, writer)
                    writer.writeEndElement()
                    writer.writeEndDocument()
                except Exception as e:
                    self.__error = str(e)
                    self.__error_flag = True
                    return False
                finally:
                    xmlFile.close()
        except Exception as e:
            self.__error = str(e)
            self.__error_flag = True
            return False
        return True

    def __loadNodesViaStream(self, reader):
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

    def __storeNodesRecursive(self, node, writer):
        '''a function called recursively, looking at all nodes beneath node
        Вложенная функция для поиска по вложенным элементам.
        Это фактически обход по графу, "в глубину". Вызывается рекурсивно - сама себя.
        Красиво, но если будет слишком тормозить - переписать с рекурсии на цикл.
        '''
        assert isinstance(node, TagTreeItem), 'node должен быть объектом типа TreeItem!'
        assert isinstance(writer, QXmlStreamWriter), 'writer должен быть объектом типа QXmlStreamWriter'
        writer.writeStartElement('item')
        writer.writeAttribute('tag_name', node.tag_as_str())
        print('store item: {}'.format(node.tag_as_str()))
        for child in node.childItems:
            self.__storeNodesRecursive(child, writer)
        writer.writeEndElement()
