from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt
from qtpy.QtGui import QColor

from ert_gui.ertwidgets import resourceIcon


class DataTypeKeysListModel(QAbstractItemModel):
    DEFAULT_DATA_TYPE = QColor(255, 255, 255)
    HAS_OBSERVATIONS = QColor(237, 218, 116)
    GROUP_ITEM = QColor(64, 64, 64)

    def __init__(self, api):
        """
        @type ert: res.enkf.EnKFMain
        """
        QAbstractItemModel.__init__(self)
        self._api = api
        self.__icon = resourceIcon("ide/small/bullet_star")

    def index(self, row, column, parent=None, *args, **kwargs):
        return self.createIndex(row, column)

    def parent(self, index=None):
        return QModelIndex()

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._api.allDataTypeKeys())

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return 1

    def data(self, index, role=None):
        assert isinstance(index, QModelIndex)

        if index.isValid():
            items = self._api.allDataTypeKeys()
            row = index.row()
            item = items[row]

            if role == Qt.DisplayRole:
                return item
            elif role == Qt.BackgroundRole:
                if self._api.isKeyWithObservations(item):
                    return self.HAS_OBSERVATIONS

    def itemAt(self, index):
        assert isinstance(index, QModelIndex)

        if index.isValid():
            row = index.row()
            return self._api.allDataTypeKeys()[row]

        return None


    def isSummaryKey(self, key):
        return self._api.isSummaryKey(key)

    def isBlockKey(self, key):
        return False

    def isGenKWKey(self, key):
        return self._api.isGenKwKey(key)

    def isGenDataKey(self, key):
        return self._api.isGenDataKey(key)

    def isCustomKwKey(self, key):
        return self._api.isCustomKwKey(key)

    def isCustomPcaKey(self, key):
        return False
