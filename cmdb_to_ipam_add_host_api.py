#!/usr/bin/python
# This script will read t_ipstatus, t_server_provisioning, t_vm_provisioning tables for CMDB mysql databse.
# and update IP's to IPAM database 
# Author: Aniket Gole
# Contributor: Joel Raja, Iram Khan
# Email: aniket.gole@ril.com; joelvivek.raja@ril.com; iram1.khan@ril.com
 
#from ladon.ladonizer import ladonize
#from ladon.clients.jsonwsp import JSONWSPClient
from suds.client import Client
from hashlib import sha256
from contextlib import closing
import hmac
import pdb
import MySQLdb
import re
import time
import logging
import sys
import os
import smtplib
import argparse
import smtplib
import commands
#import script_config
from config import script_config

# Logging #################################################################
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler(script_config.logfile)
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)


# Global Variable #################################################################
fo = open(script_config.table_file, 'aw')
datafile = file(script_config.table_file).read()
endpoint=script_config.ipam_var["endpoint"]


#endpoint='http://10.135.11.94:8053/API/NSService_10/soap11/description'
#client = Client(endpoint, cache=None)
flag = 0
try:
  client = Client(endpoint, cache=None)
  
except Exception as e:
   flag = 1
   logger.error("Error is :- %s "+ str(e))
   print "IPAM Connectivity issue"
  

#print "Flag is", flag
	
keyname = script_config.ipam_var["keyname"] 
transactionkey = script_config.ipam_var["transactionkey"]
family = script_config.ipam_var["family"]
blocktype = script_config.ipam_var["blocktype"]
subnet_value = script_config.ipam_var["subnet_value"]
owner = script_config.ipam_var["owner"]
FROM = script_config.mail_var["FROM"]
TO = script_config.mail_var["TO"]
CC = script_config.mail_var["CC"]
SUBJECT = script_config.mail_var["SUBJECT"]
TEXT = script_config.mail_var["TEXT"]
SERVER = script_config.mail_var["SERVER"]
PORT = script_config.mail_var["PORT"]
Ipam_update_count = []
sub_not_in_ipam = []
illegal_subnet_in_ipam = []
Ipam_delete_count = []
sub_ip_in_ipam = []



