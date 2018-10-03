# Simple-database-practice-Python-MySQL 

Author: Qianrui Zhao         ID: qz2338 
Any question please contact qz2338@columbia.edu 

Read data from CSV files and store it as a database. The data provide basic CRUD operators just as normal database. 
I developed two implementations, the first database class is implemented in python, and the second one in MySQL. 
And then understand why we need database techs like MySQL :) 

# 1. Tips for running the code: 
0). The test output is showed in "test_CSV_result.txt" & "test_RDB_result.txt". 

1). I do implement load() & save() for both classes. 
The input primary key fields are validated in class initialization phase, but the data is loaded in load(). 

So after initialize the class, call load() to REALLY import the data. 

Same thing for save(). After insert() / delete() some rows, the data stored in class (for RDBTable class it is the MySQL table) is updated immediately, but you need save() to update the CSV files. 

2). What find_by_primary_key() & find_by_template() return is an array of dictionaries. 

3). My implementation doesn't support cross-table correctness. Which means relation between two table instances does not exist. But it is not required in this assignment.  

4). There are some delete() call tests in my test files, which will alter data in CSV files. So I use a "people_test_CSV/RDB.csv" file to run the tests to maintain the integrity of "People.csv" file, ensuring that top_10_hitter programs will always work on the correct input data. 

# 2. Design for CSVTable class: 
1). Primary key values are maintained by iterative dictionaries to provide O(1) primary key access. 

e.g. primary key = {"playerID", "Height", "Weight"} 

data structure for saving primary key value {"playerID" : '007', "Height" : '160'", "Weight" : '100'} is 

{'007' : {'160' : '100': {index}}} 

the index is an automatic increasing number and is sured to be non-repeated. 

Pons: O(1) time complexity for seaching by primary key. I think this design is important. Primary key search operator is called in high frequency since we need not only in find_by _primary_key(), but also every time before insert a new entryto check if there is a duplicate primary key.  
Cons: Extra memory cost for maintaining this structure. 

2). All data are maintained in a dictionary where the key is the index. The index is also include in the value as a column. 

e.g. {index_000: {"index": index_1000, "playerID": '007', "Height" : '160', "Weight" : '100'}} 

When searching by template, it has to match every entry in the dictionary. The time complexity is O(n). 


# 3. Design for RDBTable class: 
The design for RDBTable class is pretty straightforward. A table is created in MySQL and the primary keys are specified as a constraint during table construction. 


# 4. Correctness rules (Applied to both CSVTable and RDBTable implementation)

1). Inserting a duplicate primary key is forbidden. 
The principle is also work during data loading phrase. 

2). Primary key must be valid. 

3). All key specified in template and target fields must be valid. 

4). In find_by_template() function, if the input template is empty then seach all by default. 







