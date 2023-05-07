# from dontlose import SQLAccess, SQLData, FromTable, JoinTable, SelectColumns, Where, Group, Order
from dataclasses import dataclass
import pyinputplus as pyip
import os
import shelve
import pyodbc
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from collections import Counter


class MakeShelf:

    # Create shelf file if not exist
    @staticmethod
    def is_shelf_exist():
        # open message
        if not os.path.isfile('Server.dat'):
            print("It looks like this is the first time you've opened this application, "
                  "so we're just going to set up a few things.\n")
            Shelfie2.server_file()
        else:
            Shelfie2.get_shelf()


class ServerFile:

    # Store variables
    def __init__(self):
        self.driver = []
        self.server_name = []
        self.database = []
        self.connection_type = []

    # Open Shelf
    def get_shelf(self):
        shelf = shelve.open('Server')
        self.driver = str(shelf['Driver'])
        self.server_name = str(shelf['Server'])
        self.database = str(shelf['Database'])
        self.connection_type = str(shelf['Connection'])
        return self.driver, self.server_name, self.database, self.connection_type

    # Access this database?
    def access_database(self):
        server_ques = pyip.inputYesNo(f"Would you still like to access {self.database} in {self.server_name}?\n")
        if server_ques != 'n' or 'no':
            self.get_shelf()
        else:
            self.server_file()

    # Add or change server file
    def server_file(self):
        with shelve.open('Server') as shelf:
            # get server name
            s = pyip.inputFilepath("Please input the server name you'd like to access.\n")
            shelf['Server'] = s
            self.server_name = s
            # get driver
            dr = pyip.inputFilepath("Please input the driver name.\n")
            shelf['Driver'] = dr
            self.driver = dr
            # get database
            d = input('Enter database name \n')
            shelf['Database'] = d
            self.database = d
            # get username and password if exists
            user_pass = pyip.inputYesNo('Do you have a username and password? \n')
            if user_pass == 'yes':
                username = input('Enter your username \n')
                password = input('Enter your_password \n')
                c = f'UID={username};PWD={password}'
            elif user_pass == 'no':
                c = 'Trusted_Connection = yes'
            shelf['Connection'] = c
            self.connection_type = c
        print('Saved.\n')
        # return data
        return self.driver, self.server_name, self.database, self.connection_type


class SQLConnect:

    # Import variables from ServerFile
    def __init__(self, shelfie2):
        self.Shelfie2 = shelfie2
        self.cursor = []
        self.connection_str = ""

    # Create a connection string
    def create_string(self):
        self.connection_str = f'DRIVER={self.Shelfie2.driver};SERVER={self.Shelfie2.server_name};' \
                              f'DATABASE={self.Shelfie2.database};{self.Shelfie2.connection_type};'
        return self.connection_str

    # Connect to server
    def connect(self):
        try:
            conn = pyodbc.connect(self.connection_str)
            self.cursor = conn.cursor()
            print(f"Successfully connected to {self.Shelfie2.server_name}'s {self.Shelfie2.database} database.")
            return self.cursor
        except pyodbc.Error as e:
            print(f'Error connecting to SQL server: {e}.')


class SQLData:

    # Declare variables
    def __init__(self, shelfie3):
        self.Shelfie3 = shelfie3
        self.tables = []

    # Access tables in database
    def get_tables(self):
        # get database tables
        table_get = [x[2] for x in self.Shelfie3.cursor.tables(tableType='TABLE')]
        # sort table
        table_get.sort()
        # place keys in tables dictionary, assign value to each key, then print tables
        self.tables = {}
        count = 0
        for t in table_get:
            self.tables.setdefault(t, count+1)
            count += 1
        # return data
        return self.tables


class FromTable:

    # Declare variables
    def __init__(self, shelfie3, shelfie4):
        # declare variables
        self.Shelfie3 = shelfie3
        self.Shelfie4 = shelfie4
        self.from_data = {}
        self.from_print = ""

    # Select FROM table
    def from_select(self):
        # print tables
        print("Please input the number of the 1st table you'd like to develop a query for.\n")
        for t, table_get in enumerate(self.Shelfie4.tables.keys()):
            print(f"{t + 1}. {table_get}")
        # select FROM table
        f_table = pyip.inputNum(min=1, max=len(self.Shelfie4.tables.keys()), blank=False)
        # match number to table
        from_table = list(self.Shelfie4.tables.keys())[int(f_table) - 1]
        # get first letter
        letter = from_table[0].lower()
        # return data
        self.make_from_dict(from_table, letter)

    # Get FROM table columns and add everything to a dictionary
    def make_from_dict(self, from_table, letter):
        # get FROM table columns
        from_columns = []
        for row in self.Shelfie3.cursor.columns(table=from_table):
            from_columns.append(str(row.column_name))
        # create dictionary for join data
        self.from_data[from_table] = {'column_names': from_columns, 'letter': letter}
        # return data
        self.from_print = f"FROM {from_table} AS {letter}\n"
        return self.from_data, self.from_print