# Functions ############################################################################
def update_host_CLI(subnet, ipaddress, dict_line, Count, cur):
    #print "Entering Update_host_CLI"
    #if ipaddress in datafile:
    #if dict_line :
    #    logger.info("%s IP Already in IPAM Database because its entry available in table_file." % (ipaddress))
    if "/" in subnet:
        #logger.info("%s IP Not in IAPM Database." % (ipaddress))
	logger.info("%s IP Subnet Valid to update IAPM Database." % (ipaddress))
	sub_ip = str(subnet).split('/')
	owner = 'Reliance Jio Infocomm Ltd'
	dnsname = ''
	view = ''
	message = '&'.join([keyname, ipaddress, dnsname, view, transactionkey])
	#print "message: ", message
	digest = hmac.new(str(transactionkey), message, digestmod=sha256).hexdigest()
	#print "digest: ", digest
	location = client.factory.create('IPAMBlock')
	location.network = sub_ip[0]
	location.bitmask = sub_ip[1]
	location.owner = owner
	location.type = ''
	location.family = family
	location.infofields = []

	if Count == 1:
	    infos = client.factory.create('ArrayOfIPAMInfo') 
	    i1 = client.factory.create('IPAMInfo')
	    i1.name = "Hostname"
	    i1.value = dict_line['hostname']
	    i2 = client.factory.create('IPAMInfo')
	    i2.name = "Environment"
	    i2.value = dict_line['environment'] 
	    i3 = client.factory.create('IPAMInfo')
	    i3.name = "SerialNumber"
	    i3.value = dict_line['serialnumber']
	    i4 = client.factory.create('IPAMInfo')
	    i4.name = "ServerType"
	    i4.value = "Base"
            infos["item"] = [i1, i2, i3, i4]
	elif Count == 0:
	    infos = client.factory.create('ArrayOfIPAMInfo')
            i1 = client.factory.create('IPAMInfo')
            i1.name = "Hostname"
            i1.value = dict_line['vm_hostname'] 
            i2 = client.factory.create('IPAMInfo')
            i2.name = "Environment"
            i2.value = dict_line['environment']
	    i3 = client.factory.create('IPAMInfo')
	    i3.name = "SerialNumber"
	    i3.value = dict_line['vm_serialnumber']
	    i4 = client.factory.create('IPAMInfo')
	    i4.name = "ServerType"
	    i4.value = "Vm"
            infos["item"] = [i1, i2, i3, i4]
	elif Count == 2:
	    #print "Entering elif Count ==2"
	    infos = client.factory.create('ArrayOfIPAMInfo') 
	    i1 = client.factory.create('IPAMInfo')
	    i1.name = "Hostname"
	    i1.value = dict_line['hostname']
	    i2 = client.factory.create('IPAMInfo')
	    i2.name = "Environment"
	    i2.value = dict_line['environment'] 
	    i3 = client.factory.create('IPAMInfo')
	    i3.name = "SerialNumber"
	    i3.value = dict_line['serialnumber']
	    i4 = client.factory.create('IPAMInfo')
	    i4.name = "ServerType"
            i4.value = "PublicIP"
	    infos["item"] = [i1, i2, i3, i4]
	    i5 = client.factory.create('IPAMInfo')
            i5.name = "RP_Email"
            i5.value = dict_line['application_owner_contact_email']
	    i6 = client.factory.create('IPAMInfo')
            i6.name = "RP_Name"
            i6.value = dict_line['application_name']
	    infos["item"] = [i1, i2, i3, i4, i5, i6]
	try:
	    if subnet not in sub_not_in_ipam:
		#print "Entering if subnet not in ipam"
	        if subnet not in illegal_subnet_in_ipam:
		    #print "Entering subnet not in illegal_subnet"
	    	    result=client.service.addHost(keyname, digest, location, ipaddress, owner, dnsname, view, infos=infos, force=False)
		    #print "result: ", result    
		    dict_line['insert_date'] = script_config.today
	    	    update_query = ("update t_ipstatus set ipam_update='Updated' where ip='%s' and ipam_update='NEW'" % (ipaddress))
	    	    fo.write(str(dict_line)+'\n')
	    	    cur.execute(update_query)
	    	    Ipam_update_count.append(ipaddress)
	    	    logger.info("%s IP inserted in IPAM Database Successfully !!!." % (ipaddress))
	    	    logger.info("%s Value updated in CMDB Database Successfully !!!." % (ipaddress))
	except Exception:
	    logger.info("%s IP Not inserted in IPAM Database Because of some error." % (ipaddress))
	    e = sys.exc_info()[1]
	    host_error = str(e).split()
	    if "'HOST_EXISTS'" in host_error:
	    	logger.info("%s IP already exist in PAM database. Will update new host values." % (ipaddress))
		host = client.factory.create('IPAMHost')
		host.address = ipaddress
		host.owner = owner
		message = '&'.join([keyname, ipaddress, owner, transactionkey])
		digest = hmac.new(str(transactionkey), message, digestmod=sha256).hexdigest()
		update_ip = client.service.updateHost(keyname, digest, host, owner, infos, False)
		if update_ip == True:
                    #del Ipam_update_count [:]
		    logger.info("New value updated in IPAM database for host %s." % (ipaddress))
	    	    #update_query = ("update t_ipstatus set ipam_update='Updated' where ip='%s' and ipam_update='NEW_TEST'" % (ipaddress))
	    	    update_query = ("update t_ipstatus set ipam_update='Updated' where ip='%s' and ipam_update='NEW'" % (ipaddress))
                    #print ipaddress
                    #print update_query
	    	    cur.execute(update_query)
	    	    logger.info("For host %s Value updated in CMDB Database Successfully !!!." % (ipaddress))
	    	    dict_line['update_date'] = script_config.today
	    	    Ipam_update_count.append(ipaddress)
		    fo.write(str(dict_line)+'\n')
		else:
		    logger.info("New value not updated for host %s." % (ipaddress))
	    elif "'ILLEGAL_PARENT_CANDIDATE'" in host_error:
	    	logger.error("%s ILLEGAL SUBNET in IPAM type should be = address to update host ip %s." % (subnet, ipaddress))
		illegal_subnet_in_ipam.append(subnet)
	    elif '*cannot' and 'find' and 'location' in host_error:
	    	logger.error("%s SUBNET NOT AVAILABLE in IPAM  %s." % (subnet, ipaddress))
		sub_not_in_ipam.append(subnet)
		
	    logger.error("%s %s %s" % (ipaddress, e, dict_line))
	    pass
 
    else:
	  logger.info("%s IP Not in IAPM Database." % (ipaddress))
	  logger.info("%s IP Subnet Not Valid to update IAPM Database. %s" % (ipaddress, dict_line))
	  logger.info("%s IP Not inserted in IPAM Database." % (ipaddress))
		
