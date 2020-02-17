
class DataResult(object):

    def __init__(self, case_name,key,realization_number, data_array, index_array):
        self.case_name = case_name
        self.key = key
        self.data_array = data_array
        self.index_array = index_array
        self.realization_number = realization_number
