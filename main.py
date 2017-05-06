#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from PyQt5.QtWidgets import QApplication
except:
    from PySide.QtWidgets import QApplication

from TagManagerMainWidget import TagManager

ORGANIZATION_NAME = 'OpenSource'
APPLICATION_NAME = 'qTagManager'

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    # Для того, чтобы каждый раз при вызове QSettings не вводить данные вашего приложения
    # по которым будут находиться настройки, можно
    # установить их глобально для всего приложения
    QApplication.setOrganizationName(ORGANIZATION_NAME)
    QApplication.setApplicationName(APPLICATION_NAME)
    m = TagManager()
    m.show()
    sys.exit(app.exec())
