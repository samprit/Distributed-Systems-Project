import requests
import time
import os
import threading
import json
from data import *
from server_utils import *

class Submit_Jobs(threading.Thread):
	    
	    def __init__(self, job,jobid, clientid):
	    	threading.Thread.__init__(self)
	    	self.job = job     # this job is a list needs different handling
	    	self.clientid = clientid
	    	self.jobid = jobid
	    
	    def run(self):
	    	# print "Submitting"
	    	urlc = "http://"+str(ListofIP[self.clientid])
	    	print "Client",self.clientid
	    	print urlc
	    	command = self.job[3]
	    	filename = self.job[2]
	    	payload = {'Command': command , 'Jobid' : self.jobid}
	    	files = {'file':open(filename,'rb')}
	    	response = 1
	    	r = requests.post(urlc,files = files,data = payload, proxies = proxyDict)
	    	if r.status_code == requests.codes.ok:
	    		response = 1
	    		print "Sent to client"
	    	else:
	    		response = 0
	    	# print "cnsdkjfnj"
	    	if response == 0:
	    		with open(jobFile,'r+') as fp:
	    			# print "waiting for lock 1"
	    			fcntl.flock(fp,fcntl.LOCK_EX)
	    			# print "lock acquired 1"
	    			jobs = json.load(fp)
	    			print "Jobs For Submitting Error"
	    			# print jobs
	    			jobs[self.jobid][4] = 'failed-request'
	    			jobs[self.jobid][1] = self.clientid
	    			fp.truncate(0)
	    			fp.seek(0)
	    			json.dump(jobs,fp)
	    			fcntl.flock(fp,fcntl.LOCK_UN)
	    			# print "lock released 1"
	    			url = 'http://'+SecondaryServerIP
	    			payload = {'data' : jobs[self.jobid] , 'From' : 'Server','Jobid' : self.jobid , 'ClientID' : -1} # for secondary server to know who sent it need to change in the secondary server server part
	    			# ClientID = -1 means no client failure, otherwise it means the given ID has failed
	    			ro = requests.post(url,data = payload, proxies= proxyDict) # can send only the jobs to reduce the messages


class Client_Failure(threading.Thread):

	def __init__(self,clientid):
		threading.Thread.__init__(self)
		self.clientid = clientid
	def run(self):
		print "Client_Failure", self.clientid
		with open(jobFile, 'r+') as fp:
			fcntl.flock(fp, fcntl.LOCK_EX) # waiting lock to be added
			jobs = {}
			try:
				jobs = json.load(fp)
			except Exception, e:
				jobs = {}
			
			for job in jobs:
				if jobs[job][1] == self.clientid and jobs[job][4] == "started" :
					jobs[job][4] = "failed"
			fp.truncate(0)
			fp.seek(0)
			json.dump(jobs, fp)
			fcntl.flock(fp, fcntl.LOCK_UN) # waiting lock to be added
			url = 'http://'+SecondaryServerIP
			payload = {'From':'Server','ClientID':self.clientid}
			r = requests.post(url,data=payload,proxies=proxyDict)


LastClientUsed = 0
NoClients = len(ListofIP)
# Should constantly loop arouund to find whether there is any pending job and send it to a client
while True:
	print "JobHandler"
	# print "Jobs"
	jobs = loadFromJson("jobs")
	# print jobs
	pending_jobs = {}
	pendingJobList = []
	for job in jobs:
		# print "Within"
		# print job
		if jobs[job][4] == 'pending' or jobs[job][4] == 'failed':
			pending_jobs[job] = jobs[job]
			pendingJobList.append(job)
	# print pendingJobList
	# print pending_jobs
	if any(pending_jobs):
		# print "Changing jobs"
		print "No of clients",NoClients
		Client = loadFromJson("psutil")
		
		for i in xrange(1,NoClients+1):
			print "Last", LastClientUsed
			if int(Client["http://"+str(ListofIP[(int(LastClientUsed)+int(i))% int(NoClients)])]) == -1:
				FailedID = (int(LastClientUsed)+ int(i)) % int(NoClients)
				c = Client_Failure(FailedID)
				c.start()
			if int(Client["http://"+str(ListofIP[(int(LastClientUsed)+int(i)) % int(NoClients)])]) > 15000000:
				LastClientUsed = (int(LastClientUsed)+int(i)) % int(NoClients)
				break
		print "LastClientUsed", LastClientUsed 
		t = Submit_Jobs(pending_jobs[pendingJobList[0]],pendingJobList[0], LastClientUsed)
		t.start()
		# print "Job Submitted"
		print "ID Submitted", pendingJobList[0]
		print "-------------------------"
		del pending_jobs[pendingJobList[0]]
		with open(jobFile,'r+') as fp:
			print "waiting for lock 1"
			fcntl.flock(fp,fcntl.LOCK_EX)
			print "lock acquired 1"
			DwJob = json.load(fp)
			# print "Job Correct Submission", DwJob
			if DwJob[pendingJobList[0]][4] == 'failed-request':
				DwJob[pendingJobList[0]][4] = 'failed'
			else:
				DwJob[pendingJobList[0]][4] = 'started'
				DwJob[pendingJobList[0]][1] = int(LastClientUsed)
			fp.truncate(0)
			fp.seek(0)
			# print "After Changing"
			# print DwJob
			json.dump(DwJob,fp)
			fcntl.flock(fp,fcntl.LOCK_UN)
			print "lock released 1"
		url =  'http://'+SecondaryServerIP
		payload = {'data': DwJob[pendingJobList[0]] ,'From':'Server','Jobid': pendingJobList[0],'ClientID': -1}
		try:
			r = requests.post(url,data = payload,proxies= proxyDict, timeout = connect_timeout)
		except Exception, e:
			print "SecondaryServer not workng"
		
		print "trying to delete"
		del pendingJobList[0]
		print "deleted...."
	time.sleep(3)