class JoinTable:

    # Declare variables
    def __init__(self, shelfie3, shelfie4, shelfie5):
        self.Shelfie3 = shelfie3
        self.Shelfie4 = shelfie4
        self.Shelfie5 = shelfie5
        self.join_data = {}
        self.join_print = ""

    # Prompt
    def decide_join(self):
        yesno_join = pyip.inputYesNo("Would you like to add a table to join?\n", blank=True)
        if yesno_join == 'yes' or yesno_join == 'y':
            self.join_select()
        if yesno_join == 'no' or yesno_join == 'n':
            # skip if no joins added
            pass

    # JOIN statement development
    def join_select(self):
        # join type select
        join_type = pyip.inputMenu(
            ["JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN",
             "LEFT OUTER JOIN", "RIGHT OUTER JOIN", "CROSS JOIN", "HASH JOIN"],
            "Please select the JOIN type you'd like to use.\n", numbered=True)
        # print tables
        print("Please input the number of the table you'd like to join.\n")
        for t, table_get in enumerate(self.Shelfie4.tables.keys()):
            print(f"{t + 1}. {table_get}")
        # select JOIN table
        j_select = pyip.inputNum(min=1, max=len(self.Shelfie4.tables.keys()), blank=False)
        # match number to table and add to dictionary
        join_table = list(self.Shelfie4.tables.keys())[int(j_select) - 1]
        # get first letter
        letter = join_table[0].lower()
        # return data
        self.make_join_dict(join_type, join_table, letter)

    # Get JOIN table columns and add everything to a dictionary
    def make_join_dict(self, join_type, join_table, letter):
        # get JOIN table columns
        join_columns = []
        for row in self.Shelfie3.cursor.columns(table=join_table):
            join_columns.append(str(row.column_name))
        # create dictionary for join data
        self.join_data[join_table] = {'column_names': join_columns, 'letter': letter, 'join_type': join_type}
        return self.join_data and self.decide_on()

    # add "ON" to join?
    def decide_on(self):
        yesno_on = pyip.inputYesNo("Would you like to add an ON statement to JOIN?\n", blank=True)
        if yesno_on == 'y' or yesno_on == 'yes':
            self.get_on()
        else:
            self.decide_join()

    # ON?
    def get_on(self):
        # storage
        on1 = ""
        on2 = ""
        fall_columns = []
        jall_columns = []
        # get columns from table
        for from_table_name in self.Shelfie5.from_data.keys():
            for column_name in self.Shelfie5.from_data[from_table_name]["column_names"]:
                fall_columns.append(f"{from_table_name}.{column_name}")
        # get columns of join table
        for join_table_name in self.join_data.keys():
            for column_name in self.join_data[join_table_name]["column_names"]:
                jall_columns.append(f"{join_table_name}.{column_name}")
        # count
        fcount = Counter(fall_columns)
        fnum = sum(fcount.values())
        jcount = Counter(jall_columns)
        jnum = sum(jcount.values())
        # if only 1 from column
        if fnum == 1:
            cont = pyip.inputYesNo(f"Only one column found in table: {str(fall_columns)}. Proceed?\n")
            if cont == "yes" or cont == "y":
                on1 = str(fall_columns)
            else:
                pass
        if fnum > 1:
            # prompt for first attribute (from)
            on1 = pyip.inputMenu(fall_columns, "Please input the number corresponding to the first value.\n",
                                 fall_columns.sort(), strip=',', numbered=True)
        # if only 1 join column
        if jnum == 1:
            cont = pyip.inputYesNo(f"Only one column found in table: {str(jall_columns)}. Proceed?\n")
            if cont == "yes" or cont == "y":
                on2 = str(fall_columns)
            else:
                pass
        if jnum > 1:
            # prompt for second attribute (join)
            on2 = pyip.inputMenu(jall_columns, "Please input the number corresponding to the second value.\n",
                                 jall_columns.sort(), strip=',', numbered=True)
        # add to dictionary
        join_table = list(self.join_data.keys())[0]
        self.join_data[join_table]['on'] = f' ON {on1} = {on2}'
        # return data
        return self.join_data and self.decide_join()

    # Create JOIN print
    def construct_join_statement(self):
        # iterate through nested loops and add to string
        join_str2 = ""
        for join_table_name, value in self.join_data.items():
            # check if there is more than 1 join statement
            if len(value) > 1:
                join_str1 = f"{value['join_type']} {join_table_name}{value.get('on', '')}"
                join_str2 += str(join_str1) + ", "
            if len(value) == 1:
                join_str1 = f"{value['join_type']} {join_table_name}{value.get('on', '')}"
                join_str2 += str(join_str1) + ""
            if len(value) == 0:
                pass
        # remove the trailing ", " from the end of the string
        join_str2 = join_str2.rstrip(", ")
        # add join_string to self.join_print
        self.join_print = str(join_str2) + "\n"
        # return data
        return self.join_print


class SelectColumns:

    # Declare variables
    def __init__(self, shelfie5, shelfie6):
        self.Shelfie5 = shelfie5
        self.Shelfie6 = shelfie6
        self.columns_all = []
        self.column = []
        self.syn_columns = ""
        self.select_print = ""

    # Choose columns
    def get_columns(self):
        # get columns from table
        all_columns = []
        for value in self.Shelfie5.from_data.values():
            # add to storage for selection
            all_columns.extend(value['column_names'])
        # get columns of join table if not empty
        for value in self.Shelfie6.join_data.values():
            # add to storage for selection
            all_columns.extend(value['column_names'])
        # remove duplicates
        self.columns_all = list(set(all_columns))
        return self.columns_all

    # Prompt
    def prompt(self):
        # in case only 1 column
        count = Counter(self.columns_all)
        num = sum(count.values())
        attr = ""
        if num == 1:
            # match column to value in from_data and/or join_data dictionaries
            for from_table in self.Shelfie5.from_data.values():
                for column_name in from_table["column_names"]:
                    if column_name in str(self.columns_all):
                        letter = from_table["letter"]
                        self.syn_columns.append(f"{letter}.{column_name}")
                        attr += f"{column_name}, "
            self.select_print = f"{attr}\n"
            return self.select_print, self.syn_columns
        else:
            col_select = pyip.inputMenu(["Select all columns.", "Add name of each column "
                                                                "you'd like to sort by."], numbered=True)
            # select all then exit
            if col_select == "Select all columns.":
                self.select_all()
            # add individual columns
            if col_select == "Add name of each column you'd like to sort by.":
                self.select_some()

    # Get all columns
    def select_all(self):
        # storage
        self.syn_columns = []
        # iterate through nested dictionary and get values for "letter" and "column name" for each from_table dictionary
        attr = "*"
        for from_table in self.Shelfie5.from_data.values():
            for column_name in from_table["column_names"]:
                letter = from_table["letter"]
                self.syn_columns.append(f"{letter}.{column_name}")
        # check for duplicates
        self.syn_columns = list(set(self.syn_columns))
        # remove the trailing ", " from the end of the string
        attr = attr.rstrip(", ")
        # return data
        self.select_print = f"{attr}\n"
        return self.select_print, self.syn_columns

    # Select columns
    def select_some(self):
        # storage
        col_list = []
        self.syn_columns = []
        attr = ""
        # prompt
        while True:
            col_select = pyip.inputMenu(self.columns_all, "Please input the number corresponding "
                                                          "to the columns you'd like to sort by.\n",
                                        self.columns_all.sort(), strip=',', numbered=True, blank=True)
            col_list.append(col_select)
            if col_select == '':
                break
        # match column to value in from_data and/or join_data dictionaries
        for from_table in self.Shelfie5.from_data.values():
            for column_name in from_table["column_names"]:
                if column_name in str(col_list):
                    letter = from_table["letter"]
                    self.syn_columns.append(f"{letter}.{column_name}")
                    attr += f"{column_name}, "
        # check for duplicates
        self.syn_columns = list(set(self.syn_columns))
        # remove the trailing ", " from the end of the string
        attr = attr.rstrip(", ")
        # get attr
        self.column = str(attr)
        # return data
        self.select_print = f"({attr})\n"
        return self.column, self.select_print, self.syn_columns


