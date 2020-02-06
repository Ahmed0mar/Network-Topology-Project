import pymongo
import re
import pandas as pd
import mysql.connector
from mysql.connector import connection

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["bet_prod_v1"]

devicescol = mydb["devices"]
interfacescol = mydb["interfaces"]
ifaliases=[]
ifnames=[]
ifindexes=[]
ips=[]
hostnames=[]
ipaddresses=[]
vendors=[]
models=[]

regexList=["^\d+(\/)\d+(\/)\d+$","^ge-\d+(\/)\d+(\/)\d+$","^et-\d+(\/)\d+(\/)\d+$",
            "^xe-\d+(\/)\d+(\/)\d+$","^fa\d+(\/)\d+(\/)\d+$","^Gi\d+(\/)\d+(\/)\d+$",
            "^Gi\d+(\/)\d+$","GigabitEthernet\d+(\/)\d+(\/)\d+$",
            "GigabitEthernet\d+(\/)\d+(\/)\d+.(\/)\d+$","HundredGigE\d+(\/)\d+.(\/)\d+$",
            "HundredGigE\d+(\/)\d+(\/)\d+(\/)\d+$","^Te\d+(\/)\d+(\/)\d+$",
            "^Te\d+(\/)\d+$","TenGigE\d+(\/)\d+(\/)\d+(\/)\d+$"]
def matchreg(interface):
    for reg in regexList:
        if re.match(reg,interface):
            return True
    return False
for x in devicescol.find({},{ "_id": 0, "hostname": 1, "ipaddress": 1,"vendor":1,"model":1 }):
    device=x['hostname'][x['hostname'].find('-')+1:x['hostname'].find('-',x['hostname'].find('-')+1)]
    if ((device[0] == 'S' and device[-1]=='B') or(device[0] == 'S' and device[-1]=='J') or\
        (device[0] == 'S' and device[-1]=='C') or (device[0] == 'S' and device[-1]=='H') or\
        (device[0] == 'R' and device[-1]=='J') or (device[0] == 'R' and device[-1]=='C') or\
        (device[0] == 'R' and device[-1]=='A') or (device[0] == 'R' and device[-1]=='H'))\
        and "TECORP" not in x['hostname']:
        if 'model' in x and 'vendor' in x:
            hostnames.append(str(x['hostname']))
            ipaddresses.append(str(x['ipaddress']))
            vendors.append(str(x['vendor']))
            models.append(str(x['model']))
        elif 'model' in x and 'vendor' not in x:
            hostnames.append(str(x['hostname']))
            ipaddresses.append(str(x['ipaddress']))
            vendors.append('')
            models.append(str(x['model']))
        elif 'model' not in x and 'vendor' in x:
            hostnames.append(str(x['hostname']))
            ipaddresses.append(str(x['ipaddress']))
            vendors.append(str(x['vendor']))
            models.append('')
        elif 'model' not in x and 'vendor' not in x:
            hostnames.append(str(x['hostname']))
            ipaddresses.append(str(x['ipaddress']))
            vendors.append('')
            models.append('')
for x in interfacescol.find({},{ "_id": 0, "ifIndex": 1, "ifName": 1,"ifAlias":1,"ipaddress":1 }):
    if 'ifName' not in x:
        continue
    elif  'ifAlias' not in x and matchreg(x['ifName']):
            ifindexes.append(str(x['ifIndex']))
            ifnames.append(str(x['ifName']))
            ifaliases.append('')
            ips.append(str(x['ipaddress']))
    elif  matchreg(x['ifName']):
            ifindexes.append(str(x['ifIndex']))
            ifnames.append(str(x['ifName']))
            ifaliases.append(x['ifAlias'].replace("\"",r""))
            ips.append(x['ipaddress'])

df = pd.DataFrame({'HostName': hostnames,
                   'IPAddress':ipaddresses,
                   'Models': models,
                   'Vendors':vendors})

df1=pd.DataFrame({'IfIndex':ifindexes,
                   'ifName':ifnames,
                   'ifAlias':ifaliases,
                   'IPAdresses':ips})

df.to_csv('outdevices.csv',index=False)
df1.to_csv('outinterfaces.csv',index=False)

mydb= mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="network_topology"
)
mycursor=mydb.cursor()

query="insert into network_topology.devices (HostName,IP,Vendor,Model) values"
query2="insert into network_topology.interfaces (IfIndex,IfName,IfAlias,IP) values"
for ind,name,alias,IP in zip(ifindexes,ifnames,ifaliases,ips):
    query2+="""(\""""+str(ind)+"\",\""+str(name)+"\",\""+str(alias)+"\",\""+str(IP)+"\")"
    try:
        mycursor.execute(query2)
        query2="insert into network_topology.interfaces (IfIndex,IfName,IfAlias,IP) values"
    except e:
        print(e)


for hname,ip,v,m in zip(hostnames,ipaddresses,models,vendors):
    query+="('"+hname+"','"+ip+"','"+v+"','"+m+"')"
    print(query)
    mycursor.execute(query)
    query="insert into network_topology.devices (HostName,IP,Vendor,Model) values"
mydb.commit()

mycursor.close()
