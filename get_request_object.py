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
import random

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai


def create_user():
 session_id = re.sub('[^A-Za-z0-9]+', '', str(uuid.uuid1()))
 print "Session ID : ", session_id
 return session_id


def get_contexts():
    url_contexts = "https://api.api.ai/v1/contexts?sessionId=%s"% sessionId
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization' : 'Bearer 71aeb35d73334779a10f6ce54ab9c881'}
    r = requests.get(url_contexts, headers=headers)
    contexts = json.loads(r.text)
    contexts_names = []
    # print "contexts : ", contexts
    if contexts:
        for context_dict in contexts:
            contexts_names.append(context_dict['name'])
    return contexts_names

def get_json_values():
    with open('intent.json') as json_data:
        d = json.load(json_data)
        return d

def update_state(parameters, contextOut, flagUpdate):
    if currentState["contexts"] and flagUpdate == 1:
        for key in currentState["contexts"].keys():
            if currentState["contexts"][key]["lifespan"] == 0:
                del currentState["contexts"][key]
            else:
                currentState["contexts"][key]["lifespan"] -= 1
    for context in contextOut:
        currentState["contexts"][context] = {"lifespan" : 0}
    for p, v in parameters.iteritems():
        currentState["parameters"][p] = v

######################################### RESPONSE MODULES #################################################################################################################
def get_response(user_says, contextOut, flagOut):
    if flagOut == 1:
        sysResponse, contextOut, parameters, flagOut, flagUpdate = get_response_apiai(user_says, contextOut)
    elif flagOut == 0:
        sysResponse, contextOut, parameters, flagOut, flagUpdate = get_response_custom_logic(user_says, contextOut)
    elif flagOut == -1:
        sysResponse, contextOut, parameters, flagOut, flagUpdate = get_verification_info(user_says, contextOut)
    elif flagOut == -2:
        sysResponse, contextOut, parameters, flagOut, flagUpdate = get_authentication_info(user_says, contextOut)
    update_state(parameters, contextOut, flagUpdate)
    return sysResponse, contextOut, parameters, flagOut

def get_response_apiai(user_says, contextOut):
    # getting reponse from api.ai in json format
    request = ai.text_request()
    request.session_id = sessionId
    request.query = user_says
    response = request.getresponse()
    response_dict = json.loads(response.read().decode('utf-8'))

    # initialization/ default values
    parameters = {}
    flagOut = 1
    flagUpdate = 1
    bot_says = ""

    # getting the name of the intent captured
    intentName = response_dict["result"]["metadata"]["intentName"]
    if intentName == "NO - problem_not_solved":
        if contextOut == ["query_completed_SSPR"]:
            intentName = "NO - problem_not_solved_SSPR"
        else:
            intentName = "NO - problem_not_solved_AD"
    if intentName == "YES - problem_solved":
        if contextOut == ["query_completed_SSPR"]:
            intentName = "YES - problem_solved_SSPR"
        else:
            intentName = "YES - problem_solved_AD"

    if intentName != "Default Fallback Intent":
        jump_status = intent_dict["intent"][intentName]["jump"]["status"]
        contextOut, flagOut = get_contextOut_flagOut(intentName, jump_status)
        contextIn = intent_dict["intent"][intentName]["contextIn"]

        if not (set(contextOut).issubset(set(currentState["contexts"].keys()))) and set(contextIn).issubset(set(currentState["contexts"].keys())):
            parameters = response_dict["result"]["parameters"]
            # print "parameters : ", parameters

            ################## SLOT FILLING ##########################################################
            if "slotFilling" in intent_dict["intent"][intentName].keys():
                parameters, contextOut, bot_says = slot_filling(intentName, parameters, contextOut)
                if contextOut == ["END_CHAT"]:
                    return bot_says, contextOut, parameters, flagOut, flagUpdate
            ##########################################################################################

            if intent_dict["intent"][intentName]["customResponse"] == "N":
                bot_says = random.choice(intent_dict["intent"][intentName]["sysResponse"])
            else:
                bot_says = get_custom_sysResponse(intentName)
        else:
            bot_says = "Can you please not deviate from the topic."
            flagUpdate = 0
    else:
        if intent_dict["intent"]["Default Fallback Intent"]["contexts"].has_key(contextOut[0]):
            bot_says = random.choice(intent_dict["intent"]["Default Fallback Intent"]["contexts"][contextOut[0]]["sysResponse"])
        else:
            bot_says = random.choice(intent_dict["intent"]["Default Fallback Intent"]["defaultMessage"])
        flagUpdate = 0

    return bot_says, contextOut, parameters, flagOut, flagUpdate

