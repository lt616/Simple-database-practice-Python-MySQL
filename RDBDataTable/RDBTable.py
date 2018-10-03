# COMP4111 Assignment 01 - RDBTable class implementation  
# Author: Qianrui Zhao      ID: qz2338 
# Any question please contact qz2338@columbia.edu 

import pymysql 
import csv 
import sys 
import os 

class RDBTable:
    # You can change to wherever you want to place your CSV files.
    current_path = os.getcwd()
    rel_path = os.path.realpath(current_path[:len(current_path) - 12] + "Data") 
    
    def __init__(self, t_name, t_file, primary_key_columns, connect_info):
        self.t_name = t_name
        self.t_file = self.rel_path + "/" + t_file 
        self.modified = False
        self.columns = None
        self.rows = None 
        self.primary_key_columns = primary_key_columns 
        self.key_columns = [] 
        
        # Connect to db 
        try: 
            self.cnx = pymysql.connect(host=connect_info['localhost'],
                              user=connect_info['dbuser'],
                              password=connect_info['password'],
                              db=connect_info['dbname'],
                              charset='utf8mb4', 
                              cursorclass=pymysql.cursors.DictCursor) 
        except: 
            print("Error: Authentication failed. ") 
            sys.exit(0) 

        self.cursor = self.cnx.cursor() 
        
        # Check if file exist 
        if not os.path.isfile(self.t_file): 
            print("Error: " + self.t_file + " is not a valid file") 
            sys.exit(0) 
        
        # Drop existing table if exist 
        # self.cursor.execute("DROP TABLE " + self.t_name + ";") 
        # self.cnx.commit() 
        
        # store key columns 
        with open(self.t_file) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',') 
            
            for row in csv_reader:                 
                for key in row: 
                    self.key_columns.append(key) 
                break 

        # check if primary key columns are valid 
        self.validate_fields(primary_key_columns) 
        self.primary_key_columns = primary_key_columns  


    def load(self): 
        is_t_created = False 

        # Read in data ad insert db 
        with open(self.t_file) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')                     

            for row in csv_reader: 
                # Create db_t 
                if not is_t_created: 
                    query = "CREATE TABLE " + self.t_name + "(" 
                    for key in row: 
                        # Create table column key 
                        query += key + " varchar(100), " 
                        self.key_columns.append(key) 

                    # Add primary keys constraint 
                    query += "CONSTRAINT " + self.t_name + "PK PRIMARY KEY (" 
                    for pk in self.primary_key_columns:  
                        query += pk + ", " 
                    query = query[:len(query) - 2] + "));" 

                    self.query_without_res(query)                     
                    print("Create table " + self.t_name + " successfully.") 
                    print("Loading data from files ..") 
                    is_t_created = True  
                
                query = self.construct_insert_query(row) 

                self.query_without_res(query)            


    def save(self):
        '''
        Write updated CSV back to the original file location.
        :return: None
        ''' 
        try: 
            with open(self.t_file, 'w') as csvfile: 
                csv_writer = csv.writer(csvfile) 
                self.cursor.execute("SELECT * FROM " + self.t_name + ";")  
                res = self.cursor.fetchall() 

                self.cnx.commit() 

                csv_writer.writerow(self.key_columns) 
                for row in res: 
                    csv_writer.writerow(self.check_row(row))  
        except Exception as e:
            print(e) 
            sys.exit(0)     

    def find_by_primary_key(self, values, selected_key_columns): 

        # Check if primary keys valid 
        if not len(values) == len(self.primary_key_columns): 
            print("Error: Invalid primary keys.") 
            sys.exit(0) 

        # Check if fields valid 
        self.validate_fields(selected_key_columns) 

        primary_keys = {} 
        for i in range(len(values)): 
            primary_keys[self.primary_key_columns[i]] = values[i] 

        res = self.select(primary_keys, selected_key_columns, False) 
        return res[0]


    def find_by_template(self, template, fields): 

        if template is {}: 
            self.select(template, fields, True)

        # Check if template and fields are valid 
        self.validate_fields(template.keys()) 
        self.validate_fields(fields) 

        return self.select(template, fields, False) 


    def select(self, template, fields, is_select_all): 
        query = "SELECT " 
        for field in fields: 
            query += field + ", " 
        query = query[:len(query) - 2] + " FROM " + self.t_name

        # If template is empty, select all from table 
        if is_select_all: 
            query += ";" 
            return self.query_with_res(query) 

        query += " WHERE " 
        for key, value in template.items(): 
            value = str(value) 
            value = value.replace('"', '\"') 
            value = value.replace("'", "\\\'") 
            query += key + " = '" +  value + "' AND " 
        query = query[:len(query) - 5] + ";" 

        return self.query_with_res(query) 


    def insert(self, row): 
        query = self.construct_insert_query(row) 
        self.query_without_res(query) 


    def delete(self, template): 

        # Check if template valid 
        self.validate_fields(template); 

        # Construct delete query 
        query = "DELETE FROM " + self.t_name

        if template is {}: 
            query += ";" 
            self.query_without_res(query) 
            return 

        query += " WHERE " 
        for key, value in template.items(): 
            query += key + " = '" + str(value) + "' AND " 
        query = query[:len(query) - 5] + ";" 

        self.query_without_res(query) 
    
    
    def construct_insert_query(self, row): 
        key_set = "" 
        value_set = "" 
        
        for key, value in row.items():
            key_set += ", " + key 
            value = value.replace('"', '\\\"')      # FEATURE escape special characters 
            value = value.replace("'", '\\\'') 
            value_set += ", '" + value + "'" 
        query = "INSERT INTO " + self.t_name + " (" + key_set[2:] + ") VALUES (" + value_set[2:] + ");" 
        
        return query 


    def query_with_res(self, query): 
        try: 
            self.cursor.execute(query) 
            res = self.cursor.fetchall() 

            self.cnx.commit() 

            return res 
        except pymysql.err.ProgrammingError as e: 
            print("Error: Table does not exist.") 
            sys.exit(0) 
        
    
    def query_without_res(self, query): 
        try: 
            self.cursor.execute(query) 
            self.cnx.commit() 
        except pymysql.err.IntegrityError as e: 
            print("Error: Duplicate primary key values.") 
            sys.exit(0) 
        except pymysql.err.ProgrammingError as e: 
            print("Error: Table does not exist.") 
            sys.exit(0) 


    def check_row(self, row): 
        new_row = []  
        for key in self.key_columns: 
            if key in row: 
                new_row.append(row[key])
            else: 
                new_row.append("")
        return new_row 


    def validate_fields(self, fields): 
        for field in fields: 
            if not field in self.key_columns: 
                print("Error: Invalid fields.") 
                sys.exit(0) 
    
    
    def validate_primary_keys(self, row, key_set): 
        for key in row: 
            if not key in key_set: 
                print("Error: Invalid primary keys.") 
                sys.exit(0) 

