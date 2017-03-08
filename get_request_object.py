#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import sys
import uuid
import re
import json
from collections import namedtuple
import urllib2
import requests
import json

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai


def create_user() :
 session_id = re.sub('[^A-Za-z0-9]+', '', str(uuid.uuid1()))
 print session_id
 return session_id


def get_apiai_response(request_str):
    request.query = request_str
    response = request.getresponse()
    print "response : \n", response.read()
    # try:
    #     json_data = json.load(response)
    # except ValueError, e:
    #     print e
    #     print "ERROR"
    print json.load(response)
    return response_dict

def get_contexts():
	url_contexts = "https://api.api.ai/v1/contexts?sessionId=%s"% sessionId
	headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization' : 'Bearer 71aeb35d73334779a10f6ce54ab9c881'}
	r = requests.get(url_contexts, headers=headers)
	# print json.loads(r.text)
	return json.loads(r.text)

if __name__ == "__main__":
	CLIENT_ACCESS_TOKEN = '71aeb35d73334779a10f6ce54ab9c881'
	ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
	state_variable = {}
	state_variable = {"contexts" : [], "parameters" : []}
	# request.session_id = create_user()

	verification_Bot_says = [""]
	sessionId = create_user()
	flag = 1 # to decide when to call api.ai

	while(1):
		user_says = raw_input("User says : ")

		active_contexts = get_contexts()
		if flag == 1:
			request = ai.text_request()
			request.session_id = sessionId
			response = get_apiai_response(user_says)
			print "Bot says : ", response["result"]["fulfillment"]["displayText"]