def get_response_custom_logic(user_says, contextOut):
    # print currentState
    # print "contextOut : ", contextOut

    for key in intent_dict["intent"].keys():
        try:
            if intent_dict["intent"][key]["contextIn"] == contextOut:
                intentName = key
                break
        except:
            continue
    # print "intentName : ", intentName

    parameters = {}
    contextOut = []
    flagOut = 0
    bot_says = ""
    jump_status = "Y"
    flagUpdate = 1

    if intentName == "query_field1_name_SSPR":
        jump_status = intent_dict["intent"][intentName]["jump"]["status"]
        contextOut, flagOut = get_contextOut_flagOut(intentName, jump_status)
        bot_says = get_custom_sysResponse(intentName)
        parameters = {"name" : user_says}
    # elif intentName == "query_field2_studentId_SSPR":
    #     jump_status = intent_dict["intent"][intentName]["jump"]["status"]
    #     contextOut, flagOut = get_contextOut_flagOut(intentName, jump_status)
    #     bot_says = get_custom_sysResponse(intentName)
    #     parameters = {"studentId" : user_says}

    # print "contextOuuut : ", contextOut
    # print "flagOuuut : ", flagOut
    # print "intentNaaame : ", intentName
    return bot_says, contextOut, parameters, flagOut, flagUpdate

#############################################################################################################################################################################




########################## VERIFICATION MODULES #############################################################################################################################
def get_verification_info(user_says, contextOut):
    bot_says = ""
    parameters = {}
    verification_status = 0
    count = 1

    while (count <= 2):
        parameters = get_verification_parameters(user_says)
        # verification_status = get_verification_status(parameters)
        if count == 2:
            verification_status = 1
        if verification_status == 1:
            bot_says = (random.choice(intent_dict["intent"]["verification_query"]["sysResponsePositive"])).replace("<link>", link)
            contextOut = intent_dict["intent"]["verification_query"]["contextOut"]
            flagOut = flagOut = intent_dict["intent"]["verification_query"]["flagOut"]
            flagUpdate = 1
            break
        else:
            if count == 1:
                bot_says = random.choice(intent_dict["intent"]["verification_query"]["sysResponseRepeat"])
                print "\n\nBot says : ", bot_says
                count += 1
            else:
                bot_says = random.choice(intent_dict["intent"]["verification_query"]["sysResponseNegative"])
                count += 1
                contextOut = ["END_CHAT"]
                flagOut = -1
                flagUpdate = 1

    return bot_says, contextOut, parameters, flagOut, flagUpdate

def get_verification_parameters(user_says):
    for field in verification_fields:
        bot_says = (random.choice(intent_dict["intent"]["verification_query"]["sysResponseTemplates"])).replace("<field>", intent_dict["intent"]["verification_query"]["intent"][field]["name"])
        print "\n\nBot says : ", bot_says
        user_says = get_user_response()
        parameters[intent_dict["intent"]["verification_query"]["intent"][field]["name"]] = user_says
    return parameters

#########################################################################################################################################################################




################################### AUTHENTICATION MODULES ##############################################################################################################
def get_authentication_info(user_says, contextOut):
    bot_says = ""
    parameters = {}
    authentication_status = 0
    count = 1

    while (count <= 2):
        parameters = get_authentication_parameters(user_says)
        # authentication_status = get_authentication_status(parameters)
        if count == 2:
            authentication_status = 1
        if authentication_status == 1:
            bot_says = (random.choice(intent_dict["intent"]["authentication_query"]["sysResponsePositive"])).replace("<link>", link)
            contextOut = intent_dict["intent"]["authentication_query"]["contextOut"]
            flagOut = flagOut = intent_dict["intent"]["authentication_query"]["flagOut"]
            flagUpdate = 1
            break
        else:
            if count == 1:
                bot_says = random.choice(intent_dict["intent"]["authentication_query"]["sysResponseRepeat"])
                print "\n\nBot says : ", bot_says
                count += 1
            else:
                bot_says = random.choice(intent_dict["intent"]["authentication_query"]["sysResponseNegative"])
                count += 1
                contextOut = ["END_CHAT"]
                flagOut = -1
                flagUpdate = 1

    return bot_says, contextOut, parameters, flagOut, flagUpdate

def get_authentication_parameters(user_says):
    for field in authentication_fields:
        bot_says = (random.choice(intent_dict["intent"]["authentication_query"]["sysResponseTemplates"])).replace("<field>", intent_dict["intent"]["authentication_query"]["intent"][field]["name"])
        print "\n\nBot says : ", bot_says
        user_says = get_user_response()
        parameters[intent_dict["intent"]["authentication_query"]["intent"][field]["name"]] = user_says
    return parameters

#############################################################################################################################################################################


def get_contextOut_flagOut(intentName, jump_status):
    contextOut = []
    flagOut = 1
    # if jump_status == "Y":
    #     if intentName == "error_message_1_pass_invalid":
    #         contextOut = intent_dict["intent"][verification_fields[0]["intentId"]]["contextIn"]
    #         if verification_fields[0] != verification_fields[-1]:
    #             flagOut = intent_dict["intent"][verification_fields[0]["intentId"]]["flagIn"]
    #     elif intentName == "query_field1_name_SSPR":
    #         contextOut = intent_dict["intent"][verification_fields[1]["intentId"]]["contextIn"]
    #         if verification_fields[1] != verification_fields[-1]:
    #             flagOut = intent_dict["intent"][verification_fields[1]["intentId"]]["flagIn"]
    # else:
    #     contextOut = intent_dict["intent"][intentName]["contextOut"]
    #     flagOut = intent_dict["intent"][intentName]["flagOut"]

    contextOut = intent_dict["intent"][intentName]["contextOut"]
    flagOut = intent_dict["intent"][intentName]["flagOut"]

    return contextOut, flagOut


