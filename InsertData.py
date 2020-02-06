import mysql.connector

mydb = mysql.connector.connect(
                     host="localhost",    # your host, usually localhost
                     user="root",         # your username
                     passwd="",  # your password
                     db="network_topology"
)

mycursor = mydb.cursor()

mycursor.execute("SHOW TABLES")

for x in mycursor:
  print(x)