#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Базовый класс (интерфейс) DataStoreHelper.
По-хорошему от него нужно наследоваться.
Но так как у нас Python, и утиная типизация
(главное наличие функций с одинаковыми именами и парамерами вызова)
- ради экономии памяти можем опустить.
А этот файл использовать как образец.
"""


class DataStoreHelperBase:
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
        """Return root or None"""
        raise NotImplementedError()

    def store(self, root, fname=None):
        """Return False ot True"""
        raise NotImplementedError()
