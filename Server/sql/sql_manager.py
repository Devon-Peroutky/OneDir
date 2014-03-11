__author__ = 'Justin Jansen'
__status__ = 'Development'
__date__ = '03/07/14'

import sqlite3 as lite

"""
SqlManager(database_name)
    - The parent class to all other classes in sql_manager.py
TableAdder(database_name, table_name)
    - A tool for adding new tables to the database
TableRemover(database_name, table_name)
    - A tool for deleting tables from the database
TableManager(database_name, table_name)
    - Manages common database tasks such as adding and removing items from a table
    - Likely that other methods will be useful.
    - Will write them as needed
"""


class SqlManager(object):
    """
    The parent manager, meant to be extended, not used unless the job
    is really unique and it is simpler to use this.
    """

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
        self.con.text_factory = str

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
    """
    Adds a table to a database, the database does not need to
    exist before invoking this.
    """

    def __init__(self, database_name, table_name):
        super(TableAdder, self).__init__(database_name)
        if table_name in self.tables:
            raise NameError('Table ' + table_name + ' Already in database')
        self.table_name = table_name
        self.table_columns = []
        self.done = False
        self.sql_types = ['integer', 'text', 'real', 'blob']

    def add_column(self, name, col_type='text'):
        """
        Defines a column to add to the table
        """
        col_type = str(col_type).lower()
        if col_type in self.sql_types:
            self.table_columns += [(name, col_type)]
        else:
            raise ValueError('Undefined column type')

    def commit(self):
        """
        Can only be ran once! To be used when all the rows have been added and you are ready to commit to adding
        the table to the database.
        """
        if not self.done:
            values = []
            for value in self.table_columns:
                values += value[0] + ' ' + value[1] + ', '
            values = ''.join(values[:-2])
            command = 'CREATE TABLE %s(%s)' % (self.table_name, values)
            self.connect()
            self._no_fetch_command(command)
            self.disconnect()
            self.done = True


class TableRemover(SqlManager):
    """
    Deletes a table from the database
    """

    def __init__(self, database_name, table_name):
        """
        @raises NameError: table not found
        """
        super(TableRemover, self).__init__(database_name)
        if not table_name in self.tables:
            raise NameError('Table ' + table_name + ' not in database')
        self._delete_table(table_name)

    def _delete_table(self, table_name):
        command = 'DROP TABLE IF EXISTS %s;' % table_name
        self.connect()
        self._no_fetch_command(command)
        self.disconnect()


class TableManager(SqlManager):
    """
    Handles pulls and pushes from a table in the database.
    Can now handle 'with'
    """

    def __init__(self, database_name, table_name):
        """
        @raises NameError: The table is not in the database
        """
        super(TableManager, self).__init__(database_name)
        if not table_name in self.tables:
            raise NameError('Table not found in database')
        self.connect()
        self.table_name = table_name
        self.table_col_names = []
        self.table_col_type = []
        self._set_columns_info()

    def _set_columns_info(self):
        """
        Gets information that the program needs about the table
        """
        command = 'pragma table_info("%s");' % self.table_name
        raw_data = self._fetch_command(command)
        for column in raw_data:
            self.table_col_names += [str(column[1])]
            self.table_col_type += [str(column[2])]

    def quick_push(self, value_list):
        """
        Assumes that you already know the order and type
        So you can just feed it a list
        @param value_list: A list of values to insert into the table
        @raises ValueError: If the list is the wrong length
        """
        if len(value_list) == len(self.table_col_names):
            values = str(value_list).strip('[').strip(']')
            command = 'INSERT INTO %s VALUES(%s)' % (self.table_name, values)
            self._no_fetch_command(command)
        else:
            raise ValueError('value_list does not match columns')

    def push(self, tuple_list):
        """
        A safer push that checks column names and converts the types before trying to push to the table.
        Columns can be inserted in any order.
        Not every column needs to be filled.
        @param tuple_list: a list in the format [(column_name, value_to_insert), ... ]
        """
        unordered = [x[0] for x in tuple_list]
        push_list = []
        for i, value in enumerate(self.table_col_names):
            if value in unordered:
                to_add = tuple_list[unordered.index(value)][1]
                col_type = self.table_col_type[i]
                col_type = str(col_type).lower()
                if col_type == 'text':
                    push_list += [str(to_add)]
                elif col_type == 'integer':
                    push_list += [int(to_add)]
                elif col_type == 'real':
                    push_list += [float(to_add)]
                elif col_type == 'blob':
                    push_list += [buffer(to_add)]
            else:
                raise ValueError('Undefined Column')
        self.quick_push(push_list)

    def clear_table(self):
        """
        Makes the table empty
        """
        command = "DELETE FROM %s;" % self.table_name
        self._no_fetch_command(command)
        self._no_fetch_command("VACUUM;")

    def pull(self, col_list=[]):
        """
        Get data from the database
        @param col_list: The rows to get, if left as None it will return all rows
        @return: The data from the table
        """
        if len(col_list) == 0:
            values = '*'
        else:
            values = ','.join(col_list)
        command = 'SELECT %s FROM %s;' % (values, self.table_name)
        return self._fetch_command(command)

    def pull_where(self, value, compare_to, operator, col_list=[]):
        """
        Resembles: SELECT col_list FROM table_name WHERE value (operator) compare_to;
        @param value: the column name of the value you want to compare with
        @param compare_to: value to compare against
        @param operator: '=', '!=', '<>', '>', '<', '>=', '<='
        @param col_list: list of columns to return data from
        @return: data from the table that match your query
        """
        operators = ['=', '!=', '<>', '>', '<', '>=', '<=']
        if not operator in operators:
            raise ValueError('Excepted operators: %s' % str(operators)[1:-1])
        if len(col_list) == 0:
            cols = '*'
        else:
            cols = ','.join(col_list)
        if type(compare_to) == str:
            comp = "%s%s'%s'" % (str(value), str(operator), str(compare_to))
        else:
            comp = "%s%s%s" % (str(value), str(operator), str(compare_to))
        command = 'SELECT %s FROM %s WHERE %s;' % (cols, self.table_name, comp)
        return self._fetch_command(command)

    def __enter__(self):
        """
        For 'with'
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
       For 'with'
        """
        self.disconnect()