class Where:

    # Declare variables
    def __init__(self, shelfie7):
        self.Shelfie7 = shelfie7
        self.where_print = ""
        self.num = 0

    # Add AND, OR, or STOP
    def more_where(self):
        # prompt
        cont_where = pyip.inputMenu(["Add AND condition.", "Add OR condition."], numbered=True, blank=True)
        if cont_where == "Add AND condition.":
            self.where_print += "AND "
            self.add_where()
        elif cont_where == "Add OR condition.":
            self.where_print += "OR "
            self.add_where()
        elif cont_where == "":
            pass

    def add_where(self):
        # count
        count = Counter(self.Shelfie7.syn_columns)
        self.num = sum(count.values())
        # add equality, between, or null statements
        where_query = pyip.inputMenu(["Add equality statement, e.g. >, LIKE, IN, EXISTS, ANY, ALL",
                                      "Add between statement, e.g. Date BETWEEN 24/02/2018 and 05/10/2020.",
                                      "Add null statement, e.g. Purchases IS NOT NULL."],
                                     numbered=True, blank=True)
        if where_query == "Add equality statement, e.g. >, LIKE, IN, EXISTS, ANY, ALL":
            return self.num, self.equality()
        elif where_query == "Add between statement, e.g. Date BETWEEN 24/02/2018 and 05/10/2020.":
            return self.num, self.between()
        elif where_query == "Add null statement, e.g. Purchases IS NOT NULL.":
            return self.num, self.null()
        else:
            pass

    # Equalizers/Booleans/Regex
    def equality(self):
        # storage
        eq2 = None
        # in case only 1 column
        if self.num <= 1:
            cont = pyip.inputYesNo(f"Only one column selected: {self.Shelfie7.column}. Proceed?\n")
            if cont == "yes" or cont == "y":
                eq1 = ''.join(map(str, self.Shelfie7.syn_columns))
                # choose operator
                eq_select = pyip.inputMenu(["<", "<=", "=", "<>", ">", ">=", "LIKE", "NOT LIKE", "IN", "NOT IN"],
                                           "Please input the number corresponding to the equalize operator.\n",
                                           numbered=True, blank=False)
                # get second attribute/column/Boolean/value
                eq2_choice = pyip.inputMenu(['TRUE', 'FALSE', 'ANY', 'ALL', 'Date', 'Number', 'Other'],
                                            "Please input the number corresponding to the second value type.\n",
                                            strip=',', numbered=True, blank=False)
                if eq2_choice == "TRUE" or "FALSE" or "ANY" or "ALL":
                    eq2 = eq2_choice
                if eq2_choice == "Date":
                    eq2 = input("Please enter a date.\n")
                if eq2_choice == "Number":
                    eq2 = pyip.inputNum('Please enter a number.\n', blank=False)
                if eq2_choice == "Other":
                    eq2 = inputMenu("Please input second value.")
                # return data
                equality_print = f"{eq1} {eq_select} {eq2}, "
                self.where_print += str(equality_print)
                # add more queries if desired
                self.more_where()
            else:
                pass
        # more than 1 column
        if self.num > 1:
            # get first attribute/column
            eq1 = pyip.inputMenu(self.Shelfie7.syn_columns, "Please input the number corresponding "
                                                            "to the first value.\n",
                                 self.Shelfie7.syn_columns.sort(), strip=',', numbered=True, blank=False)
            # choose operator
            eq_select = pyip.inputMenu(["<", "<=", "=", "<>", ">", ">=", "LIKE", "NOT LIKE", "IN", "NOT IN"],
                                       "Please input the number corresponding to the equalize operator.\n",
                                       numbered=True, blank=False)
            # get second attribute/column/Boolean/value
            eq2_choice = pyip.inputMenu(['TRUE', 'FALSE', 'ANY', 'ALL', 'Date', 'Number', 'Column', 'Other'],
                                        "Please input the number corresponding to the second value type.\n",
                                        strip=',', numbered=True, blank=False)
            if eq2_choice == "TRUE" or "FALSE" or "ANY" or "ALL":
                eq2 = eq_select
            if eq2_choice == "Date":
                eq2 = input("Please enter a date.\n")
            if eq2_choice == "Number":
                eq2 = pyip.inputNum('Please enter a number.\n', blank=False)
            if eq2_choice == "Column":
                eq2 = pyip.inputMenu(self.Shelfie13.syn_columns2, "Please input the number corresponding "
                                                                  "to the column.\n",
                                     self.Shelfie13.syn_columns2.sort(), strip=',', numbered=True, blank=False)
            if eq2_choice == "Other":
                eq2 = inputMenu("Please input second value.")
            # return data
            equality_print = f"{eq1} {eq_select} {eq2}, "
            self.where_print += str(equality_print)
            # add more queries if desired
            self.more_where()

    # Between
    def between(self):
        # storage
        bet2 = None
        bet3 = None
        # in case only 1 column
        if self.num == 1:
            cont = pyip.inputYesNo(f"Only one column selected: {self.Shelfie7.column}. Proceed?\n")
            if cont == "yes" or cont == "y":
                bet1 = ''.join(map(str, self.Shelfie7.syn_columns))
                # choose between or not between
                bet_select = pyip.inputMenu(["BETWEEN", "NOT BETWEEN"],
                                            "Please input the number corresponding to the BETWEEN operator.\n",
                                            numbered=True, blank=False)
                # get second attribute
                bet2_choice = pyip.inputMenu(['Date', 'Number', 'Other'],
                                             "Please input the number corresponding to the first value type.\n",
                                             strip=',', numbered=True, blank=False)
                if bet2_choice == "Date":
                    bet2 = input("Please enter a date.\n")
                if bet2_choice == "Number":
                    bet2 = pyip.inputNum('Please enter a number.\n', blank=False)
                if bet2_choice == "Other":
                    bet2 = input("Please input the first value.\n")
                # get third attribute
                bet3_choice = pyip.inputMenu(['Date', 'Number', 'Other'],
                                             "Please input the number corresponding to the second value type.\n",
                                             strip=',', numbered=True, blank=False)
                if bet3_choice == "Date":
                    bet3 = input("Please enter a date.\n")
                if bet3_choice == "Number":
                    bet3 = pyip.inputNum('Please enter a number.\n', blank=False)
                if bet3_choice == "Column":
                    bet3 = pyip.inputMenu(self.Shelfie7.syn_columns,
                                          "Please input the number corresponding to the column.\n",
                                          self.Shelfie7.syn_columns.sort(), strip=',', numbered=True, blank=False)
                if bet2_choice == "Other":
                    bet3 = input("Please input the second value.\n")
                # return data
                between_print = f"{bet1} {bet_select} {bet2} AND {bet3}, "
                self.where_print += str(between_print)
                # add more queries if desired
                self.more_where()
            else:
                pass
        # multiple columns
        if self.num > 1:
            # get first attribute/column
            bet1 = pyip.inputMenu(self.Shelfie7.syn_columns, "Please input the number corresponding "
                                                             "to the first value.\n",
                                  strip=',', numbered=True, blank=False)
            # choose between or not between
            bet_select = pyip.inputMenu(["BETWEEN", "NOT BETWEEN"],
                                        "Please input the number corresponding to the BETWEEN operator.\n",
                                        numbered=True, blank=False)
            # get second attribute
            bet2_choice = pyip.inputMenu(['Date', 'Number', 'Column', 'Other'],
                                         "Please input the number corresponding to the first value type.\n",
                                         strip=',', numbered=True, blank=False)
            if bet2_choice == "Date":
                bet2 = input("Please enter a date.\n")
            if bet2_choice == "Number":
                bet2 = pyip.inputNum('Please enter a number.\n', blank=False)
            if bet2_choice == "Column":
                bet2 = pyip.inputMenu(self.Shelfie7.syn_columns, "Please input the number corresponding "
                                                                 "to the column.\n",
                                      self.Shelfie7.syn_columns.sort(), strip=',', numbered=True, blank=False)
            if bet2_choice == "Other":
                bet2 = input("Please input the first value.\n")
            # get third attribute
            bet3_choice = pyip.inputMenu(['Date', 'Number', 'Column', 'Other'],
                                         "Please input the number corresponding to the second value type.\n",
                                         strip=',', numbered=True, blank=False)
            if bet3_choice == "Date":
                bet3 = input("Please enter a date.\n")
            if bet3_choice == "Number":
                bet3 = pyip.inputNum('Please enter a number.\n', blank=False)
            if bet3_choice == "Column":
                bet3 = pyip.inputMenu(self.Shelfie7.syn_columns, "Please input the number corresponding "
                                                                 "to the column.\n",
                                      self.Shelfie7.syn_columns.sort(), strip=',', numbered=True, blank=False)
            if bet2_choice == "Other":
                bet3 = input("Please input the second value.\n")
            # return data
            between_print = f"{bet1} {bet_select} {bet2} AND {bet3}, "
            self.where_print += str(between_print)
            # add more queries if desired
            self.more_where()

    # Null results
    def null(self):
        # in case only 1 column
        if self.num == 1:
            cont = pyip.inputYesNo(f"Only one column selected: {self.Shelfie7.column}. Proceed?\n")
            if cont == "yes" or cont == "y":
                n_select = ''.join(map(str, self.Shelfie7.syn_columns))
                # choose null or not null
                null_select = pyip.inputMenu(['IS NULL', 'IS NOT NULL'],
                                             "Would you like to filter for or against null results?\n", strip=',',
                                             numbered=True, blank=False)
                # return data
                null_print = f"{n_select} {null_select}, "
                self.where_print += str(null_print)
                # add more queries if desired
                self.more_where()
        else:
            pass
        # multiple columns
        if self.num > 1:
            # get attribute/column to filter
            n_select = pyip.inputMenu(self.Shelfie7.syn_columns, "Which column would you like to filter for "
                                                                 "or against null results?\n", strip=',',
                                      numbered=True, blank=False)
            # choose null or not null
            null_select = pyip.inputMenu(['IS NULL', 'IS NOT NULL'],
                                         "Would you like to filter for or against null results?\n", strip=',',
                                         numbered=True, blank=False)
            # return data
            null_print = f"{n_select} {null_select}, "
            self.where_print += str(null_print)
            # add more queries if desired
            self.more_where()

    # Fix WHERE statement
    def fix_where(self):
        self.where_print = "WHERE " + self.where_print.rstrip(", ")
        self.where_print += "\n"
        return self.where_print


