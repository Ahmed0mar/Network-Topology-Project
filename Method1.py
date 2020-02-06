import mysql.connector
from mysql.connector import connection

def read_file(filename):
    FilePath=r"F:\Projects\NNM Project-Khayat Project\NaProject-final\script-lldp\\"
    LocalIndex=-1
    ParentIndex=-1
    IdIndex=-1
    PortIndex=-1
    SystemIndex=-1
    local=[]
    parent=[]
    ids=[]
    port=[]
    system=[]
    file = open(FilePath+filename,"r")
    #this loop to get the start indexes of
    for line in file:
         if line.find("Local Interface") >=0 and LocalIndex==-1: LocalIndex=line.find("Local Interface")
         if line.find("Parent Interface") >=0 and ParentIndex==-1: ParentIndex=line.find("Parent Interface")
         if line.find("Chassis Id") >=0 and IdIndex==-1: IdIndex=line.find("Chassis Id")
         if line.find("Port info") >=0 and PortIndex==-1: PortIndex=line.find("Port info")
         if line.find("System Name") >=0 and SystemIndex==-1:
             SystemIndex=line.find("System Name")
             continue
         if LocalIndex > -1:
             local.append(line[LocalIndex:line.find(" ",LocalIndex)])
             parent.append(line[ParentIndex:line.find(" ",ParentIndex)])
             ids.append(line[IdIndex:line.find(" ",IdIndex)])
             port.append(line[PortIndex:line.find(" ",PortIndex)])
             system.append(line[SystemIndex:line.find(" ",SystemIndex)])
    insert_method_data(IP="10.37.105.158",local=local,parent=parent,ids=ids,port=port,system=system)

def insert_method_data(IP,local,parent,ids,port,system):
    mydb= mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="network_topology"
    )
    IfName=""
    dbcursor=mydb.cursor()
    for loc,parentitem,Id,portitem,systemitem in zip(local,parent,ids,port,system):
        if portitem.isdigit():
            query="""select IfName from interfaces where
                     IP=(select IP from devices where HostName like """+systemitem+""") and IfIndex="""+portitem
            dbcursor.execute(query)
            queryResults = mycursor.fetchall()
            for element in queryResults:
                IfName=element[0]
            query=""" insert into lldb(DeviceId,LocalInterface,NeighbourHostName,NeighbourInterface)
                        select DeviceId,"""+loc+ ""","""+systemitem+ ""","""+IfName+ """
                        from devices where IP="""+IP
            dbcursor.execute(query)
        else:
            query=""" insert into lldb(DeviceId,LocalInterface,NeighbourHostName,NeighbourInterface)
                        select DeviceId,"""+loc+ ""","""+systemitem+ ""","""+portitem+ """
                        from devices where IP="""+IP
            dbcursor.execute(query)
        db.commit()

def profiling():
    dbconnection= mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="network_topology"
    )
    query="select * from devices where model='Cisco'"
    dbconnection.execute(query)
    dbcursor=dbconnection.cursor()
    queryResults = dbcursor.fetchall()
    for data in queryResults:
            IfName=element[0]

read_file("lldp.txt")
