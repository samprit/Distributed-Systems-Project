#!/usr/bin/python
# DIPAYAN MUKHERJEE
# 11CS30045
import requests
import time
import os
import threading

import sys
import fcntl
import json

from data import *


# need to format the output
def SendGet():
	# This code will send get requests to all clients
	threading.Timer(10.0,SendGet).start()
	responseArr = {}
	for Ip in getListofIP():
		Addr = "http://"+str(Ip)
		print Addr,
		# Addr = "http://localhost:8001"
		try:
			r = requests.get(Addr, proxies = proxyDict, timeout = connect_timeout)
			mem_data = r.content
			mem = mem_data.split("free=")[1]
			mem = mem.split("L")[0]
			print "   is running"
			responseArr[Addr] = int(mem)
		except Exception, e:
			# print e
			print "   is not running"
			responseArr[Addr] = -1


	# with open(psutilFile, "w+") as g:
	# 	fcntl.flock(g, fcntl.LOCK_EX)
	# 	for resp in responseArr:
	# 		g.write(str(resp) + "\n")
	# 	fcntl.flock(g, fcntl.LOCK_UN)

	saveAsJson(responseArr,"psutil")


def main():
	SendGet()
if __name__ == '__main__':
	main()




#section 1 : Handling Get requests from User

#section 2 : Handling Post request from User

#Section 4 : receiving POST from Client
#Section 5 : sending POST request to Client