class Having:

    # Declare variables
    def __init__(self, shelfie7):
        self.Shelfie7 = shelfie7
        self.having_print = ""

    # Add HAVING?
    def decide_having(self):
        # prompt
        yesno_having = pyip.inputYesNo("Would you like to add a HAVING statement?\n", blank=True)
        if yesno_having == 'y' or yesno_having == 'yes':
            self.get_having()
        else:
            pass

    # Get order
    def get_having(self):
        # storage
        hav1 = ""
        # count
        count = Counter(self.Shelfie7.columns_all)
        num = sum(count.values())
        # if only 1 column
        if num == 1:
            cont = pyip.inputYesNo(f"Only one column found in table: {self.Shelfie7.column}. Proceed?\n")
            if cont == "yes" or cont == "y":
                hav1 = self.Shelfie7.column
            else:
                pass
        # multiple columns
        if num > 1:
            # get attribute/column
            hav1 = pyip.inputMenu(self.Shelfie7.columns_all, "Please input the value set you'd like to filter "
                                                             "the results by\n", strip=',', numbered=True, blank=False)
        # choose ascending or descending
        hav_results = pyip.inputMenu(["<", "<=", "=", "<>", ">", ">="],
                                     "Please input the number corresponding to the equalize operator.\n",
                                     numbered=True, blank=False)
        # get number
        hav2 = pyip.inputNum("Please input the value.\n", strip=',', blank=True)
        # return data
        self.having_print = f"HAVING COUNT {hav1} {hav_results} {hav2}\n"
        return self.having_print


class Group:

    # Declare variables
    def __init__(self, shelfie7):
        self.Shelfie7 = shelfie7
        self.group_print = ""

    # Group results?
    def decide_group(self):
        yesno_group = pyip.inputYesNo("Would you like to group the results?\n", blank=True)
        if yesno_group == 'y' or yesno_group == 'yes':
            self.get_group()
        else:
            pass

    # Get group
    def get_group(self):
        # storage
        g1_select = ""
        # count
        count = Counter(self.Shelfie7.columns_all)
        num = sum(count.values())
        # if only 1 column
        if num == 1:
            cont = pyip.inputYesNo(f"Only one column found in table: {self.Shelfie7.column}. Proceed?\n")
            if cont == "yes" or cont == "y":
                g1_select = self.Shelfie7.column
            else:
                pass
        # multiple columns
        if num > 1:
            # get attribute/column to group by
            g1_select = pyip.inputMenu(self.Shelfie7.columns_all, "Which column would you like to group by?\n",
                                       strip=',', numbered=True, blank=False)
        # choose asc or desc
        g2_select = pyip.inputMenu(['ASC', 'DESC'],
                                   "Would you like to group in ascending or descending order?\n",
                                   numbered=True, blank=True)
        # return data
        self.group_print = f"GROUP {g1_select} {g2_select}\n"
        return self.group_print