def get_custom_sysResponse(intentName):
    bot_says = ""

    if intentName == "query_field3_emailId_SSPR":
        bot_says = random.choice(intent_dict["intent"]["verification_query"]["sysResponse"]).replace("<link>", link)



########################################### VERIFICATION/AUTHENTICATION QUERY FIELDS #############################################################################
def get_verification_fields():
    verification_fields = []
    for field in intent_dict["verification_fields"]:
        if field["status"] == "Y":
            verification_fields.append(field["intentId"])
        # else:
        #     verification_fields.append({})
    # print "verification_fields : ", verification_fields
    return verification_fields


def get_authentication_fields():
    authentication_fields = []
    for field in intent_dict["authentication_fields"]:
        if field["status"] == "Y":
            authentication_fields.append(field["intentId"])
    # print "authentication_fields : ", authentication_fields
    return authentication_fields

####################################################################################################################################################################

def slot_filling(intentName, parameters, contextOut):
    essentialSlots = intent_dict["intent"][intentName]["slotFilling"].keys()
    bot_says = ""
    for slot in essentialSlots:
        while (not parameters[slot]):
            bot_says = intent_dict["intent"][intentName]["slotFilling"][slot]["sysResponse"]
            print "\n\nBot says : ", bot_says
            user_says = get_user_response()
            
            if intentName == "YES - password_reset_problem":
                count_acc_type = 0
                num_count_acc_type = 2
                while (count_acc_type <= num_count_acc_type-1):
                    account_type = get_account_type(user_says)
                    if account_type != "NOT FOUND":
                        parameters[slot] = account_type
                        return parameters, contextOut, ""
                    else:
                        if count_acc_type != num_count_acc_type-1:
                            bot_says = random.choice(["Please enter a valid account name."])
                            print "\n\nBot says : ", bot_says
                            user_says = get_user_response()
                        count_acc_type += 1
                bot_says = random.choice(["I am afraid I do not recognize any account with this name. Sorry, I have to close this chat session. Thank you. Have a good day!"])
                contextOut = ["END_CHAT"]
                break

            else :
                user_says = get_user_response()
                parameters[slot] = user_says
    return parameters, contextOut, bot_says

def get_account_type(user_says):
    for key1 in intent_dict["account_type"].keys():
        for key2 in intent_dict["account_type"][key1]["synonyms"].keys():
            for variation in intent_dict["account_type"][key1]["synonyms"][key2]["variations"]:
                if variation in user_says:
                    return key2
    return "NOT FOUND"


##### get user response ########################
def get_user_response():
    user_says = raw_input("\nUser says : ")
    while (user_says == ""):
        user_says = raw_input("\nUser says : ")
    return user_says
################################################



####################################### MAIN FUNCTION ###############################################################################################################
if __name__ == "__main__":
    # Setting up API.AI
    CLIENT_ACCESS_TOKEN = '71aeb35d73334779a10f6ce54ab9c881'
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    sessionId = create_user()
    currentState = {"contexts" : {}, "parameters" : {}}

    # Getting the name of the institution
    school = raw_input("\nEnter the name of the institution : ")


    print "\n\n####################### CONVERSATION STATUS : START #################################\n\n"

    # getting Intent dictionary
    intent_dict = get_json_values()

    # default values/initializaion
    parameters = {}
    contextOut = []
    flagUpdate = 1
    link = "www.abcd.com"

    # state after default system response
    default_sysResponse = intent_dict["intent"]["Default start message"]["sysResponse"]
    sysResponse = default_sysResponse.replace("<school>", school)
    contextOut = intent_dict["intent"]["Default start message"]["contextOut"]
    update_state(parameters, contextOut, flagUpdate)

    print "\n\nBot says : ", sysResponse
    # print "\ncontextOut : ", contextOut
    # print "\ncurrentState : ", currentState

    # getting verification/authentication fields
    verification_fields = get_verification_fields()
    authentication_fields = get_authentication_fields()

    # <flagOut> to decide who is going to get the intent for the next user utterance (api.ai/ custom logic)
    flagOut = intent_dict["intent"]["Default start message"]["flagOut"]

    # conversation flow
    while("END_CHAT" not in contextOut):
        # recording user utterance
        if flagOut != -1 and flagOut != -2:
            user_says = get_user_response()

        # getting response details
        sysResponse, contextOut, parameters, flagOut = get_response(user_says, contextOut, flagOut)

        print "\n\nBot says : ", sysResponse
        # print "\ncontextOut : ", contextOut
        # print " \ncurrentState : ", currentState

    print "\n\n######################## CONVERSATION STATUS : END #####################################\n\n"







