import requests
import time
import os
import threading
from data import *
from server_utils import *

class Submit_Jobs(threading.Thread):
	    
	    def __init__(self, job, clientid):
	    	threading.Thread.__init__(self)
	    	self.job = job
	    	self.clientid = clientid
	    
	    def run(self):
	    	urlc = "http://"+str(ListofIP[self.clientid])
	    	command = self.job[3]
	    	filename = self.job[2]
	    	payload = {'Command': command , 'Jobid' : self.job[0]}
	    	files = {'file':open(filename,'rb')}
	    	r = requests.post(url,files = files,data = payload, proxies = proxyDict)
	    	#file should be locked
	    	#read jobs from file
	    	#write job back to job dict
	    	# write back to the json file


LastClientUsed = 0
NoClients = 1 # TO BE CHANGED
# Should constantly loop arouund to find whether there is any pending job and send it to a client
while True:
	jobs = loadFromJson("jobs")
	pending_jobs = {}
	pendingJobList = []
	for job in jobs:
		if jobs[job][4] == 'pending' or jobs[job][4] == 'failed':
			pending_jobs[job] = jobs[job]
			pendingJobList.append(job)
	if any(pending_jobs):
		Client = loadFromJson("psutil")
		for i in xrange(0,NoClients):
			if Client[(ListofIP[(LastClientUsed+i) % NoClients]][0] > 15 MB:
				LastClientUsed = LastClientUsed+i % NoClients
				break
		t = Submit_Jobs(pending_jobs[pendingJobList[0]], LastClientUsed)
		t. start()
		#This modifies the json file of job
		# lock the file
		# download the file 
		del pending_jobs[pendingJobList[0]]
		jobs[pendingJobList[0]][4] = 'started'
		jobs[pendingJobList[0]][1] = clientid
		del pendingJobList[0]
		saveAsJson(jobs,"jobs")
		# unlock the file
	time.sleep(3)