class Union:

    # Declare variables
    def __init__(self):
        self.union_print = ""

    # Union type?
    def decide_union(self):
        union_type = pyip.inputMenu(["UNION", "UNION ALL"], numbered=True, blank=True)
        # return results
        self.union_print = f"{union_type}\n"
        return self.union_print


class FromTable2:

    # Declare variables
    def __init__(self, shelfie3, shelfie4):
        # declare variables
        self.Shelfie3 = shelfie3
        self.Shelfie4 = shelfie4
        self.from_data2 = {}
        self.from_print2 = ""

    # Select FROM table
    def from_select2(self):
        # print tables
        print("Please input the number of the 1st table you'd like to develop a query for.\n")
        for t, table_get in enumerate(self.Shelfie4.tables.keys()):
            print(f"{t + 1}. {table_get}")
        # select FROM table
        f_table = pyip.inputNum(min=1, max=len(self.Shelfie4.tables.keys()), blank=False)
        # match number to table
        from_table = list(self.Shelfie4.tables.keys())[int(f_table) - 1]
        # get first letter
        letter = from_table[0].lower()
        # return data
        self.make_from_dict2(from_table, letter)

    # Get FROM table columns and add everything to a dictionary
    def make_from_dict2(self, from_table, letter):
        # get FROM table columns
        from_columns = []
        for row in self.Shelfie3.cursor.columns(table=from_table):
            from_columns.append(str(row.column_name))
        # create dictionary for join data
        self.from_data2[from_table] = {'column_names': from_columns, 'letter': letter}
        # return data
        self.from_print2 = f"FROM {from_table} AS {letter}\n"
        return self.from_data2, self.from_print2


class SelectColumns2:

    # Declare variables
    def __init__(self, shelfie12):
        self.Shelfie12 = shelfie12
        self.column2 = ""
        self.columns_all2 = []
        self.syn_columns2 = ""
        self.select_print2 = ""

    # Choose columns
    def get_columns2(self):
        # get columns from table
        all_columns = []
        for value in self.Shelfie12.from_data2.values():
            # add to storage for selection
            all_columns.extend(value['column_names'])
        # remove duplicates
        self.columns_all2 = list(set(all_columns))
        return self.columns_all2

    # Prompt
    def prompt2(self):
        # in case only 1 column
        count = Counter(self.columns_all2)
        num = sum(count.values())
        attr = ""
        if num == 1:
            # match column to value in from_data and/or join_data dictionaries
            for from_table in self.Shelfie12.from_data2.values():
                for column_name in from_table["column_names"]:
                    if column_name in str(self.columns_all2):
                        letter = from_table["letter"]
                        self.syn_columns2.append(f"{letter}.{column_name}")
                        attr += f"{column_name}, "
            self.select_print2 = f"{attr}\n"
            return self.select_print2, self.syn_columns2
        if num > 1:
            col_select = pyip.inputMenu(["Select all columns.", "Add name of each column "
                                                                "you'd like to sort by."], numbered=True)
            # select all then exit
            if col_select == "Select all columns.":
                self.select_all2()
            # add individual columns
            if col_select == "Add name of each column you'd like to sort by.":
                self.select_some2()

    # Get all columns
    def select_all2(self):
        # storage
        self.syn_columns2 = []
        # iterate through nested dictionary and get values for "letter" and "column name" for each from_table dictionary
        attr = "*"
        for from_table in self.Shelfie12.from_data2.values():
            for column_name in from_table["column_names"]:
                letter = from_table["letter"]
                self.syn_columns2.append(f"{letter}.{column_name}")
        # check for duplicates
        self.syn_columns2 = list(set(self.syn_columns2))
        # remove the trailing ", " from the end of the string
        attr = attr.rstrip(", ")
        # return data
        self.select_print2 = f"{attr}\n"
        return self.select_print2, self.syn_columns2

    # Select columns
    def select_some2(self):
        # storage
        col_list = []
        self.syn_columns2 = []
        attr = ""
        # prompt
        while True:
            col_select = pyip.inputMenu(self.columns_all2, "Please input the number corresponding "
                                                           "to the columns you'd like to sort by.\n",
                                        self.columns_all2.sort(), strip=',', numbered=True, blank=True)
            col_list.append(col_select)
            if col_select == '':
                break
        # match column to value in from_data and/or join_data dictionaries
        for from_table in self.Shelfie12.from_data2.values():
            for column_name in from_table["column_names"]:
                if column_name in str(col_list):
                    letter = from_table["letter"]
                    self.syn_columns2.append(f"{letter}.{column_name}")
                    attr += f"{column_name}, "
        # check for duplicates
        self.syn_columns2 = list(set(self.syn_columns2))
        # remove the trailing ", " from the end of the string
        attr = attr.rstrip(", ")
        # get attr
        self.column2 = str(attr)
        # return data
        self.select_print2 = f"({attr})\n"
        return self.column2, self.select_print2, self.syn_columns2