#Delete ipam function #############################################################

def delete_host_CLI(subnet, ipaddress, dict_line, cur):
    if "/" in subnet:
        logger.info("%s IP Not in IAPM Database." % (ipaddress))
	logger.info("%s IP Subnet Valid to update IAPM Database." % (ipaddress))
	sub_ip = str(subnet).split('/')
	#print 'sub ip:', sub_ip
	owner = 'Reliance Jio Infocomm Ltd'
	dnsname = ''
	view = ''
	host = client.factory.create('IPAMHost')
	host.address = ipaddress
	host.owner = owner
	message = '&'.join([keyname, ipaddress, owner, transactionkey])
	digest = hmac.new(str(transactionkey), message, digestmod=sha256).hexdigest()
        host.owner = owner
	try:
	    if sub_ip not in sub_ip_in_ipam:
		host = client.factory.create('IPAMHost')
		host.address = ipaddress
		host.owner = owner
		message = '&'.join([keyname, ipaddress, owner, transactionkey])
		digest = hmac.new(str(transactionkey), message, digestmod=sha256).hexdigest()
	    	result=client.service.deleteHost(keyname, digest, host, 'no', True, view)
	    	#print "result: ", result
		dict_line['insert_date'] = script_config.today
		#print "dict_line :", dict_line
	    	fo.write(str(dict_line)+'\n')
	    	Ipam_delete_count.append(ipaddress)
		
		#print "Ipam_delete_count : ", Ipam_delete_count
	    	update_query = ("update t_ipstatus set ipam_update='Deleted' where ip='%s'" % (ipaddress))
		#print "update query: ", update_query
		cur.execute(update_query)
		#print "execute: ", cur.execute(update_query)
		cur.commit()
		#print "%s IP deleted in IPAM Database Successfully !!!." % (ipaddress)
		logger.info("%s IP deleted in IPAM Database Successfully !!!." % (ipaddress))
	    	#print "%s Value updated in CMDB Database Successfully !!!." % (ipaddress)
	    	logger.info("%s Value updated in CMDB Database Successfully !!!." % (ipaddress))
	except Exception:
	    logger.info("%s IP Not deleted in IPAM Database Because of some error." % (ipaddress))
	    e = sys.exc_info()[1]
	    #print 'e is:', e
	    logger.error("Exception in initializing DB :" + str(e))
 	    #host_error = str(e).split()
	    #if "'HOST_EXISTS'" in host_error:
	    #	logger.info("%s IP already exist in PAM database. Will update new host values." % (ipaddress))
	    host = client.factory.create('IPAMHost')
	    host.address = ipaddress
	    host.owner = owner
	    message = '&'.join([keyname, ipaddress, owner, transactionkey])
	    digest = hmac.new(str(transactionkey), message, digestmod=sha256).hexdigest()




# Mysql Connection #################################################################
# Open database connection
def sql_value():
    db = MySQLdb.connect(script_config.mysql_server["mysql_host"], script_config.mysql_server["mysql_user"], script_config.mysql_server["mysql_passwd"], script_config.mysql_server["mysql_database"])
    base = script_config.mysql_query["base"]
    vm = script_config.mysql_query["vm"]
    dele = script_config.mysql_query["dele"]
    pubip = script_config.mysql_query["pubip"]
    Count=0
    for query in vm, base, pubip:
        with closing(db.cursor()) as cur:
	    cur.execute(query)
	    row = cur.fetchall()
	    #print "row:", row
	    cols = [ d[0] for d in cur.description ]
	    #print "cols:", cols
	    for i in row:
		if i :
	            res = dict(zip(cols, i))
            	    #print "res:", res
		    #print "cur:", cur
		    #print "Count: ", Count
		    update_host_CLI(str(res['subnet']), res['ip'], res, Count, cur)
		
	Count=Count+1
	if Count == 3:
	    cur = db.cursor()
	    cur.execute(dele)
	    row = cur.fetchall()
	    cols = [ d[0] for d in cur.description ]
	    for i in row:
		if i :
        	    res = dict(zip(cols, i))
		    delete_host_CLI(str(res['subnet']), res['ip'], res, cur)
	     
     
    #Closing mysql connection
    db.commit()
    db.close()

def MailIfError(FROM, TO, CC, SUBJECT, TEXT, SERVER, PORT):
   
   message = """From: RJIL Notification  <%s>
To: %s
CC: %s
Subject: %s

%s 

IPAM Connectivity issue.

Sorry for the inconvenience. Team is working on it.


""" % (FROM, ", ".join(TO), ", ".join(CC), SUBJECT, TEXT)
   server = smtplib.SMTP(SERVER, PORT)
   server.sendmail(FROM, TO + CC, message)
   server.quit()


