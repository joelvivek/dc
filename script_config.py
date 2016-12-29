#!/usr/bin/python
# This file contains Global and IPAM config vars for the IPAM database update.

# Author : Aniket Gole
# Contributor : Joel Raja, Iram Khan
# Email : aniket.gole@gmail.com; joelvivek.raja@ril.com; iram1.khan@ril.com
# Global Variable #################################################################
import time
import os
import sys

mysql_server_dev = {
		 "mysql_host"	: "10.137.2.81",
	         "mysql_user"   : "aniket",
	         "mysql_passwd" : "@n!kEt",
	         "mysql_database"  : "cmdb"
}
mysql_server = {
		 "mysql_host"	: "10.137.2.100",
	         "mysql_user"   : "autouser",
	         "mysql_passwd" : "idcautouser@567",
	         "mysql_database"  : "cmdb"

}
# IPAM Variable #################################################################
'''
#For IPAM dev env enable this 
ipam_var = {
	#"endpoint" : 'http://10.135.11.94:8053/API/NSService_10/soap11/descriptiontest',
	"endpoint" : 'http://10.135.11.94:8053/API/NSService_10/soap11/description',
	"keyname" : 'test',
	"transactionkey" : 'mYWBA38ktN3Z6uHNBj653aKSpoSUU1GNZKZW8SicEJI=',
	"family" : 'IPv4',
	"blocktype" : 'address_set',
	"subnet_value" : False,
	"owner" : 'Reliance Jio Infocomm Ltd'
}
'''
#commenting the real server
ipam_var = {
    "endpoint" : 'https://10.70.4.12:8443/API/NSService_10/soap11/description',
    "keyname" : 'oss',
    "transactionkey" : '8f2qkMd6uZEoiEtSOKwWG8zpF6WnyfoGGg904GyzlOU=',
    "family" : 'IPv4',
    "blocktype" : 'address_set',
    "subnet_value" : False,
    "owner" : 'Reliance Jio Infocomm Ltd'
}

mail_var = {
	"FROM" : 'rjil.notification@rjil.net',
#	"TO" : ['joelvivek.raja@ril.com'],
#	"CC" : ['joelvivek.raja@ril.com'],
# commenting the mail ids
    "TO" : ['aniket.gole@rjil.net', 'Shashikant.Gunjkar@ril.com', 'aniket.gole@ril.com', 'rupesh.thakur@ril.com', 'Manan.Gandhi@ril.com', 'anant.nagvekar@ril.com', 'Vishal.Sable@ril.com', 'Satish.Gurumurthy@ril.com', 'Shankar.Ramakrishnan@ril.com', 'Shailendra.Dwivedi@ril.com', 'Dhiren.Dedhia@ril.com', 'JioDC.PnE@ril.com', 'RJIL.IDCOPSCore@ril.com'], 
    "CC" : ['RJIL.IDCAutomation@ril.com'],
	"SUBJECT" : "CMDB-to-IPAM Status Notification!!!",
	"TEXT" : "This is automated notification about CMDB to IPAM status.",
	"SERVER" : "smtp.uni.rjil.ril.com",
	"PORT" : "25"
}

mysql_query = {

        "base" : "select t_ipstatus.subnet, t_ipstatus.ip, t_ipstatus.ip_status, t_ipstatus.environment, t_server_provisioning.hostname, t_server_provisioning.serialnumber, t_ipstatus.ipam_update from t_ipstatus, t_server_provisioning where t_ipstatus.ip=t_server_provisioning.data_ip and t_ipstatus.ipam_update='NEW' and t_ipstatus.ip_status = 'USED'",
        "vm" : "select t_ipstatus.subnet, t_ipstatus.ip, t_ipstatus.ip_status, t_ipstatus.environment, t_vm_provisioning.vm_hostname, t_vm_provisioning.vm_serialnumber, t_ipstatus.ipam_update from t_ipstatus, t_vm_provisioning where t_ipstatus.ip=t_vm_provisioning.vm_data_ip and t_ipstatus.ipam_update='NEW' and t_ipstatus.ip_status = 'USED'",
	"dele" :"select t_ipstatus.subnet, t_ipstatus.ip from t_ipstatus, T_Server_Decommission where t_ipstatus.ip=T_Server_Decommission.data_ip and t_ipstatus.ip_status = 'USED' and t_ipstatus.ipam_update ='NEW' ",

	"pubip" : "select t_ipstatus.subnet, t_ipstatus.ip, t_ipstatus.ip_status, t_ipstatus.environment, t_ipstatus.hostname, t_ipstatus.serialnumber, t_ipstatus.ipam_update, t_ipstaus.application_name, t_ipstatus.application_owner_contact_email from t_ipstatus where lower(type) like 'public%' and ipam_update='NEW'"

# 	"base" :"select t_ipstatus.subnet, t_ipstatus.ip, t_ipstatus.ip_status, t_ipstatus.environment, t_server_provisioning.hostname, t_server_provisioning.serialnumber, t_ipstatus.ipam_update from t_ipstatus, t_server_provisioning where  t_ipstatus.ip=t_server_provisioning.data_ip and t_ipstatus.subnet = '192.168.1.0/22'",

#       "vm" :"select t_ipstatus.subnet, t_ipstatus.ip, t_ipstatus.ip_status, t_ipstatus.environment, t_vm_provisioning.vm_hostname, t_vm_provisioning.vm_serialnumber, t_ipstatus.ipam_update from t_ipstatus, t_vm_provisioning where t_ipstatus.ip=t_vm_provisioning.vm_data_ip and t_ipstatus.ipam_update='NEW' and t_ipstatus.ip = '192.168.86.18'",

#       "dele" :"select t_ipstatus.subnet, t_ipstatus.ip from t_ipstatus where t_ipstatus.subnet = '10.135.12.0/22' and t_ipstatus.ip = '10.135.12.92' ",

#      "pubip" : "select '49.40.0.0/16' subnet, map.public_ip ip,  ip.ip_status, ip.environment, GROUP_CONCAT(vser.hostname SEPARATOR ', ' ) hostname, vser.serialnumber, ip.ipam_update,  vser.application_name, vser.application_owner_contact_email from  cmdb.public_ip_map map, cmdb.t_ipstatus ip, cmdb.V_SERVER vser where  ip.ip = map.private_ip and ip.ip = vser.data_ip and public_ip like '49.40.%' GROUP BY public_ip  "

}


today = time.strftime("%d-%m-%Y-%H:%M")
date = time.strftime("%d-%m-%Y")
table_file = 'table_file'
logfile_name= 'ipam_host_ipdate_' + date +'.log'
script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
logfile = script_dir + '/logs/' + logfile_name


