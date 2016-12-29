#!/usr/bin/env python

'''
Authors: 
joelvivek.raja@ril.com

Scope:

Read records from CMDB and check

Steps:
1. Create a new temp table in CMDB
2. Fetch data from T_IPSTATUS against TSP and TVP
Compliance check for IP = USED
  Check the T_IPSTATUS where the IP = 'USED' in a iterating IPs, 
       Take those IPs and check against T_SERVER_PROVIOSIONING or T_VM_PROVISIONING.
             If the IP exist in the T_SERVER_PROVIOSIONING update TSP_ISPRESENT, and add respective data like TSP_HOSTNAME, TSP_SERIALNUMBER, TSP_DATA_IP, TSP_ILO_IP, TSP_DATA_TYPE, etc
	     If the IP exist in the T_VM_PROVIOSIONING update TVP_ISPRESENT, and add respective data like TVP_HOSTNAME, TVP_SERIALNUMBER, TVP_DATA_IP, TVP_ILO_IP, TVP_DATA_TYPE
 
3. Insert all records of CMDB into a temp table 
4. Create a report in excel and send it in mail



'''

import sys
import MySQLdb as mdb
#import logging.handlers
import logging
from logging import handlers
from _mysql import NULL
import json
#import openpyxl as pywb
#import numpy as np
import csv
import smtplib
import csv
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEBase import MIMEBase
from email import Encoders
from email.message import Message


reload(sys)
sys.setdefaultencoding('utf8')




data = json.loads(open("input.json").read())


output          =   data["OUTPUT"]
o_server        =   output["SERVER"]
o_username      =   output["USERNAME"]
o_password      =   output["PASSWORD"]
o_database      =   output["DATABASE"]
o_table         =   output["TABLE"]
LOG_FILENAME    =   output["LOG_FILENAME"]
LOG_FILESIZE    =   output["LOG_FILESIZE"]
LOG_BACKUP_COUNT=   output["LOG_BACKUP_COUNT"]

cmdb_server     =   data["CMDB"]["SERVER"]
cmdb_username   =   data["CMDB"]["USERNAME"]
cmdb_password   =   data["CMDB"]["PASSWORD"]
cmdb_database   =   data["CMDB"]["DATABASE"]
cmdb_table_ip   =   data["CMDB"]["TABLE_IP"]
cmdb_table_tsp  =   data["CMDB"]["TABLE_TSP"]
cmdb_table_tvp  =   data["CMDB"]["TABLE_TVP"]

filename = data["FILE_CONTENT"]["FILENAME"]
FILE=open(filename, "w");
fieldnames =['IP','IP ISPRESENT','TSP ISPRESENT','TVP ISPRESENT','IP SERIALNUMBER','IP HOSTNAME','IP STATUS','IP VLAN_ID','IP TYPE','TSP ILORSA IP','TSP DATA IP','TSP DEVICETYPE','TSP SERIALNUMBER','TSP HOSTNAME','TVP VM DATA IP','TVP SERIALNUMBER','TVP VM HOSTNAME','TVP ILORSA IP']

file1 = data["FILE_CONTENT"]["FILENAME"]

emailtolist      =  data["EMAIL_RECIPENT"]["EMAILTOLIST"]
emailfromlist    =  data["EMAIL_RECIPENT"]["EMAILFROMLIST"]
emailsubject     =  data["EMAIL_RECIPENT"]["EMAILSUBJECT"]



# all logger

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
my_logger = logging.getLogger('Log')
my_logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=LOG_FILENAME, backupCount=LOG_BACKUP_COUNT)
handler.setFormatter(formatter)
my_logger.addHandler(handler)


############################################################################
# Create temp table T_IP_COMPLIANCE
############################################################################

