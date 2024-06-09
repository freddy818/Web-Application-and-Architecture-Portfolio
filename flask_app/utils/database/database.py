import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
import requests
import datetime
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users']
        self.login_attempts = 0
        self.sign_up_attempt = 0
        self.word_of_the_day = ""
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row
    
    def about(self, nested=False):    
        query = """select concat(col.table_schema, '.', col.table_name) as 'table',
                          col.column_name                               as column_name,
                          col.column_key                                as is_key,
                          col.column_comment                            as column_comment,
                          kcu.referenced_column_name                    as fk_column_name,
                          kcu.referenced_table_name                     as fk_table_name
                    from information_schema.columns col
                    join information_schema.tables tab on col.table_schema = tab.table_schema and col.table_name = tab.table_name
                    left join information_schema.key_column_usage kcu on col.table_schema = kcu.table_schema
                                                                     and col.table_name = kcu.table_name
                                                                     and col.column_name = kcu.column_name
                                                                     and kcu.referenced_table_schema is not null
                    where col.table_schema not in('information_schema','sys', 'mysql', 'performance_schema')
                                              and tab.table_type = 'BASE TABLE'
                    order by col.table_schema, col.table_name, col.ordinal_position;"""
        results = self.query(query)
        if nested == False:
            return results

        table_info = {}
        for row in results:
            table_info[row['table']] = {} if table_info.get(row['table']) is None else table_info[row['table']]
            table_info[row['table']][row['column_name']] = {} if table_info.get(row['table']).get(row['column_name']) is None else table_info[row['table']][row['column_name']]
            table_info[row['table']][row['column_name']]['column_comment']     = row['column_comment']
            table_info[row['table']][row['column_name']]['fk_column_name']     = row['fk_column_name']
            table_info[row['table']][row['column_name']]['fk_table_name']      = row['fk_table_name']
            table_info[row['table']][row['column_name']]['is_key']             = row['is_key']
            table_info[row['table']][row['column_name']]['table']              = row['table']
        return table_info



    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        #list of tables
        table_list = ['institutions', 'positions', 'experiences', 'skills', 'feedback', 'users', 'leaderboard', 'word']

        #list of column titles
        col_list = [["inst_id","type","name","department","address","city","state","zip"], 
                    ["position_id","inst_id","title","responsibilities","start_date","end_date"], 
                    ["experience_id", "position_id", "name", "description", "hyperlink", "start_date", "end_date"],
                    ["skill_id", "experience_id", "name", "skill_level"]]
        for t in table_list:
            #open these files and perform self.query on it
            with open(f"{data_path}/create_tables/{t}.sql", 'r') as file:
                self.query(file.read())

        #for each title in the table list, open a corresponding csv file
        for i in range(len(table_list)-4):
            with open(f"{data_path}/initial_data/{table_list[i]}.csv", 'r') as file:
                reader = csv.reader(file)
                col = col_list[i]
                rows = list(reader)[1:]
                #converting all data to its property data type
                for j in range(len(rows)):
                    if i == 0:
                        rows[j][0] = int(rows[j][0])
                    elif i == 1:
                        rows[j][0] = int(rows[j][0])
                        rows[j][1] = int(rows[j][1])
                    elif i == 2:
                        rows[j][0] = int(rows[j][0])
                        rows[j][1] = int(rows[j][1])
                    elif i == 3:
                        rows[j][0] = int(rows[j][0])
                        rows[j][1] = int(rows[j][1])
                        rows[j][3] = int(rows[j][3])
                #call insert rows with these parameters
                self.insertRows(table = table_list[i], columns=col, parameters=rows)


    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        col = ','.join(columns) #create string
        val = ','.join(['%s'] * len(columns)) #list of placeholders
        
        qry = f"INSERT IGNORE INTO {table} ({col}) VALUES ({val})"
       
        for row in parameters: #for each row in parameters call self.query on that row with the query above
            self.query(qry, row)
            

    def getResumeData(self):
        resumeData = {} #initialize a dictionary
        #call these queries
        instData = self.query("SELECT * FROM institutions") 
        posData = self.query("SELECT * FROM positions")
        expData = self.query("SELECT * FROM experiences")
        skillData = self.query("SELECT * FROM skills")
        for instDict in instData: #for each dictionary in the instData
            if instDict['inst_id'] not in resumeData:
                resumeData[instDict['inst_id']] = {} #set the resumeData at this key to be an empty dictionary
                #add these keys and values at the outer dictionary's specified key
                resumeData[instDict['inst_id']]['address'] = instDict['address']
                resumeData[instDict['inst_id']]['city'] = instDict['city']
                resumeData[instDict['inst_id']]['state'] = instDict['state']
                resumeData[instDict['inst_id']]['type'] = instDict['type']
                resumeData[instDict['inst_id']]['zip'] = instDict['zip']
                resumeData[instDict['inst_id']]['department'] = instDict['department']
                resumeData[instDict['inst_id']]['name'] = instDict['name']
                resumeData[instDict['inst_id']]['positions'] = {}
                for posDict in posData: #pretty much works the same as the outer loop, just at different keys in values, the key values for this are dependent on the dictionaries in posData
                    if posDict['inst_id'] == instDict['inst_id']:
                        resumeData[instDict['inst_id']]['positions'][posDict['position_id']] = {}
                        resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['end_date'] = posDict['end_date']
                        resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['responsibilities'] = posDict['responsibilities']
                        resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['start_date'] = posDict['start_date']
                        resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['title'] = posDict['title']
                        resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['experiences'] = {}
                        for expDict in expData:
                            #again works similar to the prior loop, just the key, values being inserted are dependent on the dicts in expData
                            if expDict['position_id'] == posDict['position_id']:
                                resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['experiences'][expDict['experience_id']] = {}
                                resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['experiences'][expDict['experience_id']]['description'] = expDict['description']
                                resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['experiences'][expDict['experience_id']]['end_date'] = expDict['end_date']
                                resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['experiences'][expDict['experience_id']]['hyperlink'] = expDict['hyperlink']
                                resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['experiences'][expDict['experience_id']]['name'] = expDict['name']
                                resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['experiences'][expDict['experience_id']]['skills'] = {}
                                #again works similar to prior loop, just key, values inserted are dependent on the dicts in skillData
                                for skillDict in skillData:
                                    if skillDict['experience_id'] == expDict['experience_id']:
                                        resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['experiences'][expDict['experience_id']]['skills'][skillDict['skill_id']] = {}
                                        resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['experiences'][expDict['experience_id']]['skills'][skillDict['skill_id']]['name'] = skillDict['name']
                                        resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['experiences'][expDict['experience_id']]['skills'][skillDict['skill_id']]['skill_level'] = skillDict['skill_level']
                                resumeData[instDict['inst_id']]['positions'][posDict['position_id']]['experiences'][expDict['experience_id']]['start_date'] = expDict['start_date']

        #return the final 
        return resumeData

    def getFeedback(self):
        return self.query("SELECT * from feedback")
    

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        qry = self.query("SELECT * from users")


        #if someone tried entering an empty password, just instantly return failure
        if password == "":
            return {'success': 0}
        

        password = self.onewayEncrypt(password)

        #use a set to store emails so no repeats
        email_list = set()

        #add to the set of emails
        for row in qry:
            email_list.add(row['email'])
        
        #creating the paramters for insert rows
        parameters = [[email,password,role, 0, 0]]
        cols = ['email', 'password', 'role', 'wordle_visits', 'completed_game']


        #Make sure that the email has not already been used nor is it just an empty string or a bunch of spaces
        if email not in email_list and email.strip() != "":
            #insert rows, success: 1 indicates success, 0 is fail
            self.insertRows(table = 'users', columns = cols, parameters=parameters)
            return {'success' : 1}
        else:
            return {'success' : 0}

    def authenticate(self, email='me@email.com', password='password'):
        qry = self.query("SELECT * FROM users")
        for row in qry:
            #if the email is the same
            if row['email'] == email:
                #check if the password works
                if row['password'] == self.onewayEncrypt(password):
                    #reset the amt of attempts if successful
                    self.login_attempts = 0
                    return {'success': 1}
        #increase attempts if unsuccessful
        self.login_attempts += 1
        return {'success': 0}

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message
    
