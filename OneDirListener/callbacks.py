__author__ = 'Justin'


class CallBack(object):
    def __init__(self):
        self.files = []
        self.folders = []
        self.store_list = []

    def file_folder_separator(self, line):
        """
        A callback for separating files from folders, do not call.
        """
        if not len(line) == 0:
            if not line[0] == 'd':
                self.files += [line.split(' ')[-1]]
            else:
                self.folders += [line.split(' ')[-1]]

    def general_list(self, line):
        """
        Private: Do not call.
        """
        self.general_list += [line]
