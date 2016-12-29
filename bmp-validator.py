#!/usr/bin/env python

import re
import sys
import subprocess

def main():
	version = sys.version_info[0] + (0.1*sys.version_info[1])
	if version < 2.4:
		sys.stderr.write("Current Python version: "+ version + "\nRequired Python version: >= 2.4\n")
		sys.exit(1)
	p = subprocess.Popen(['hostname'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	hostname = out.rstrip()
	p = subprocess.Popen(['vxdmpadm', 'gettune', 'all'], 
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	lines=out.split("\n")
	if lines[0].find("Tunable") == -1:
		sys.stderr.write("VCS is not setup or configured incorrectly\n")
		sys.exit(1)
	for i in range(len(lines)):
		if i!=0 and i!=1 and lines[i]!='':
			words = re.compile('[\t| ]+').split(lines[i])
			if len(words)!=3:
				sys.stderr.write(lines[i])
			else:
				if words[1] == words[2]:
					words.insert(0, hostname)
					words.append("CONFORM")
				else:
					words.insert(0, hostname)
					words.append("NON-CONFIRM")
				print ",".join(words)


if __name__=='__main__':
	main()
