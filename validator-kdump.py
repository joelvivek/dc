#!/usr/bin/env python

import re
import sys
import subprocess
import os

def main():
	path = "/idc/dump"
	# check version 
	version = sys.version_info[0] + (0.1*sys.version_info[1])
        if version < 2.4:
                sys.stderr.write("Current Python version: "+ version + "\nRequired Python version: >= 2.4\n")
                sys.exit(1)

 	# get hostname 	
	p = subprocess.Popen(['hostname'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        hostname = out.rstrip()
	
	# calculate free_space	
	st = os.statvfs("/")
	free_space = st.f_bavail * st.f_frsize / 1024 / 1024 / 1024
	if st.f_bavail * st.f_frsize / 1024 / 1024 / 1024  >= 10:
		free_space = ",SPACE-COMPLIANT"	
	else:
		free_space = ",SPACE-NOT-COMPLIANT"

	# execute command	
	p = subprocess.Popen(['service', 'kdump', 'status'], 
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	if err:
		print hostname+",NOT-INSTALLED,NOT-CONFIGURED,NOT-OPERATIONAL"+free_space


	# parse and validate
	lines = out.split("\n")
	lines.remove('')
	for line in lines:
		if line == "Kdump is operational":
			print hostname+",INSTALLED,CONFIGURED,OPERATIONAL"+free_space
		elif line == "Kdump is not operational":
			file = open("/proc/cmdline", "r")
			try:
				cmd_parameters = file.readlines()
				if cmd_parameters[0].find("crashkernel") != -1 and getPathConfig(path):
					print hostname+",INSTALLED,CONFIGURED,NOT-OPERATIONAL"+free_space
				else:
					print hostname+",INSTALLED,NOT-CONFIGURED,NOT-OPERATIONAL"+free_space
			finally:
				file.close()
def getPathConfig(path):
	file = open("/etc/kdump.conf","r")
	try:
		lines = file.readlines()
		for line in lines:
			line=line.rstrip().lstrip()
			if line == "path "+path:
				return True
			else:
				continue
		return False
	finally:
		file.close()
			
if __name__=='__main__':
	main()