class Where2:

    # Declare variables
    def __init__(self, shelfie13):
        self.Shelfie13 = shelfie13
        self.where_print2 = ""
        self.num = 0

    # Add AND, OR, or STOP
    def more_where2(self):
        # prompt
        cont_where = pyip.inputMenu(["Add AND condition.", "Add OR condition."], numbered=True, blank=True)
        if cont_where == "Add AND condition.":
            self.where_print2 += "AND "
            self.add_where2()
        elif cont_where == "Add OR condition.":
            self.where_print2 += "OR "
            self.add_where2()
        elif cont_where == "":
            pass

    def add_where2(self):
        # count
        count = Counter(self.Shelfie13.syn_columns2)
        self.num = sum(count.values())
        # add equality, between, or null statements
        where_query = pyip.inputMenu(["Add equality statement, e.g. >, LIKE, IN, EXISTS, ANY, ALL",
                                      "Add between statement, e.g. Date BETWEEN 24/02/2018 and 05/10/2020.",
                                      "Add null statement, e.g. Purchases IS NOT NULL."],
                                     numbered=True, blank=True)
        if where_query == "Add equality statement, e.g. >, LIKE, IN, EXISTS, ANY, ALL":
            return self.num, self.equality2()
        elif where_query == "Add between statement, e.g. Date BETWEEN 24/02/2018 and 05/10/2020.":
            return self.num, self.between2()
        elif where_query == "Add null statement, e.g. Purchases IS NOT NULL.":
            return self.num, self.null2()
        else:
            pass

    # Equalizers/Booleans/Regex
    def equality2(self):
        # storage
        eq2 = None
        # in case only 1 column
        if self.num == 1:
            cont = pyip.inputYesNo(f"Only one column selected: {self.Shelfie13.column2}. Proceed?\n")
            if cont == "yes" or cont == "y":
                eq1 = ''.join(map(str, self.Shelfie13.syn_columns2))
                # choose operator
                eq_select = pyip.inputMenu(["<", "<=", "=", "<>", ">", ">=", "LIKE", "NOT LIKE", "IN", "NOT IN"],
                                           "Please input the number corresponding to the equalize operator.\n",
                                           numbered=True, blank=False)
                # get second attribute/column/Boolean/value
                eq2_choice = pyip.inputMenu(['TRUE', 'FALSE', 'ANY', 'ALL', 'Date', 'Number', 'Other'],
                                            "Please input the number corresponding to the second value type.\n",
                                            strip=',', numbered=True, blank=False)
                if eq2_choice == "TRUE" or "FALSE" or "ANY" or "ALL":
                    eq2 = eq_select
                if eq2_choice == "Date":
                    eq2 = input("Please enter a date.\n")
                if eq2_choice == "Number":
                    eq2 = pyip.inputNum('Please enter a number.\n', blank=False)
                if eq2_choice == "Other":
                    eq2 = inputMenu("Please input second value.")
                # return data
                equality_print = f"{eq1} {eq_select} {eq2}, "
                self.where_print2 += str(equality_print)
                # add more queries if desired
                self.more_where2()
            else:
                pass
        # more than 1 column
        if self.num > 1:
            # get first attribute/column
            eq1 = pyip.inputMenu(self.Shelfie13.syn_columns2, "Please input the number corresponding "
                                                              "to the first value.\n",
                                 self.Shelfie13.syn_columns2.sort(), strip=',', numbered=True)
            # choose operator
            eq_select = pyip.inputMenu(["<", "<=", "=", "<>", ">", ">=", "LIKE", "NOT LIKE", "IN", "NOT IN"],
                                       "Please input the number corresponding to the equalize operator.\n",
                                       numbered=True, blank=False)
            # get second attribute/column/Boolean/value
            eq2_choice = pyip.inputMenu(['TRUE', 'FALSE', 'ANY', 'ALL', 'Date', 'Number', 'Column', 'Other'],
                                        "Please input the number corresponding to the second value type.\n",
                                        strip=',', numbered=True, blank=False)
            if eq2_choice == "TRUE" or "FALSE" or "ANY" or "ALL":
                eq2 = eq_choice
            if eq2_choice == "Date":
                eq2 = input("Please enter a date.\n")
            if eq2_choice == "Number":
                eq2 = pyip.inputNum('Please enter a number.\n', blank=False)
            if eq2_choice == "Column":
                eq2 = pyip.inputMenu(self.Shelfie13.syn_columns2, "Please input the number corresponding "
                                                                  "to the column.\n",
                                     self.Shelfie13.syn_columns2.sort(), strip=',', numbered=True, blank=False)
            if eq2_choice == "Other":
                eq2 = inputMenu("Please input second value.")
            # return data
            equality_print = f"{eq1} {eq_select} {eq2}, "
            self.where_print2 += str(equality_print)
            # add more queries if desired
            self.more_where2()

    # Between
    def between2(self):
        # storage
        bet2 = None
        bet3 = None
        # in case only 1 column
        if self.num == 1:
            cont = pyip.inputYesNo(f"Only one column selected: {str(self.Shelfie13.column2)}. Proceed?\n")
            if cont == "yes" or cont == "y":
                bet1 = ''.join(map(str, self.Shelfie13.syn_columns2))
                # choose between or not between
                bet_select = pyip.inputMenu(["BETWEEN", "NOT BETWEEN"],
                                            "Please input the number corresponding to the BETWEEN operator.\n",
                                            numbered=True)
                # get second attribute
                bet2_choice = pyip.inputMenu(['Date', 'Number', 'Other'],
                                             "Please input the number corresponding to the first value type.\n",
                                             strip=',', numbered=True, blank=False)
                if bet2_choice == "Date":
                    bet2 = input("Please enter a date.\n")
                if bet2_choice == "Number":
                    bet2 = pyip.inputNum('Please enter a number.\n', blank=False)
                if bet2_choice == "Other":
                    bet2 = input("Please input the first value.\n")
                # get third attribute
                bet3_choice = pyip.inputMenu(['Date', 'Number', 'Other'],
                                             "Please input the number corresponding to the second value type.\n",
                                             strip=',', numbered=True, blank=False)
                if bet3_choice == "Date":
                    bet3 = input("Please enter a date.\n")
                if bet3_choice == "Number":
                    bet3 = pyip.inputNum('Please enter a number.\n', blank=False)
                if bet3_choice == "Column":
                    bet3 = pyip.inputMenu(self.Shelfie13.syn_columns2,
                                          "Please input the number corresponding to the column.\n",
                                          self.Shelfie13.syn_columns2.sort(), strip=',', numbered=True, blank=False)
                if bet2_choice == "Other":
                    bet3 = input("Please input the second value.\n")
                # return data
                between_print = f"{bet1} {bet_select} {bet2} AND {bet3}, "
                self.where_print2 += str(between_print)
                # add more queries if desired
                self.more_where2()
            else:
                pass
        # multiple columns
        if self.num > 1:
            # get first attribute/column
            bet1 = pyip.inputMenu(self.Shelfie13.syn_columns2, "Please input the number corresponding "
                                                               "to the first value.\n",
                                  self.Shelfie13.syn_columns2.sort(), strip=',', numbered=True, blank=False)
            # choose between or not between
            bet_select = pyip.inputMenu(["BETWEEN", "NOT BETWEEN"],
                                        "Please input the number corresponding to the BETWEEN operator.\n",
                                        numbered=True)
            # get second attribute
            bet2_choice = pyip.inputMenu(['Date', 'Number', 'Column', 'Other'],
                                         "Please input the number corresponding to the first value type.\n",
                                         strip=',', numbered=True, blank=False)
            if bet2_choice == "Date":
                bet2 = input("Please enter a date.\n")
            if bet2_choice == "Number":
                bet2 = pyip.inputNum('Please enter a number.\n', blank=False)
            if bet2_choice == "Column":
                bet2 = pyip.inputMenu(self.Shelfie13.syn_columns2, "Please input the number corresponding "
                                                                   "to the column.\n",
                                      self.Shelfie13.syn_columns2.sort(), strip=',', numbered=True, blank=False)
            if bet2_choice == "Other":
                bet2 = input("Please input the first value.\n")
            # get third attribute
            bet3_choice = pyip.inputMenu(['Date', 'Number', 'Column', 'Other'],
                                         "Please input the number corresponding to the second value type.\n",
                                         strip=',', numbered=True, blank=False)
            if bet3_choice == "Date":
                bet3 = input("Please enter a date.\n")
            if bet3_choice == "Number":
                bet3 = pyip.inputNum('Please enter a number.\n', blank=False)
            if bet3_choice == "Column":
                bet3 = pyip.inputMenu(self.Shelfie13.syn_columns2, "Please input the number corresponding "
                                                                   "to the column.\n",
                                      self.Shelfie13.syn_columns2.sort(), strip=',', numbered=True, blank=False)
            if bet2_choice == "Other":
                bet3 = input("Please input the second value.\n")
            # return data
            between_print = f"{bet1} {bet_select} {bet2} AND {bet3}, "
            self.where_print2 += str(between_print)
            # add more queries if desired
            self.more_where2()

    # Null results
    def null2(self):
        # in case only 1 column
        if self.num == 1:
            cont = pyip.inputYesNo(f"Only one column selected: {self.Shelfie13.column2}. Proceed?\n")
            if cont == "yes" or cont == "y":
                n_select = ''.join(map(str, self.Shelfie13.syn_columns2))
                # choose null or not null
                null_select = pyip.inputMenu(['IS NULL', 'IS NOT NULL'],
                                             "Would you like to filter for or against null results?\n", strip=',',
                                             numbered=True, blank=False)
                # return data
                null_print = f"{n_select} {null_select}, "
                self.where_print2 += str(null_print)
                # add more queries if desired
                self.more_where2()
        else:
            pass
        # multiple columns
        if self.num > 1:
            # get attribute/column to filter
            n_select = pyip.inputMenu(self.Shelfie13.syn_columns2, "Which column would you like to filter for "
                                                                   "or against null results?\n", strip=',',
                                      numbered=True, blank=False)
            # choose null or not null
            null_select = pyip.inputMenu(['IS NULL', 'IS NOT NULL'],
                                         "Would you like to filter for or against null results?\n", strip=',',
                                         numbered=True, blank=False)
            # return data
            null_print = f"{n_select} {null_select}, "
            self.where_print2 += str(null_print)
            # add more queries if desired
            self.more_where2()

    # Fix WHERE statement
    def fix_where2(self):
        self.where_print2 = "WHERE " + self.where_print2.rstrip(", ")
        self.where_print2 += "\n"
        return self.where_print2


