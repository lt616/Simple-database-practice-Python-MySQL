# COMP4111 Assignment 01 - CSVTable class implementation  
# Author: Qianrui Zhao      ID: qz2338 
# Any question please contact qz2338@columbia.edu 

import csv          # Python package for reading and writing CSV files.
import copy         # Copy data structures.


import sys
import os

# You can change to wherever you want to place your CSV files.
current_path = os.getcwd()
rel_path = os.path.realpath(current_path[:len(current_path) - 12] + "Data"); 

class CSVTable():

    def __init__(self, table_name, table_file, primary_key_columns):
        '''
        Constructor
        :param table_name: Logical names for the data table.
        :param table_file: File name of CSV file to read/write.
        :param key_columns: List of column names the form the primary key.
        ''' 
        self.data_dir = rel_path + "/"
        
        self.current_index = 0
        self.key_columns = []
        self.db_values = {} 

        self.table_name = table_name 
        self.file_name = self.data_dir + table_file 
        self.primary_key_columns = [] 
        self.primary_key_values = {} 

        # check if file exist 
        if not os.path.isfile(self.file_name): 
            print("Error: " + self.file_name + " is not a valid file") 
            sys.exit(0) 

        # initial key columns 
        with open(self.file_name) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',') 
            
            for row in csv_reader:                     
                self.key_columns.append("Index") 
                for key in row: 
                    self.key_columns.append(key) 
                break 

        # check if input primary key columns are valid 
        self.validate_fields(primary_key_columns) 
        self.primary_key_columns = primary_key_columns  
                        

    def __str__(self):
        '''
        Pretty print the table and state.
        :return: String
        ''' 
        res = ""
        
        for key_name in self.key_columns: 
            res += key_name + "\t" 
        res += "\n" 
        
        for index, row in self.db_values.items(): 
            res += str(index) + "\t"
            
            for key in row:
                res += str(row[key]) + "\t"
            
            res += "\n" 
        
        return res
    

    def load(self):
        '''
        Load information from CSV file.
        :return: None
        ''' 
        self.db_values = {} 
        self.primary_key_values.clear() 

        # Read data line by line and insert into db 
        with open(self.file_name) as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',') 
            
            for row in csv_reader: 
                
                pre, value = self.check_primary_key(row) 
                if pre is None:
                    continue 
                
                pre[value] = self.current_index 
                
                self.insert_row(row)


    def find_by_primary_key(self, values, fields): 
        if not len(values) == len(self.primary_key_columns): 
            print("Error: Invalid number of primary key values") 
            sys.exit(0) 

        self.validate_fields(fields)
        
        # find index of target row by searching primary key values 
        temp = self.primary_key_values 
        for value in values: 
            if not value in temp: 
                return None 
            temp = temp[value] 
        
        # access target row using index 
        res = {} 
        for field in fields: 
            res[field] = self.db_values[temp][field] 
        
        return res
        

    def find_by_template(self, t, fields):
        '''
        Return a table containing the rows matching the template and field selector.
        :param t: Template that the rows much match.
        :param fields: A list of columns to include in responses.
        :return: A list containing the answer. 
        ''' 
        # validate inputs 
        self.validate_template(t)
        self.validate_fields(fields)
        
        # Find Match Rows 
        res = [] 
        for index in self.db_values: 
            row = self.db_values[index] 
            
            if self.match(row, t): 
                res.append(self.construct_row(row, fields)) 
                       
        return res

    def save(self):
        '''
        Write updated CSV back to the original file location.
        :return: None
        ''' 
        
        try: 
            with open(self.file_name, 'w') as csvfile: 
                csv_writer = csv.writer(csvfile) 
                csv_writer.writerow(self.key_columns[1:]) 
                for index, row in self.db_values.items(): 
                    csv_writer.writerow(self.check_row(row)) 
        except Exception as e:
            print(e) 
            sys.exit(0) 
        

    def insert(self, r):
        '''
        Insert a new row into the table.
        :param r: New row.
        :return: None. Table state is updated. 
        ''' 
        
        self.validate_template(r) 
        
        # If primary key duplicate 
        pre, value = self.check_primary_key(r) 
        if pre is None:
            return
        
        pre[value] = self.current_index
        self.insert_row(r)

    
    def delete(self, t):
        '''
        Delete all tuples matching the template.
        :param t: Template
        :return: None. Table is updated.
        ''' 
        
        self.validate_template(t) 
        
        # Find Match Rows 
        res = [] 
        dict_res = [] 
        for index in self.db_values: 
            row = self.db_values[index] 
            
            if self.match(row, t): 
                res.append(self.check_row(row)) 
                dict_res.append(row)
        
        # Delete primary key and row in db 
        for row_to_delete in dict_res:
            index = self.delete_primary_key(row_to_delete) 
            self.delete_row(index)
    
    
    #### Helper func 
    def match(self, row, t): 
        for key, value in t.items(): 
            if not str(value) == row[key]:
                return False 
        return True 
    
    
    def construct_row(self, row, fields): 
        new_row = {} 
        for field in fields: 
            new_row[field] = row[field] 

        return new_row 

    
    def validate_template(self, t): 
        # If field in template does not exist         
        for key in t: 
            if not key in self.key_columns: 
                print("Error: Invalid template.") 
                sys.exit(0)

    
    def validate_fields(self, fields):          
        # If field in fields does not exist 
        for field in fields: 
            if not field in self.key_columns: 
                print("Error: Invalid fields") 
                sys.exit(0)

    
    def check_primary_key(self, row): 
        # Insert primary key 
        temp = self.primary_key_values 
        for key in self.primary_key_columns: 
            if not key in row: 
                print("Error: Incomplete primary keys.") 
                sys.exit(0) 
            value = row[key] 
            pre = temp 
            if not value in temp: 
                temp[value] = {} 
            temp = temp[value] 
        # If primary key already exist, print Error Message and continue 
        if pre[value]: 
            print("Error: Primary key for row " + str(row) + " already exist.") 
            print("Abondon invalid row ..") 
            sys.exit(0) 
                
        return pre, value 

    
    def check_row(self, row): 
        new_row = []  
        for key in self.key_columns: 
            if key in row: 
                new_row.append(row[key])
            else: 
                new_row.append("")
        return new_row[1:] 
    
    
    def insert_row(self, row): 
        # Insert db values 

        self.db_values[self.current_index] = row
        self.current_index += 1
    
    
    def delete_primary_key(self, row): 
        temp = self.primary_key_values 
        for key in self.primary_key_columns[:len(self.primary_key_columns) - 1]: 
            temp = temp[row[key]] 
        res = temp[row[self.primary_key_columns[-1]]] 
        temp[row[self.primary_key_columns[-1]]] = {} 

        return res 
    
    
    def delete_row(self, res): 
        del self.db_values[res]


