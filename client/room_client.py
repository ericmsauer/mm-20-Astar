import random
import json

# This fuction will return the room loc that the member 
# will go to if he wants to get food
def theNearestRoom(current ,rooms):
	return rooms[current]["connectedRooms"][0]

def room_has_avail_seat(current, rooms):
	return rooms[current]['seatsAvailable'] > 0

# This function will return the room loc that the member
# will go next if he want to go to the target room
def findThePath(current, target, rooms):
	return random.choice(rooms[current]["connectedRooms"])

# we can not allow three people go to sleep at the same time!!!
def allowSleep(statues):
	return statues.count("sleep")<2

# we are assume that they will sleep on the chair and no one will not interrupt
def recoveryTime(fatigue, new_fatigue):
	return (fatigue-new_fatigue)*360/100


####
#### We are confusing id at this point and I am going to deal with it later
class Scheduler:
	def __init__(self):
		self.members = None
		self.AI = None
		self.rooms = None
		self.actions = {}
		self.member_statuses = ["active", "active", "active"]
		self.roomInfo = {}


	def update(self, value):
		self.updateMember(value)
		self.updateAIState(value)
		self.updateRoom(value)
		self.setActions()

	def updateMember(self, value):
		if self.members is None:
			self.members = {}
			for person in value["team"].values():
				self.members[person["person_id"]] = person
		if "people" in value:
			for person in value["people"].values():
				if person["person_id"] in self.members:
					self.members[person["person_id"]] = person
	
	def updateAIState(self, value):
		if self.AI is None:
			self.AI = {}
		if "aiStats" in value:
			for attr in value["aiStats"]:
				self.AI[attr] = value["aiStats"][attr]

	def updateRoom(self, value):
		self.rooms = value["map"]

	def setActions(self):
		rid = self.members[1]["location"]
		if self.roomInfo.get(rid) is None:
			self.roomInfo[rid] = self.rooms[rid]
			print self.rooms[rid]
		next_room = random.choice(self.rooms[rid]["connectedRooms"])
		self.actions = [{"action": "move", "room" : next_room, "person_id": 1}]


import socket
import json
import random
import sys


if __name__ == "__main__":
	dumpfile = open("room", "w")
	if len(sys.argv) > 2:
		HOST = sys.argv[1]
		PORT = int(sys.argv[2])
	else:
		HOST = 'localhost'
		PORT = 8080
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	#Team information is hard-coded here. Change to change team configuration
	s.sendall('{"team":"A*", "members":[{"name":"test1", "archetype":"Coder"},{"name":"test2", "archetype":"Architect"},{"name":"test3", "archetype":"Informant"}]}\n')
	data = s.recv(1024)
	game_running = True
	scheduler = Scheduler()
	while len(data) > 0 and game_running:
		value = None
		if "\n" in data:
			data = data.split('\n')
			if len(data) > 1 and data[1] != "":
				data = data[1]
				data += s.recv(1024)
			else:
				value = json.loads(data[0])
				if 'winner' in value:
					game_running = False
				else:
					scheduler.update(value)
					actions = scheduler.actions
					s.sendall(json.dumps(actions)+'\n')
					data = s.recv(1024)
		else:
			data += s.recv(1024)
	#dumpfile.write(str(scheduler.roomInfo))
	json.dump(scheduler.roomInfo, dumpfile)
	dumpfile.close()
	s.close()

