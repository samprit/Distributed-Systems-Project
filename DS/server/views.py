from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404

import requests
import time
import os

@csrf_exempt
def index(request):
	if request.method == 'POST':
#		print request.META['HTTP_SAM']
#		print request.body
		for filename, file in request.FILES.iteritems():
			name = request.FILES[filename].name
			print name
		return HttpResponse("Got POST")
	elif request.method == 'GET':
		print request
		return HttpResponse("Dipu is great")
	else:
		raise Http404
		return HttpResponse("failed")
