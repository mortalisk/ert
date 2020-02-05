from ert_gui.ertwidgets.models.selectable_list_model import SelectableListModel


class FilterableKwListModel(SelectableListModel):
    """
    Adds ERT - plotting keyword specific filtering functionality to the general SelectableListModel
    """
    def __init__(self, key_defs):
        SelectableListModel.__init__(self, key_defs)
        self._show_summary_keys = True
        self._show_gen_kw_keys = True
        self._show_gen_data_keys = True
        self._show_custom_kw_keys = True
        
    def getList(self):
        return self._items

