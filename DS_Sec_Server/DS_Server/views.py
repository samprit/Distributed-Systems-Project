import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)

from data import *

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404

import requests
import time
import fcntl
import json

from server_utils import *

import psutil
import sys, inspect

# users = {'admin':'admin123'}
# ListofIP = ["localhost:8001"]
# PrimIP = "10.5.30.143:8001"

# MainServerIP = "http://localhost:8000"
# SecondaryServerIP = "http://localhost:8001"

MainServerIP = 'http://'+PrimIP
# SecServerIP = 'http://'+SecondaryServerIP

# dirWhereItWillSave = '/home/subham/DS/'
dirWhereItWillSave = parentdir + "/"

@csrf_exempt
def index(request):
	# print "kansdkjndskfj"
	Jname = 'jobidname.json' #should be created beforehand
	jobFile = 'jobFile.json'

	# here we need to handle different POST whether from client or Web
	if request.method == 'POST':
		From = request.POST.__getitem__('From')
		print "Posting From:",From
		if From == 'Client':
			# print "FROM CLIENT"
			Output = request.POST.__getitem__('Output')
			JobStatus = request.POST.__getitem__('JobStatus')
			Jobid = request.POST.__getitem__('Jobid')
			print Jobid, JobStatus
			print "Output", Output
			# print dirWhereItWillSave,jobFile
			with open(lockFile,'w+') as lf:
				fcntl.flock(lf,fcntl.LOCK_EX)
				with open(dirWhereItWillSave+jobFile,'r+') as fp:
					fcntl.flock(fp,fcntl.LOCK_EX)
					jobs = {}
					try:
						jobs = json.load(fp)
						jobs[Jobid][4] = JobStatus
						jobs[Jobid][5] = Output
					except Exception, e:
						jobs = {}
					fp.truncate(0)
					fp.seek(0)
					json.dump(jobs,fp)
					# jobs[self.][1] = self.clientid
					fcntl.flock(fp,fcntl.LOCK_UN)
				fcntl.flock(lf,fcntl.LOCK_UN)
			# url = 'http://'+SecondaryServerIP
			# try:
			# 	r = requests.post(url,data = jobs, proxies= proxyDict)
			# except Exception, e:
			# 	print "SecondaryServer not working"
			return HttpResponse("OK")
		elif From == 'Web': #for handling web request
			# print "FROM WEB"
			# ipAddrOfPOST = str(request.META['REMOTE_ADDR'])
			#save timestamp of post
			# Save the file sent
			# print "Web"
			username = request.POST.__getitem__('username')
			Command = request.POST.__getitem__('Command')
			# print username, Command
			name = ''
			# inputfilename = request.POST.__getitem__('inputfilename')
			for filename, file in request.FILES.iteritems():
				name = request.FILES[filename].name
				fileToSave = request.FILES[filename]
				with open(dirWhereItWillSave + name, 'wb+') as destination:
					for chunk in fileToSave.chunks():
						destination.write(chunk)
			# #read virtual and swap memories
			# fileReceived = open(dirWhereItWillSave + name, "r+")
			# virtualMemory, swapMemory = fileReceived.read().split('\n')[0:2]
			# fileReceived.close()
			# print username
			jobid = -1
			## Function of reading and writing in file
			# print dirWhereItWillSave,Jname
			with open(dirWhereItWillSave+Jname,'r+') as fp:
				fcntl.flock(fp, fcntl.LOCK_EX) # waiting lock to be implemented
				data = {}
				try:
					data = json.load(fp)
				except Exception, e:
					data["Jobid"] = "-1"
				jobid = int(data["Jobid"])+1
				jobid = str(jobid)
				data["Jobid"] = str(jobid)
				fp.truncate(0)
				fp.seek(0)
				json.dump(data, fp)
				fcntl.flock(fp,fcntl.LOCK_UN) # waiting lock to be implemented
			job = retrieve_Job(username,name,Command)
			#print jobid
			print "Job Id Submitted : ", jobid
			with open(lockFile,'w+') as lf:
				fcntl.flock(lf,fcntl.LOCK_EX)
				with open(dirWhereItWillSave+jobFile, 'r+') as fp:
					# print "JobsFile opening"
					fcntl.flock(fp, fcntl.LOCK_EX) # waiting lock
					jobs = {}
					try:
						jobs = json.load(fp)
						# print "Jobs Loaded"
						# print jobs
					except Exception, e:
						jobs = {}
					#print jobs
					jobs[jobid] = job
					fp.truncate(0)
					fp.seek(0)
					# print "New Jobs"
					# print jobs
					json.dump(jobs, fp)
					# print "Dumped ", jobs
					fcntl.flock(fp,fcntl.LOCK_UN) # waiting lock	
				fcntl.flock(lf,fcntl.LOCK_UN)
			# wait to send response until job is complete	
			#print jobs
			# url = 'http://'+SecondaryServerIP
			# payload = {'From':'Server','ClientID':-1,'data':job,'Jobid':jobid}
			# try:
			# 	r = request.POST(url , data = payload, proxies = proxyDict)
			# except Exception, e:
			# 	print "SecondaryServer not working"
			
			return HttpResponse(jobid) #check 
		elif From == 'Server':
			# needs change
			# print "FROM SERVER"

			with open(dirWhereItWillSave+ jobFile, 'r+') as fp:
				# print "abcd"
				jobs = {}
				try:
					jobs = json.load(fp)
				except Exception, e:
					jobs = {}
				ClientID = int(request.POST.__getitem__("ClientID"))
				# print ClientID
				if ClientID < 0:
					# print ClientID
					jobid = int(request.POST.__getitem__('Jobid'))
					# print dict(request.POST)
					jobdata = dict(request.POST)['data']
					# print jobdata
					jobs[jobid] = jobdata
				else:
					for job in jobs:
						if str(jobs[job][1]) == str(ClientID) and jobs[job][4] == "started" :
							jobs[job][4] = "failed"
				fp.truncate(0)
				fp.seek(0)
				json.dump(jobs,fp)
			return HttpResponse("OK")



	elif request.method == 'GET':
		if request.META['HTTP_FROM'] == 'Web':
			username = request.META['HTTP_USERNAME']
			Jobid = request.META['HTTP_JOBID']
			data = loadFromJson(dirWhereItWillSave+jobFile)
			# print "cjjsiodjfi", data, dirWhereItWillSave, jobFile
			JobStatus = data[Jobid][4]
			Output = data[Jobid][5]
			ClientId = data[Jobid][1]
			print "Jobid ", Jobid
			print "Output ", Output
			print "Status ", JobStatus
			print "ClientId ", ClientId
			if JobStatus == "finished":
				return HttpResponse(str(ClientId)+" : "+str(Output))
			else:
				return HttpResponse(str(ClientId)+" : "+str(JobStatus))
		elif request.META['HTTP_FROM'] == 'Server':
			return HttpResponse("IamOK") 
		else:
			raise Http404
			return HttpResponse("failed")


def retrieve_Job(username,filename,command):
	# dirWhereItWillSave = ''
	#retrieve the filename, command, outputfilename, username
	job = [username, -1, dirWhereItWillSave + filename, command, 'pending', '']
	return job