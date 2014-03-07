__author__ = 'Justin Jansen'
__status__ = 'Development'
__date__ = '03/07/14'

import sqlite3 as lite

"""
This is mostly untested! Use at your own risk! :)
Or test it for me ;)

Based on my Homework 4 (crawler.py) SqlManager... which was tested... so it should be pretty safe
"""


class SqlManager(object):
    def __init__(self, database_name):
        self.name = database_name.split('.')[0]
        self.tables = self._pull_tables()
        self.con = None

    def connect(self):
        """
        Connects the manager to the database
        @return: True if a successful connection is made
        """
        self.con = lite.connect(self.name + '.db')

    def disconnect(self):
        """
        Disconnects the database
        """
        if self.con:
            self.con.close()
            self.con = None

    def _pull_tables(self):
        """
        Finds the name of all the tables in the database
        """
        command = "SELECT name FROM sqlite_master WHERE type='table';"
        self.connect()
        table_list = self._fetch_command(command)
        self.disconnect()
        table_list = [str(name[0]) for name in table_list]
        return table_list

    def _fetch_command(self, command):
        """
        Runs a sql command that returns something
        """
        cur = self.con.cursor()
        cur.execute(command)
        return cur.fetchall()

    def _no_fetch_command(self, command):
        """
        Runs a sql command that does not return anything
        """
        cur = self.con.cursor()
        cur.execute(command)
        self.con.commit()


class TableAdder(SqlManager):
    def __init__(self, database_name, table_name):
        super(TableAdder, self).__init__(database_name)
        if table_name in self.tables:
            raise NameError('Table ' + table_name + ' Already in database')
        self.table_name = table_name
        self.table_columns = []
        self.done = False

    def add_column(self, name, col_type='text'):
        """
        Defines a column to add to the table
        """
        self.table_columns += [(name, col_type)]

    def commit(self):
        """
        Can only be ran once! To be used when all the rows have been added and you are ready to commit to adding
        the table to the database.
        """
        if not self.done:
            command = 'CREATE TABLE ' + self.table_name + '('
            for value in self.table_columns:
                command += value[0] + ' ' + value[1] + ', '
            command = command[:-2] + ");"
            self.connect()
            self._no_fetch_command(command)
            self.disconnect()
            self.done = True


class TableManager(SqlManager):
    def __init__(self, database_name, table_name):
        super(TableManager, self).__init__(database_name)
        if not table_name in self.tables:
            raise NameError('Table not found in database')
        self.table_name = table_name
        self.table_col_names = []
        self.table_col_type = []
        self._set_columns_info()

    def _set_columns_info(self):
        """
        Gets information that the program needs about the table
        """
        command = 'pragma table_info("' + self.table_name + '");'
        self.connect()
        raw_data = self._fetch_command(command)
        for column in raw_data:
            self.table_col_names += [str(column[1])]
            self.table_col_type += [str(column[2])]
        self.disconnect()

    def quick_push(self, value_list):
        """
        Assumes that you already know the order and type
        So you can just feed it a list
        @param value_list: A list of values to insert into the table
        """
        if len(value_list) == len(self.table_col_names):
            command = "INSERT INTO " + self.table_name + " VALUES"
            command = command + '(' + str(value_list).strip('[').strip(']') + ');'
            self.connect()
            self._no_fetch_command(command)
            self.disconnect()
        else:
            raise ValueError('value_list does not match columns')

    def push(self, tuple_list):
        """
        A safer push that checks column names and converts the types before trying to push to the table
        @param tuple_list: a list in the format [(column_name, value_to_insert), ... ]
        """
        # TODO
        pass

    def clear_table(self):
        """
        Makes the table empty
        """
        self.connect()
        command = "DELETE FROM " + self.table_name + ';'
        self._no_fetch_command(command)
        self._no_fetch_command("VACUUM;")
        self.disconnect()

    def pull(self, row_list=None):
        """
        Get data from the database
        @param row_list: The rows to get, if left as None it will return all rows
        @return: The data from the table
        """
        self.connect()
        command = "SELECT "
        if not row_list:
            command += "* "
        else:
            for x in row_list:
                if x in self.table_col_names:
                    command += x + ', '
            command = command[:-2]
        command += " FROM " + self.table_name + ';'
        values = self._fetch_command(command)
        self.disconnect()
        return values