def init_db():
    my_logger.info("Initializing the output DB")
    #print "initializing init_db"
    try:
        my_logger.info ("Trying to connect to Output DB")
        my_logger.info("Connecting to MySQL DB")
        db = mdb.connect(o_server, o_username, o_password, o_database)
        cursor = db.cursor()
        stmt = "SHOW TABLES LIKE '"+o_table+"'"
        cursor.execute(stmt)
        result = cursor.fetchone()
        my_logger.debug("The result is :" + stmt)
        #print("The result is :", result)
	my_logger.info ("Checking if the table already exist, if so, drop and create a new table")
        if result:
            my_logger.debug (" Table Exist so truncating")
            stmt1 = "TRUNCATE TABLE "+ o_table +" "
	    cursor.execute(stmt1)
	    my_logger.debug( " Table "+ o_table + " Truncated")
            db.commit()
            db.close()        
	else:
            my_logger.info("The Table doesnt exist, so creating table")
            stmt1 = "CREATE TABLE "+ o_table +" \
( \
id INT(11) NOT NULL AUTO_INCREMENT, \
ip VARCHAR(25) NOT NULL DEFAULT 'N', \
ip_ispresent VARCHAR(1) NOT NULL DEFAULT 'N', \
tsp_ispresent VARCHAR(1) NOT NULL DEFAULT 'N', \
tvp_ispresent VARCHAR(1) NOT NULL DEFAULT 'N', \
ip_serialnumber VARCHAR(100) NOT NULL DEFAULT 'N', \
ip_hostname VARCHAR(100) NOT NULL DEFAULT 'N', \
ip_status VARCHAR(100) NOT NULL DEFAULT 'N', \
ip_vlan_id VARCHAR(100) NOT NULL DEFAULT 'N', \
ip_type VARCHAR(100) NOT NULL DEFAULT 'N', \
tsp_ilorsa_ip VARCHAR(100) NOT NULL DEFAULT 'N', \
tsp_data_ip VARCHAR(100) NOT NULL DEFAULT 'N', \
tsp_devicetype VARCHAR(100) NOT NULL DEFAULT 'N', \
tsp_serialnumber VARCHAR(100) NOT NULL DEFAULT 'N', \
tsp_hostname VARCHAR(100) NOT NULL DEFAULT 'N', \
tvp_vm_data_ip VARCHAR(100) NOT NULL DEFAULT 'N', \
tvp_serialnumber VARCHAR(100) NOT NULL DEFAULT 'N', \
tvp_vm_hostname VARCHAR(100) NOT NULL DEFAULT 'N', \
tvp_ilorsa_ip VARCHAR(100) NOT NULL DEFAULT 'N', \
UNIQUE INDEX id (id)\
) "
	    cursor.execute(stmt1)
	    #cursor.execute("truncate table "+ o_table)
	    my_logger.debug("Table " +o_table+ " created")
            db.commit()
            db.close()
            return True

    except Exception as e:
	my_logger.exception("Exception in initializing DB", str(e) )
        #print ("Exception while initializing output DB: ", str(e)  ) 
        return False



############################################################################
################################# IP #######################################
############################################################################


def ip_read():
	print "Initizlizing ip_read"
	my_logger.info("Conecting CMDB Prod")
        cmdb = mdb.connect(cmdb_server, cmdb_username, cmdb_password, cmdb_database)
        cmdb_cursor = cmdb.cursor(mdb.cursors.DictCursor)
	sql_ip ="select ip.ip, ip.ip_status, ip.vlan_id, ip.type, ip.hostname, ip.serialnumber \
from "+cmdb_table_ip+" ip \
where ip.IP_STATUS in ('USED', 'FREE')"
        cmdb_cursor.execute(sql_ip)
	my_logger.debug("sql_ip is " + sql_ip)
	rows = cmdb_cursor.fetchall()
        cmdb_cursor.close()
        cmdb.close()
        return rows


def process_list_ip(prefix, values):
	insert_count = 0
	print "Initializing Process_list_ip"
        my_logger.info("Connecting to MySQL DB")
        db = mdb.connect(o_server, o_username, o_password, o_database)
        cursor = db.cursor()
	ips = []
	for value in values:
                ipip = ""
                ipstatus = ""
                ipvlanid = ""
                iptype = ""
		iphostname = ""
		ipsrno = ""
                if value['ip'] :
                    ipip = value['ip'].strip()
                    if value['ip_status']:
                        ipstatus = value['ip_status'].strip()
                    else:
                        ipstatus = "NULL"
                    if value['vlan_id']:
                        ipvlanid = value['vlan_id'].strip()
                    else:
                        ipvlanid = "NULL"
                    if value['type']:
                        iptype = value['type'].strip()
                    else:
                        iptype = "NULL"
                    if value['hostname']:
                        iphostname = value['hostname'].strip()
                    else:
                        iphostname = "NULL"
                    if value['serialnumber']:
                        ipsrno = value['serialnumber'].strip()
                    else:
                        ipsrno = "NULL"				
                if ipip in ips:
                        stmt = "update "+ o_table +" set  \
			"+prefix+"ispresent = 'Y', \
			"+prefix+"serialnumber='"+ipsrno+"',  \
			"+prefix+"hostname ='" + iphostname +"', \
			"+prefix+"status ='" + ipstatus +"', \
			"+prefix+"vlan_id ='" + ipvlanid +"', \
			"+prefix+"type ='" + iptype +"' where ip = '"+ipip+"'" 
                        cursor.execute(stmt.encode('utf-8'))
			my_logger.debug("The update stmt process_list_ip is :" + stmt)
			#print 'stmt is', stmt

                else:
                        stmt = "insert into "+ o_table +" ( \
						ip, \
						"+prefix+"ispresent, \
						"+prefix+"serialnumber, \
						"+prefix+"hostname, \
						"+prefix+"status, \
						"+prefix+"vlan_id, \
						"+prefix+"type \
						)  \
						values( \
						'"+ipip+ "', \
						'Y', \
						'"+ipsrno+ "', \
						'"+iphostname+ "', \
						'"+ipstatus+ "', \
						'"+ipvlanid+ "', \
						'"+iptype+ "' \
						)"
			#print 'stmt is', stmt
			my_logger.debug("The insert stmt process_list_ip is :" + stmt)
                        cursor.execute(stmt.encode('utf-8'))
                        ips.append(ipip)
        db.commit()
        cursor.close()
        db.close()





