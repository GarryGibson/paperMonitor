import mysql.connector
import logging
import ConfigParser
import json
import io

config = json.load(io.open('config.json','r'))
log = logging.getLogger('monitor')

def getConnection():
    try:
        log.debug('Connecting to DB..')
        host = str(config['DEFAULT']['DBCONNECTION']['HOST'])
        port = config['DEFAULT']['DBCONNECTION']['PORT']
        database = str(config['DEFAULT']['DBCONNECTION']['DATABASE'])
        user = str(config['DEFAULT']['DBCONNECTION']['USER'])
        password = str(config['DEFAULT']['DBCONNECTION']['PASSWORD'])

        connection = mysql.connector.connect(host=host,port=port,database=database,user=user,password=password,connection_timeout=10)
                
        if(connection):
            log.debug('Connected')
        return connection
    except mysql.connector.Error as err:
        log.exception('Failed to connect:')
        return None

def saveTempHumid(connection, temp, humid):
    query = "INSERT INTO sensorreading (Temperature,Humidity) VALUES(%s,%s)"
    args = (round(temp,2),round(humid,2))

    try:
        log.debug('Attempting DB write...')
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(query,args)
            connection.commit()
            cursor.close()
            log.debug('..succeeded')
            return True
        else:
            log.debug('Tried to execute SQL, but not connected to DB')
            return False
    except mysql.connector.Error as oops:
        log.exception('SQL execution failed')
        cursor.close()
        return False