class Having2:

    # Declare variables
    def __init__(self, shelfie13):
        self.Shelfie13 = shelfie13
        self.having_print2 = ""

    # Add HAVING?
    def decide_having2(self):
        yesno_having = pyip.inputYesNo("Would you like to add a HAVING statement?\n", blank=True)
        if yesno_having == 'y' or yesno_having == 'yes':
            self.get_having2()
        else:
            pass

    # Get order
    def get_having2(self):
        # storage
        hav1 = ""
        # count
        count = Counter(self.Shelfie13.syn_columns2)
        num = sum(count.values())
        # if only 1 column
        if num == 1:
            cont = pyip.inputYesNo(f"Only one column found in table: {self.Shelfie13.column2}. Proceed?\n")
            if cont == "yes" or cont == "y":
                hav1 = self.Shelfie13.column2
            else:
                pass
        # multiple columns
        if num > 1:
            # get attribute/column
            hav1 = pyip.inputMenu(self.Shelfie13.columns_all2, "Please input the value set you'd like to filter "
                                                               "the results by\n", strip=',',
                                  numbered=True, blank=False)
        # choose ascending or descending
        hav_results = pyip.inputMenu(["<", "<=", "=", "<>", ">", ">="],
                                     "Please input the number corresponding to the equalize operator.\n",
                                     numbered=True, blank=False)
        # get number
        hav2 = pyip.inputNum("Please input the value.\n", strip=',', blank=True)
        # return data
        self.having_print2 = f"HAVING COUNT {hav1} {hav_results} {hav2}\n"
        return self.having_print2


class Group2:

    # Declare variables
    def __init__(self, shelfie13):
        self.Shelfie13 = shelfie13
        self.group_print2 = ""

    # Group results?
    def decide_group2(self):
        yesno_group = pyip.inputYesNo("Would you like to group the results?\n", blank=True)
        if yesno_group == 'y' or yesno_group == 'yes':
            self.get_group2()
        else:
            pass

    # Get group
    def get_group2(self):
        # storage
        g1_select = ""
        # count
        count = Counter(self.Shelfie13.syn_columns2)
        num = sum(count.values())
        # if only 1 column
        if num == 1:
            cont = pyip.inputYesNo(f"Only one column found in table: {self.Shelfie13.column2}. Proceed?\n")
            if cont == "yes" or cont == "y":
                g1_select = self.Shelfie13.column2
            else:
                pass
        # multiple columns
        if num > 1:
            # get attribute/column to group by
            g1_select = pyip.inputMenu(self.Shelfie13.columns_all2, "Which column would you like to group by?\n",
                                       strip=',', numbered=True, blank=False)
        # choose asc or desc
        g2_select = pyip.inputMenu(['ASC', 'DESC'],
                                   "Would you like to group in ascending or descending order?\n",
                                   numbered=True, blank=True)
        # return data
        self.group_print2 = f"GROUP {g1_select} {g2_select}\n"
        return self.group_print2