############################################################################
############################## TSP #########################################
############################################################################

def tsp_read():
	print "Initizlizing tsp_read"
	my_logger.info("Conecting CMDB Prod for TSP")
        cmdb = mdb.connect(cmdb_server, cmdb_username, cmdb_password, cmdb_database)
        cmdb_cursor = cmdb.cursor(mdb.cursors.DictCursor)
	sql_tsp ="select tsp.data_ip, tsp.ilorsa_ip, tsp.devicetype, tsp.serialnumber, tsp.hostname  \
from "+cmdb_table_tsp+" tsp "
        cmdb_cursor.execute(sql_tsp)
	my_logger.debug("sql_tsp is " + sql_tsp)
	rows = cmdb_cursor.fetchall()
        cmdb_cursor.close()
        cmdb.close()
        return rows

def process_list_tsp(prefix, values):
	insert_count = 0
	update_count = 0
    	total_count  = 0
	print "Initializing Process_list_tsp"
        my_logger.info("Connecting to MySQL DB")
        db = mdb.connect(o_server, o_username, o_password, o_database)
        cursor = db.cursor()
	ips = []
        stmt = "select ip from "+ o_table+" "
        cursor.execute(stmt)
        rows_NC = cursor.fetchall()
        for Evalue in rows_NC:
                wrd = Evalue[0]
                wrd = wrd.strip()
		#print "wrd is: ",wrd
                ips.append(wrd)
        B = set(ips)
        ips = list(B)
        for value in values:
                total_count += 1
	        tspip = ""
                tspiloip = ""
                tspdevicetype = ""
                tspsrno = ""
                tsphostname = ""
                if value['data_ip']:
                        tspip = value['data_ip'].strip()
                        if value['ilorsa_ip']:
                                tspiloip = value['ilorsa_ip'].strip()
                        else:
                                tspiloip = "NULL"
                        if value['devicetype']:
                                tspdevicetype = value['devicetype'].strip()
                        else:
                                tspdevicetype ="NULL"
                        if value['serialnumber']:
                                tspsrno = value['serialnumber'].strip()
                        else:
                                tspsrno = "NULL"
                        if value['hostname']:
                                tsphostname = value['hostname'].strip()
                        else:
                                tsphostname = "NULL"

                if (tspip in ips) or (tspiloip in ips) :
                        stmt = "update "+o_table+" set \
						" + prefix +"ispresent = 'Y', \
						"+prefix+"serialnumber='"+tspsrno+"', \
						"+ prefix+"hostname ='" + tsphostname +"', \
						"+ prefix+"devicetype ='" + tspdevicetype +"', \
						"+ prefix+"ilorsa_ip ='" + tspiloip +"', \
						"+ prefix+"data_ip ='" + tspip +"' \
						where (ip = '"+tspip + "' or ip = '"+tspiloip+"')  "
			update_count += 1
                        cursor.execute(stmt.encode('utf-8'))
			my_logger.debug("The update stmt process_list_tsp is :" + stmt)
			#print 'stmt is', stmt
                else:
				try:
						stmt = "insert into "+ o_table +" ( \
						" +prefix+"ispresent, \
						" +prefix+"serialnumber, \
						" +prefix+"hostname, \
						" +prefix+"ilorsa_ip, \
						" +prefix+"data_ip, \
						" +prefix+"devicetype \
						)  \
						values( \
						'Y', \
						'"+tspsrno+ "', \
						'"+tsphostname+ "', \
						'"+tspiloip+ "', \
						'"+tspip+ "', \
						'"+tspdevicetype+ "' \
						)"
						#print 'stmt is', stmt
						my_logger.debug("The insert stmt process_list_tsp is :" + stmt)
			                        cursor.execute(stmt.encode('utf-8'))
						insert_count += 1
                        			ips.append(tspip)
			                        my_logger.debug(stmt)
               	 		except Exception as e:
					my_logger.error("Exception while inserting recording - checking for duplicate" + str(e))
					if "Duplicate" in str(e):
			                        stmt = "update "+o_table+" set \
						" + prefix +"ispresent = 'Y', \
						"+prefix+"serialnumber='"+tspsrno+"', \
						"+ prefix+"hostname ='" + tsphostname +"', \
						"+ prefix+"devicetype ='" + tspdevicetype +"', \
						"+ prefix+"ilorsa_ip ='" + tspiloip +"', \
						"+ prefix+"data_ip ='" + tspip +"' \
						where ip = '"+tspip+"'"
				                try:
                        				cursor.execute(stmt.encode('utf-8'))
				                        ips.append(tspip)
                        				my_logger.debug(stmt)
							update_count += 1
				                except Exception as e:
				                        my_logger.error("IP  doesn't fit for insert/update :", str(e))
   	my_logger.info(prefix+"insert count is : " + str(insert_count))
    	my_logger.info(prefix+"update count is : " + str(update_count))
    	my_logger.info(prefix+"total count is: " + str(total_count))
        db.commit()
        cursor.close()
        db.close()



