import sqlite3 as lite

"""
This is a portion of my homework 4
We don't have to use it, but I figured I would

There is def a few things that need to be fixed in it
"""


class SqlManager():
    """
    A Limited amount of control over the sql database through python
    """

    def __init__(self, database_name):
        self.name = database_name
        self.tables = {}
        self.con = None

    def connect(self):
        """
        Connects the manager to the database
        @return: True if a successful connection is made
        """
        self.con = lite.connect(self.name)

    def disconnect(self):
        """
        Disconnects the database
        """
        if self.con:
            self.con.close()
            self.con = None

    def is_table_set(self, table_name):
        """
        Checks if a table has already been defined
        @param table_name: The name of the table
        @return: True if the table has been defined
        """
        if table_name in self.tables:
            return True
        else:
            return False

    def get_table_columns_from_db(self, table_name): #TODO fix (this is geared towards hw 4)
        """
        Find the values of columns in the table
        @param table_name: The name of the table to look up
        @return: a list of tuples in the form (name, type)
        """
        command = 'pragma table_info(' + table_name + ');'
        raw_table_data = self._fetch_command(command)
        tuple_list = []
        for col in raw_table_data:
            tuple_list += [(str(col[1]), str(col[2]))]
        return tuple_list

    def add_new_table(self, table_name, table_tuple_list):
        """
        Tries to add table to the database
        @param table_name: the name of the table to add
        @param table_tuple_list: a list of tuples [(name, type)]
        @raise: Value error table is already in the db, this will not allow overwrites
        """
        if not self.is_table_set(table_name):
            self.tables[table_name] = table_tuple_list
            command = "CREATE TABLE " + table_name + "("
            for value in table_tuple_list:
                command += value[0] + ' ' + value[1] + ', '
            command = command[:-2] + ");"
            self._no_fetch_command(command)
        else:
            raise ValueError('Table already exists, you must delete first.')

    def remove_table(self, table_name):
        """
        Deletes a table from the database
        @param table_name: the name of the table
        """
        command = "DROP TABLE IF EXISTS " + table_name + ';'
        del self.tables[table_name]
        self._no_fetch_command(command)

    def define_existing_table(self, table_name):
        """
        Query database for table, and imports column information
        Needed when wanting to use existing table
        @param table_name: The name of the table to query
        """
        tuple_list = self.get_table_columns_from_db(table_name)
        self.tables[table_name] = tuple_list

    def push(self, table_name, corresponding_data):
        """
        Insert table into database
        @param table_name: the name of the table to push into
        @param corresponding_data: the data that corresponds to the columns
        """
        command = "INSERT INTO " + table_name + " VALUES"
        command = command + '(' + str(corresponding_data).strip('[').strip(']') + ');'
        self._no_fetch_command(command)

    def pull(self, table_name, corresponding_data):
        """
        Get data from the database
        @param table_name: The name of the table
        @param corresponding_data: The rows to get
        @return: The data from the table
        """
        command = "SELECT "
        if not corresponding_data:
            command += "* "
        else:
            for x in corresponding_data:
                command += x + ', '
            command = command[:-2]
        command += " FROM " + table_name + ';'
        return self._fetch_command(command)

    def clear_table(self, table_name):
        """
        Makes the table empty
        @param table_name: the name of the table
        """
        if self.is_table_set(table_name):
            command = "DELETE FROM " + table_name + ';'
            self._no_fetch_command(command)
            self._no_fetch_command("VACUUM;")

    def _fetch_command(self, command):
        cur = self.con.cursor()
        cur.execute(command)
        return cur.fetchall()

    def _no_fetch_command(self, command):
        cur = self.con.cursor()
        cur.execute(command)
        self.con.commit()
