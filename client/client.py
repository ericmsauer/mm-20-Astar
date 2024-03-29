#!/usr/bin/python2
import socket
import json
import random
import sys

def updateMembers(members, value):
    if members is None:
        members = {}
        for person in value["team"].values():
            members[person["person_id"]] = person
    if "people" in value:
        for person in value["people"].values():
            if person["person_id"] in members:
                members[person["person_id"]] = person
    return members

def updateAIState(AI, value):
    AI = AI or {}
    if "aiStats" in value:
        for attr in value["aiStats"]:
            AI[attr] = value["aiStats"][attr]
    return AI

#This function determines what actions to be performed each turn
#
#Edit this to change the behavior of the client
#
#@param members A dictionary of team member's current state indexed by their person_id
#@param value The dictionary with turn info sent by the server
def setActions(members, AI, value):
    actions = []
    for m_id, m in members.iteritems():
        act = {}
        myroom = value["map"][m["location"]]
        act["person_id"] = m["person_id"]
        if "action" not in act:
            if m["fatigue"] > 90:
                act["action"] = "sleep"
            elif m["hunger"] > 75:
                if "FOOD" in myroom["resources"]:
                    act["action"] = "eat"
                else:
                    act["action"] = "view"
            else:
                act["action"] = "theorize"
        actions.append(act)
    return actions

if __name__ == "__main__":
    if len(sys.argv) > 2:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
    else:
        HOST = 'localhost'
        PORT = 8080
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    #Team information is hard-coded here. Change to change team configuration
    s.sendall('{"team":"A*", "members":[{"name":"test1", "archetype":"Architect"},{"name":"test2", "archetype":"Architect"},{"name":"test3", "archetype":"Theorist"}]}\n')
    data = s.recv(1024)
    game_running = True
    members = None
    AI = None
    while len(data) > 0 and game_running:
        value = None
        if "\n" in data:
            data = data.split('\n')
            if len(data) > 1 and data[1] != "":
                data = data[1]
                data += s.recv(1024)
            else:
                value = json.loads(data[0])
                #print 'Received', repr(data[0])
                if 'winner' in value:
                    game_running = False
                else:
                    members = updateMembers(members, value)
                    AI = updateAIState(AI, value)
                    actions = setActions(members, AI, value)
                    s.sendall(json.dumps(actions)+'\n')
                    data = s.recv(1024)
        else:
            data += s.recv(1024)
    s.close()
