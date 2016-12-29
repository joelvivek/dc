#!/usr/bin/env python

import re
import os
import sys
import subprocess

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
	
	# execute command	
	p = subprocess.Popen(['service', 'kdump', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	
	# install kdump
	if err:
		print hostname + ",Not installed. Installing kdump" 
		p = subprocess.Popen(['yum', '-y', 'install', 'kexec-tools'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, installation_err = p.communicate()
		if installation_err:
			print hostname + "," + installation_err
			sys.exit(1)
		else:
			p = subprocess.Popen(['service', 'kdump', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			out, err = p.communicate()
		
	
	# check and configure service
	lines = out.split("\n")
	lines.remove('')
	for line in lines:
		if line == "Kdump is operational":
			print hostname+",Operational"
		elif line == "Kdump is not operational":
			st = os.statvfs(path)
			free_space = st.f_bavail * st.f_frsize / 1024 / 1024 / 1024
			if free_space >= 10:
				setKdumpPath(hostname, path)
			else:
				print hostname+",Not Enough free space (<10G). Aborting"
			file = open("/proc/cmdline", "r")
			try:
				cmd_parameters = file.readlines()
				if cmd_parameters[0].find("crashkernel") == -1:
					addToGrubFile()
				else:
					print hostname + ",Installed and Configured. Starting the service"
					p = subprocess.Popen(['service', 'kdump', 'start'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					output, service_err = p.communicate()
					if service_err:
						print hostname + ","+service_err
					else:
						print hostname + ",Operational"
					sys.exit(0)
					
			finally:
				file.close()
			print hostname + ",Kdump Configured. Reboot for making service Operational."

def addToGrubFile():
	grub_file = open("/boot/grub/grub.conf", "rb+")
	try:
		grub_lines = grub_file.readlines()
		for i, grub_line in enumerate(grub_lines):
			grub_line = grub_line.lstrip('\t ')
			if grub_line.startswith("kernel") and grub_line.find("crashkernel") == -1:
				grub_lines[i] = "\t" + grub_line.rstrip() + getCrashKernel()
		grub_file.seek(0)
		for grub_line in grub_lines:
			grub_file.write(grub_line)
	finally:
		grub_file.close()
	
	
def getCrashKernel():
	# get os_version	
	p = subprocess.Popen(['cat','/etc/issue'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        lines= out.split("\n")
	line = lines[0].split(" ")
	for word in line:
		try:
			version = float(word)
			print version
			if version < 6.3:
				return " crashkernel=0M-2G:128M,2G-6G:256M,6G-8G:512M,8G-:768M\n"
			else:
				return " crashkernel=auto\n"
		except ValueError:
			continue

def setKdumpPath(hostname, path):
	if not os.path.isdir(path):
		print hostname+",Directory "+path+" not found. Creating directories"
		os.makedirs(path)
		print hostname+",Directory Created: "+path

	file = open("/etc/kdump.conf", "rw+")
	try:
		lines = file.readlines()
		found = False
		for i, line in enumerate(lines):
			line = line.rstrip().lstrip()
			if line.startswith("path"):
				found = True
				if line == "path "+path:
					print hostname + "," + "existing path: " + line
					return
				else:
					lines[i] = "path " + path+"\n"
		if not found:
			lines.append("path "+path +"\n")

		file.seek(0)
		for line in lines:
			file.write(line)
		print hostname+",kdump path set to "+path		
	finally:
		file.close()
	
			
if __name__=='__main__':
	main()
