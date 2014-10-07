import random
import json

guidance_file = open("client/guidance")
guidance = json.loads(guidance_file.read())

# This fuction will return the room loc that the member 
# will go to if he wants to get food
def theNextFoodRoom(current):
	return guidance["food"][current]

def theNextSeatRoom(current):
	return guidance["seat"][current]

def theDestinedRoom(current, dest):
	return guidance["path"][dest][current]

def theNearestRoom(current ,rooms):
	return rooms[current]["connectedRooms"][0]

def room_has_avail_seat(current, rooms):
	return rooms[current]['seatsAvailable'] > 0

def room_has_no_people(current, rooms):
	return rooms[current]['peopleInRoom'].length == 1

# This function will return the room loc that the member
# will go next if he want to go to the target room
def findThePath(current, target, rooms):
	return random.choice(rooms[current]["connectedRooms"])

# we can not allow three people go to sleep at the same time!!!
def allowSleep(statues):
	return statues.values().count("sleep")<2

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
		self.member_statuses = {}
		self.turn_count = 0

	def update(self, value):
		# try:
		# 	self.updateMember(value)
		# 	self.updateAIState(value)
		# 	self.updateRoom(value)
		# 	self.updateStatus()
		# 	self.setActions()
		# 	if self.turn_count < 10:
		# 		self.begin_sleep_offset()
		# 	self.turn_count += 1
		# 	self.changingMode()
		# 	print self.AI
		# 	print self.actions
		# except Exception, e:
		# 	print "There is an error"
		self.updateMember(value)
		self.updateAIState(value)
		self.updateRoom(value)
		self.actions = {i:{} for i in self.members.keys()}
		self.updateStatus()
		self.setActions()
		if self.turn_count < 10:
			self.begin_sleep_offset()
		self.turn_count += 1
		self.changingMode()


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
		if "aiStats" in value:
			for attr in value["aiStats"]:
				self.AI[attr] = value["aiStats"][attr]
		else:
			self.AI = {"complexity": 1.0,"implementation": 0.0,"optimization": 0.0,"stability": 1.0,"theory": 0.0}


	def updateRoom(self, value):
		self.rooms = value["map"]

	def updateStatus(self):
		for i in self.members.keys():
			if not self.member_statuses.get(i):
				self.member_statuses[i] = "active"
			if self.member_statuses[i]=="active" and self.members[i]["asleep"]:
				self.member_statuses[i] = "sleep"

	# def updateScheduler(self):
	# 	for schedule in self.wakeup_schedules:
	# 		schedule["count_down"] -= 1

	def setActions(self):
		for mid in self.members.keys():
			for tryFunc in [self.tryWakeUp, self.trySleep, self.tryEat, self.trySeat ,self.tryCode]:
				if not self.actions[mid]:
					tryFunc(mid)
				else:
					break
			self.actions[mid]["person_id"] = mid

	def tryCode(self, mid):
		if self.turn_count > 1350:
			self.actions[mid] = {"action" : "code", "type" : "test"}
			# if we are stablised, we will distract other teams
			# if self.AI['stability']==1.0:
			# 	self.member_statuses[mid] = "distract"
		elif self.AI['theory'] < 1000:
			self.actions[mid] = {"action" : "theorize"}
		elif self.AI['implementation'] < 1000:
			if self.AI['complexity'] > max(1,self.AI['implementation']/4):
				self.actions[mid] = {"action" : "code", "type" : "refactor"}
			else:
				self.actions[mid] = {"action" : "code", "type" : "implement"}
		elif self.AI['optimization'] < 1000:
			if self.AI['complexity'] > max(1,self.AI['implementation']/4):
				self.actions[mid] = {"action" : "code", "type" : "refactor"}
			else:
				self.actions[mid] = {"action" : "code", "type" : "optimize"}

	def trySeat(self, mid):
		member = self.members[mid]
		current = member["location"]
		# if not room_has_avail_seat(current, self.rooms):
		if current != "19" and self.member_statuses[mid]=="active":
			move_loc = theDestinedRoom(current, "19")
			self.actions[mid] = {"action" : "move", "room" : move_loc}

	# If member is hungry, he will eat in the room, set the action to eat
	# If there is no food in the room, he will go to another room, return go action
	# Else it will return None
	def tryEat(self, mid):
		member = self.members[mid]
		my_room = self.rooms[member["location"]]
		status = self.member_statuses[mid]
		if status=="insane":
			return # we will continue coding until death

		if member["hunger"] <= 60 and status!="eat": # they are not hungry
			return # we do nothing
		if member["hunger"] <= 10 and status=="eat":
			self.member_statuses[mid] = "active"
			return # we do nothing
		if "FOOD" in my_room["resources"]: # we have food
			self.actions[mid] = {"action" : "eat"} # we eat
			self.member_statuses[mid] = "eat"
		else:
			# move_loc = theNearestRoom(member["location"] ,self.rooms) # find the room to go to
			move_loc = theNextFoodRoom(member["location"])
			self.actions[mid] = {"action" : "move", "room" : move_loc}

	# If member is fatigue, he will try to sleep, return sleep action
	# schedule others to wake him up at some point, return schedule object 
	def trySleep(self, mid):
		status = self.member_statuses[mid]
		if status=="insane":
			return # we will continue coding until the death

		if not self.members[mid]['asleep'] and self.member_statuses[mid] == 'sleep':
			self.member_statuses[mid] = 'active'
		member = self.members[mid]
		if member["fatigue"] <= 60: # they are not tired
			return # we do nothing
		if allowSleep(self.member_statuses):
			if room_has_avail_seat(member['location'], self.rooms):# and room_has_no_people(member['location'], self.rooms):
				self.actions[mid] = {"action" : "sleep"} # we are going to sleep
				self.member_statuses[mid]="sleep" # we are setting an alarm clock
			else:
				# move_loc = theNearestRoom(member['location'], self.rooms)
				move_loc = theNextSeatRoom(member['location'])
				self.actions[mid] = {'action' : 'move', 'room' : move_loc}

	# If member is fatigue, he will try to sleep, return sleep action
	# schedule others to wake him up at some point, return schedule object 
	def begin_sleep_offset(self):
		mid = self.members.keys()[0]
		if not self.members[mid]['asleep'] and self.member_statuses[mid] == 'sleep':
			self.member_statuses[mid] = 'active'
		member = self.members[mid]
		if allowSleep(self.member_statuses):
			if room_has_avail_seat(member['location'], self.rooms):# and room_has_no_people(member['location'], self.rooms):
				self.actions[mid] = {"action" : "sleep", 'person_id' : mid} # we are going to sleep
				self.member_statuses[mid]="sleep" # we are setting an alarm clock
			else:
				# move_loc = theNearestRoom(member['location'], self.rooms)
				move_loc = theNextSeatRoom(member['location'])
				self.actions[mid] = {'action' : 'move', 'room' : move_loc, 'person_id' : mid}

	def changingMode(self):
		if self.turn_count>1200:
			self.member_statuses = { i : "insane" for i in self.members.keys()}


	# If the alarm is set, we should wake them up immediately
	def tryWakeUp(self, mid):
		if self.members[mid]['asleep']:
			return
		me = self.members[mid]
		wake_id = None # we are going to find a id we are going to wake up
		for i in self.member_statuses.keys():
			member = self.members[i]
			if  self.member_statuses[i]=="sleep" and  member["fatigue"] < 30:
				wake_id = i
				break
		if wake_id is None: # we do nothing if we wakes no one
			return
		if me["location"] == self.members[wake_id]["location"]: # we are in the same room
			self.actions[mid] = {"action" : "wake", "victim" : self.members[wake_id]['person_id']} # we wake them up
			self.member_statuses[wake_id] = "active"
		else:
			# move_loc = findThePath(member["location"], self.members[wake_id]["location"], self.rooms)
			move_loc = theDestinedRoom(me["location"], self.members[wake_id]["location"])
			self.actions[mid] = {'action' : 'move', 'room' : move_loc}