############################################################################
############################## TVP #########################################
############################################################################

def tvp_read():
	print "Initizlizing tvp_read"
	my_logger.info("Conecting CMDB Prod for TSP")
        cmdb = mdb.connect(cmdb_server, cmdb_username, cmdb_password, cmdb_database)
        cmdb_cursor = cmdb.cursor(mdb.cursors.DictCursor)
	sql_tvp ="select tvp.vm_data_ip, tvp.ilorsa_ip, tvp.serialnumber, tvp.vm_hostname  \
from "+cmdb_table_tvp+" tvp "
        cmdb_cursor.execute(sql_tvp)
	my_logger.debug("sql_tvp is " + sql_tvp)
	rows = cmdb_cursor.fetchall()
        cmdb_cursor.close()
        cmdb.close()
        return rows

def process_list_tvp(prefix, values):
	insert_count = 0
	print "Initializing Process_list_tvp"
        my_logger.info("Connecting to MySQL DB")
        db = mdb.connect(o_server, o_username, o_password, o_database)
        cursor = db.cursor()
	ips = []
        stmt = "select ip from "+ o_table+" "
        cursor.execute(stmt)
        rows_NC = cursor.fetchall()
        for Evalue in rows_NC:
                wrd = Evalue[0]
                wrd = wrd.strip()
                ips.append(wrd)
        B = set(ips)
        ips = list(B)
        for value in values:
                tvpip = ""
                tvpiloip = ""
                tvpsrno = ""
                tvphostname = ""
                if value['vm_data_ip']:
                        tvpip = value['vm_data_ip'].strip()
                        if value['ilorsa_ip']:
                                tvpiloip = value['ilorsa_ip'].strip()
                        else:
                                tvpiloip = "NULL"
                        if value['serialnumber']:
                                tvpsrno = value['serialnumber'].strip()
                        else:
                                tvpsrno = "NULL"
                        if value['vm_hostname']:
                                tvphostname = value['vm_hostname'].strip()
                        else:
                                tvphostname = "NULL"

                if (tvpip in ips) or (tvpiloip in ips) :
                        stmt = "update "+o_table+" set \
						"+prefix+"ispresent = 'Y', \
						"+prefix+"serialnumber='"+tvpsrno+"', \
						"+prefix+"vm_hostname ='" +tvphostname+"', \
						"+prefix+"ilorsa_ip ='" +tvpiloip+"', \
						"+prefix+"vm_data_ip ='" +tvpip+"' \
						where (ip = '"+tvpip + "' or ip = '"+tvpiloip+"')  "
                        cursor.execute(stmt.encode('utf-8'))
			#print 'stmt is', stmt
			my_logger.debug("The update stmt process_list_tvp is :" + stmt)

                else:
				try:
						stmt = "insert into "+o_table+ " ( \
						"+prefix+"ispresent, \
						"+prefix+"serialnumber, \
						"+prefix+"vm_hostname, \
						"+prefix+"ilorsa_ip, \
						"+prefix+"vm_data_ip \
						)  \
						values( \
						'Y', \
						'"+tvpsrno+ "', \
						'"+tvphostname+ "', \
						'"+tvpiloip+ "', \
						'"+tvpip+ "' \
						)"
						my_logger.debug("The insert stmt process_list_tvp is :" + stmt)
						#print 'stmt is', stmt
			                        cursor.execute(stmt.encode('utf-8'))
                        			ips.append(tvpip)
			                        my_logger.debug(stmt)
               	 		except Exception as e:
					my_logger.error("Exception while inserting recording - checking for duplicate" + str(e))
					if "Duplicate" in str(e):
			                        stmt = "update "+o_table+" set \
						"+prefix+"ispresent = 'Y', \
						"+prefix+"serialnumber='"+tvpsrno+"', \
						"+prefix+"vm_hostname ='" +tvphostname+"', \
						"+prefix+"ilorsa_ip ='" +tvpiloip+"', \
						"+prefix+"vm_data_ip ='" +tvpip+"' \
						where (ip = '"+tvpip + "' or ip =  '"+tvpiloip+"') "
				                try:
                        				cursor.execute(stmt.encode('utf-8'))
				                        ips.append(tvpip)
                        				my_logger.debug(stmt)
				                except Exception as e:
				                        my_logger.error("IP  doesn't fit for insert/update :", str(e))

        db.commit()
        cursor.close()
        db.close()




