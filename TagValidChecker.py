#!/usr/bin/env python
# -*- coding: utf-8 -*-

class TagValidChecker:
    def check(self, tag_name):
        if not isinstance(tag_name, str):
            return False
        flag = True
        # Count chars
        if 3 < len(tag_name) < 10:
            flag = True
        else:
            flag = False
        if 0 < len(tag_name.split(' ')) < 3:
            flag = flag and True
        else:
            flag = flag and False
        return flag

    def message(self):
        return 'tag name должен быть длиной от 3 до 10 символов и содержать 1 ибли 3 слова'