def Mailed(FROM,TO,CC,SUBJECT,TEXT,SERVER, PORT, Ipam_update_count, block, iblock, Ipam_delete_count):

  
    message = """From: RJIL Notification  <%s>
To: %s
CC: %s
Subject: %s

%s

%s subnets are not available in IPAM - (if list empty please ignore.)
%s

%s illegal Subnets in IPAM, It needs to chaged block type = Address - (if list empty please ignore.)
%s

%s IP's updated in IPAM !!!
%s

%s IP's deleted in IPAM !!!
%s

""" % (FROM, ", ".join(TO), ", ".join(CC), SUBJECT, TEXT, len(block), block, len(iblock), iblock, len(Ipam_update_count), Ipam_update_count, len(Ipam_delete_count), Ipam_delete_count)
    server = smtplib.SMTP(SERVER, PORT)
    server.sendmail(FROM, TO + CC, message)
    server.quit()


##################################################################
if __name__ == "__main__":
    logger.info("======== Script started =========")
    parser = argparse.ArgumentParser(description='For commandline argument please follow the below usage.\n\n Eg:- python cmdb_to_ipam_add_host_api.py -sub 10.135.1.0/24 -ip 10.135.1.36 \n\n OR use mysql Eg:- python cmdb_to_ipam_add_host_api.py -mysql yes \nFor more information or any query please mail to <RJIL.IDCAutomation@ril.com> ')
    parser.add_argument("-sub", "--SubnetIP", nargs=1, type=str, help="Provide Subnet IP address with bitmask eg 10.137.2.0/24.")
    parser.add_argument("-ip", "--Ipaddress", nargs=1, type=str, help="Provide IP address eg. 10.137.2.57 OR")
    parser.add_argument("-mysql", "--MysqlDB", nargs=1, type=str, help="python cmdb_to_ipam_add_host_api.py -mysql yes( Which will read CMDB database for getting host with some field.)")
    args = parser.parse_args()
    if args.SubnetIP and args.Ipaddress:
        dict_line = {}
        dict_line['subnet'] = args.SubnetIP[0]
        dict_line['ip'] = args.Ipaddress[0]
        update_host_CLI(dict_line['subnet'], dict_line['ip'], dict_line)
    elif args.MysqlDB:
	if flag == 1:
		MailIfError(FROM,TO,CC,SUBJECT,TEXT,SERVER, PORT)
		logger.info("####### Summary start for %s #######" % (script_config.today))
		logger.info("IPAM connectivity issue :- %s" % endpoint)
		logger.info("####### Summary End for %s #######" % (script_config.today))
	else:
		sql_value()
	        logger.info("####### Summary start for %s #######" % (script_config.today))
		logger.info("Total number of IP updated in IPAM at %s :- %s" % (script_config.today, len(Ipam_update_count)))
		logger.info("IP updated List in IPAM at %s :- %s" % (script_config.today, Ipam_update_count))
		logger.info("Total number of IP deleted in IPAM at %s :- %s" % (script_config.today, len(Ipam_delete_count)))
		logger.info("IP deleted List in IPAM at %s :- %s" % (script_config.today, Ipam_delete_count))
		logger.info("%s Subnet not available in IPAM :- %s" % (len(sub_not_in_ipam), sub_not_in_ipam))
		logger.info("%s Subnet illegal in IAPM %s" % (len(illegal_subnet_in_ipam), illegal_subnet_in_ipam))
		logger.info("Total number of IP deleted in IPAM at %s :- %s" % (script_config.today, len(Ipam_delete_count)))
		logger.info("IP deleted List in IPAM at %s :- %s" % (script_config.today, Ipam_delete_count))
	 
		logger.info("####### Summary End for %s #######" % (script_config.today))
		#command = ("cat %s |grep 'Cannot find location' |awk {'print $15'} | sort | uniq |tr -d '('" % (script_config.logfile))
		#block = commands.getstatusoutput(command)
		#Mailed(FROM,TO,CC,SUBJECT,TEXT,SERVER, PORT, Ipam_update_count, block[1])
		Mailed(FROM,TO,CC,SUBJECT,TEXT,SERVER, PORT, Ipam_update_count, sub_not_in_ipam, illegal_subnet_in_ipam, Ipam_delete_count)
    else:
        parser.print_help()
        sys.exit(1)
    # Close opend file
    fo.close()
    logger.info("======== Script Ended =========")