############################################################################
############################## CSV Creation #########################################
############################################################################

def compliance_read():
	print "Initizlizing compliance_read"
	my_logger.info("Conecting CMDB test for compliance data")
        cmdb = mdb.connect(o_server, o_username, o_password, o_database)
        cmdb_cursor = cmdb.cursor()
	sql_comp =" select \
ip, \
ip_ispresent, \
tsp_ispresent, \
tvp_ispresent, \
ip_serialnumber, \
ip_hostname, \
ip_status, \
ip_vlan_id, \
ip_type, \
tsp_ilorsa_ip, \
tsp_data_ip, \
tsp_devicetype, \
tsp_serialnumber, \
tsp_hostname, \
tvp_vm_data_ip, \
tvp_serialnumber, \
tvp_vm_hostname, \
tvp_ilorsa_ip \
from "+o_table+" "


        cmdb_cursor.execute(sql_comp)
	my_logger.debug("sql_comp is " + sql_comp)
	rows = cmdb_cursor.fetchall()
        cmdb_cursor.close()
        cmdb.close()
        return rows



########################################
# write sql query  in csv/xls
#####################################

def process_comp(values):

	output=csv.writer(FILE, dialect='excel')
	with open(filename,"wb+") as csv_file:
		writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
	#print writer
		output.writerow(fieldnames)
		for each_line in values:
                #output.writerow([])
        	        output.writerow(each_line)


	FILE.close()
#cmdb_cursor.close()
#cmdb.close()

'''

table = np.array(rows)
 
wb = pywb.Workbook()
ws = wb.active
ws.title = 'Table 1'
 
tableshape = np.shape(table)
alph = list(string.ascii_uppercase)
 
for i in range(tableshape[0]):
    for j in range(tableshape[1]):
        ws[alph[i]+str(j+1)] = table[i, j]
 
wb.save('Scores.xlsx')

'''

#wb = openpyxl.load_workbook('example.xlsx')


#cur.close()



############################################################################
# Sending Mail
############################################################################

def send_mail():



        emailfrom = (emailfromlist)
        emailto = (emailtolist)
        recipients = [emailtolist]

        fo = open("test.txt", "rb+")
        str = fo.read(1000);
        text = str
        fo.close()


        msg = MIMEMultipart()
        msg["From"] = emailfrom
        msg["To"] = emailto
        msg["Subject"] = emailsubject
        msg.attach(MIMEText(text))

        ctype = "application/octet-stream"
        filename = file1.split('/')
        filnm = filename[-1]
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(file1, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % filnm)
        msg.attach(part)

        server = smtplib.SMTP("smtp.uni.rjil.ril.com:25")
        server.sendmail(emailfrom, emailto, msg.as_string())
        server.quit()
        print "End of total execution, check reports in mail"





def main():
        print "start of script"
        init_db()
        print "delete table done"
        ip_list = ip_read()
        print "ip read complete"
        process_list_ip("ip_", ip_list)
        print "ip record inserted"
        tsp_list = tsp_read()
        print "tsp read complete"
        process_list_tsp("tsp_", tsp_list)
        print "tsp record inserted"
        tvp_list = tvp_read()
        print "tvp read complete"
        process_list_tvp("tvp_", tvp_list)
        print "tvp record inserted"
	compliance_list = compliance_read()
	process_comp(compliance_list)
	print "sending mail"
	send_mail()



# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
        main()






