'''
Created on Feb 1, 2017
Updated on Apr 8, 2017
Version: 0.02.00

@author: Matthew Hess, Sr
@email: matt.hess@lookoutmountainresearch.com

'''
import sys
sys.path.append("/var/www/lookoutmountainresearch.com/test/scripts/LookoutMountainResearch")
import MySQLdb
import lmr_secrets
import logging

# Create logger for each instance of the database that is used.

def db_connect():
    lmr_secrets.load_db_secrets()
    host = lmr_secrets['db_hostname']      # The IP address or hostname for the DB.
    user = lmr_secrets['db_user']          # The DB user name.
    passwd = lmr_secrets['db_password']    # The DB password.
    db = lmr_secrets['db_instance']        # The name of the database instance.

    #DBLogger = Logger()
    #DBLogger.StartLogger("DatabaseConnection", "database")
    #DBLogger.LogActivity("INFO", "Database connection has started.")

    try:
        db = MySQLdb.connect(host, user, passwd, db)
    except Exception as e:
        DBConnectionError = "Connection to DB Failed!"
        print(DBConnectionError)
        #DBLogger.LogActivity("CRITICAL", DBConnectionError)
        sys.exit()

    # you must create a Cursor object. It will let you execute all the queries you need
    cur = db.cursor()
    yield True
    db.close

def db_insert(insert_sql):
    db_connect()
    try: # Use all the SQL you like
        cur.execute(querySQL)
        db.commit()
        if queryType == "INSERT":
            output = "Insert Successful"
            #DBLogger.LogActivity("INFO", "INSERT" + str(querySQL))
        elif queryType == "SELECT":
            output = cur.fetchall()
            #DBLogger.LogActivity("INFO", "SELECT" + str(querySQL))
        elif queryType == "UPDATE":
            output = "Update Successful"
            #DBLogger.LogActivity("INFO", "UPDATE" + str(querySQL))
        elif queryType == "DELETE":
            output = "Delete Successful"
            #DBLogger.LogActivity("INFO", "DELETE" + str(querySQL))
    except:
        cur.close()
        cur = db.cursor()
        db.rollback()
        output = queryType + " record transaction failed. SQL = " + querySQL
        print(output)
        #DBLogger.LogActivity("CRITICAL",output)
        sys.exit()


    db.close()
    #DBLogger.LogActivity("INFO", "Database connection has been successfully closed.")

    # print all the first cell of all the rows
    return output