class Order:

    # Declare variables
    def __init__(self, shelfie7, shelfie13):
        self.Shelfie7 = shelfie7
        self.Shelfie13 = shelfie13
        self.order_print = ""

    # Order results?
    def decide_order(self):
        yesno_order = pyip.inputYesNo("Would you like to order the results?\n", blank=True)
        if yesno_order == 'y' or yesno_order == 'yes':
            self.get_order()
        else:
            pass

    # Get order
    def get_order(self):
        # storage
        t_columns = []
        for columns in self.Shelfie7.columns_all:
            t_columns.append(columns)
        for columns in self.Shelfie13.columns_all2:
            t_columns.append(columns)
        # remove duplicates
        t_columns = list(set(t_columns))
        # get attribute/column to order results
        or1 = pyip.inputMenu(t_columns,
                             "Please input the value set you'd like to order the results by\n",
                             t_columns.sort(), strip=',', numbered=True, blank=True)
        # choose ascending or descending
        order_results = pyip.inputMenu(["ASC", "DESC"], "Please input the number "
                                                        "corresponding to the method of ordering results.\n",
                                       numbered=True, blank=False)
        # return data
        self.order_print = f"ORDER BY {or1} {order_results}\n"
        return self.order_print


class Top:

    # Declare values
    def __init__(self):
        self.top_print = ""

    # Limit results
    def get_top(self):
        # decide if results should be limited
        yesno_limit = pyip.inputYesNo("Would you like to limit the results?\n", blank=True)
        if yesno_limit == 'y' or yesno_limit == 'yes':
            # decide limit
            limit_num = pyip.inputNum("Please input the max number of results you'd like to obtain.\n",
                                      min=1, max=10000000, blank=False)
            print("\n")
            # return data
            self.top_print = f"SELECT TOP ({limit_num})\n"
            return self.top_print
        else:
            pass


class PrintQuery:

    # Declare values
    def __init__(self, shelfie5, shelfie6, shelfie7, shelfie8, shelfie9, shelfie10, shelfie11, shelfie12,
                 shelfie13, shelfie14, shelfie15, shelfie16, shelfie17, shelfie18):
        self.Shelfie5 = shelfie5
        self.Shelfie6 = shelfie6
        self.Shelfie7 = shelfie7
        self.Shelfie8 = shelfie8
        self.Shelfie9 = shelfie9
        self.Shelfie10 = shelfie10
        self.Shelfie11 = shelfie11
        self.Shelfie12 = shelfie12
        self.Shelfie13 = shelfie13
        self.Shelfie14 = shelfie14
        self.Shelfie15 = shelfie15
        self.Shelfie16 = shelfie16
        self.Shelfie17 = shelfie17
        self.Shelfie18 = shelfie18

    # Print
    def print_query(self):
        results = f"{self.Shelfie18.top_print}" \
                  f"SELECT {self.Shelfie7.select_print}" \
                  f"{self.Shelfie5.from_print}" \
                  f"{self.Shelfie6.join_print}" \
                  f"{self.Shelfie8.where_print}" \
                  f"{self.Shelfie9.having_print}" \
                  f"{self.Shelfie10.group_print}" \
                  f"{self.Shelfie17.order_print}"
        print(results)

    # Print with union
    def print_query2(self):
        results2 = f"{self.Shelfie18.top_print}" \
                   f"SELECT {self.Shelfie7.select_print}" \
                   f"{self.Shelfie5.from_print}" \
                   f"{self.Shelfie6.join_print}" \
                   f"{self.Shelfie8.where_print}" \
                   f"{self.Shelfie9.having_print}" \
                   f"{self.Shelfie10.group_print}" \
                   f"{self.Shelfie11.union_print}" \
                   f"SELECT {self.Shelfie13.select_print2}" \
                   f"{self.Shelfie12.from_print2}" \
                   f"{self.Shelfie14.where_print2}" \
                   f"{self.Shelfie15.having_print2}" \
                   f"{self.Shelfie16.group_print2}" \
                   f"{self.Shelfie17.order_print}"
        print(results2)


# Define object
Shelfie1 = MakeShelf()
Shelfie2 = ServerFile()
Shelfie3 = SQLConnect(Shelfie2)
Shelfie4 = SQLData(Shelfie3)
Shelfie5 = FromTable(Shelfie3, Shelfie4)
Shelfie6 = JoinTable(Shelfie3, Shelfie4, Shelfie5)
Shelfie7 = SelectColumns(Shelfie5, Shelfie6)
Shelfie8 = Where(Shelfie7)
Shelfie9 = Having(Shelfie7)
Shelfie10 = Group(Shelfie7)
Shelfie11 = Union()
Shelfie12 = FromTable2(Shelfie3, Shelfie4)
Shelfie13 = SelectColumns2(Shelfie12)
Shelfie14 = Where2(Shelfie13)
Shelfie15 = Having2(Shelfie13)
Shelfie16 = Group2(Shelfie13)
Shelfie17 = Order(Shelfie7, Shelfie13)
Shelfie18 = Top()
Shelfie19 = PrintQuery(Shelfie5, Shelfie6, Shelfie7, Shelfie8, Shelfie9, Shelfie10, Shelfie11, Shelfie12,
                       Shelfie13, Shelfie14, Shelfie15, Shelfie16, Shelfie17, Shelfie18)


def main():
    # check if shelf exists: if it does - pass and open shelf file, if it doesn't - create one with server_file()
    Shelfie1.is_shelf_exist()
    # check if this is the right database - pass, if not then edit shelf file
    Shelfie2.access_database()
    # create connection string
    Shelfie3.create_string()
    # connect to server
    Shelfie3.connect()
    # get tables
    Shelfie4.get_tables()
    # get from table data
    Shelfie5.from_select()
    # get join tables
    Shelfie6.decide_join()
    # create join statement
    Shelfie6.construct_join_statement()
    # get columns to select by
    Shelfie7.get_columns()
    # decide how to compile select
    Shelfie7.prompt()
    # create where statements
    Shelfie8.add_where()
    Shelfie8.fix_where()
    # get having
    Shelfie9.decide_having()
    # get group
    Shelfie10.decide_group()
    # add union?
    yesno_union = pyip.inputYesNo("Would you like to add a UNION statement?\n", blank=True)
    if yesno_union == 'y' or yesno_union == 'yes':
        # add union statement
        Shelfie11.decide_union()
        # get from table data
        Shelfie12.from_select2()
        # get columns to select by
        Shelfie13.get_columns2()
        # decide how to compile select
        Shelfie13.prompt2()
        # create where statements
        Shelfie14.add_where2()
        Shelfie14.fix_where2()
        # get having
        Shelfie15.decide_having2()
        # get group
        Shelfie16.decide_group2()
        # get order statement
        Shelfie17.decide_order()
        # decide to limit results
        Shelfie18.get_top()
        # print query
        Shelfie19.print_query2()
    else:
        # get order statement
        Shelfie17.decide_order()
        # decide to limit results
        Shelfie18.get_top()
        # print query
        Shelfie19.print_query()


if __name__ == "__main__":
    main()