#######################################################################################
# Final exam
#######################################################################################


    #a function that lets me get the amount of times a user has visited the wordle page from the data table
    def timesVisited(self, user):
        qry = self.query("SELECT * FROM users")
        for row in qry:
            if user == row['email']:
                return row['wordle_visits']
            
    # add to that column in the user's row in the data table if they have visited the site
    def addVisit(self, user):

        params = (user,)
        self.query( "UPDATE users SET wordle_visits = wordle_visits + 1 WHERE email = %s", params)

    # function to update the data table if a user has completed the game
    def completedGame(self, user):
        qry = self.query("SELECT * FROM users")
        params = (user,)
        for row in qry:
            if user == row['email']:
                self.query( "UPDATE users SET completed_game = completed_game + 1 WHERE email = %s", params)

    # function to get whether or not the user has played the game from the data table
    def getCompletedGame(self, user):
        qry = self.query("SELECT * FROM users")
        for row in qry:
            if user == row['email']:
                return row['completed_game']


    # add to the leaderboard 
    def addToLeaderboard(self, email, time):
                
        #creating the paramters for insert rows
        parameters = [[email,time]]
        cols = ['email', 'time']
    
        self.insertRows(table = 'leaderboard', columns = cols, parameters=parameters)

    # return the leader board data as a dictionary where dict['xxx@email'] = time
    def getLeaderboardData(self):
        qry = self.query("SELECT * FROM leaderboard")

        data = {}

        for leaderboardDict in qry:
            data[leaderboardDict['email']] = leaderboardDict['time']
        return data
    
    # function to get the daily word
    def getword(self):

        url = "https://random-word-by-api-ninjas.p.rapidapi.com/v1/randomword"

        querystring = {"type":"verb, adjective, noun"}

        headers = {
            "X-RapidAPI-Key": "ecd2152f85msha845931e39876b5p188823jsnd67ace51e7dd",
            "X-RapidAPI-Host": "random-word-by-api-ninjas.p.rapidapi.com"
        }

        # request from the api a random word
        qry = self.query("SELECT * FROM word")

        # if the word data base is empty
        if len(qry) == 0:

            # request a random word from the api and store it in a variable
            word = requests.get(url, headers=headers, params=querystring, verify=False)
            word = word.json()['word']

            # make sure that the word being returned is going to 
            while not word.isalpha():
                word = requests.get(url, headers=headers, params=querystring)
                word = word.json()['word']

            # insert into the data table the date, and then the word
            params = (datetime.date.today(), word,)
            self.query("INSERT INTO word (date, word) VALUES (%s, %s)", params)
            self.word_of_the_day = word

            # when the date is different from the date stored in the table
        elif qry[0]['date'] != datetime.date.today():

            # we request a new word
            word = requests.get(url, headers=headers, params=querystring)
            word = word.json()['word']
            while not word.isalpha():
                word = requests.get(url, headers=headers, params=querystring)
                word = word.json()['word']

            params = (datetime.date.today(), word)
            self.query("UPDATE word SET date = %s, word =%s",  params)
            self.query("UPDATE users SET completed_game = completed_game -1")
            # store the word into the table, and since it is a new day we should make it so that the user has not completed todays game
            self.word_of_the_day = word
        else:
            self.word_of_the_day = qry[0]['word']

        return self.word_of_the_day
    
    def clearLeaderboard(self):
        # try to clear the leaderboard
        qry = self.query("SELECT * FROM word")

        # if there is no date stored do nothing
        if len(qry) == 0:
            return "do nothing"
        
        # if the date is changed delete each row in the leaderboard
        if qry[0]['date'] != datetime.date.today():
            self.query("DELETE FROM leaderboard")
            return "deleted table"
        # otherise we do nothing
        else:
            return "preserve table"
