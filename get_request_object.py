#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys
import uuid
import re
import json
from collections import namedtuple

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

CLIENT_ACCESS_TOKEN = '71aeb35d73334779a10f6ce54ab9c881'
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
request = ai.text_request()


def create_user() :

 request.session_id = re.sub('[^A-Za-z0-9]+', '', str(uuid.uuid1()))
 return request.session_id


def json_obj(json)	
 x = json.loads(json, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
 print x.contexts.name
 # return x


def get_apai_response(request_str="Hi i need to reset my password"):
    
    request.query = request_str
    response = request.getresponse()
    print (response.read())

get_apai_response()
json_obj(str(response.read()))