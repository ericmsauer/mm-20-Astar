import json

def nextGuidance(rooms, standard):
	room_guidance = dict()
	queue = list()
	for rid,room in rooms.iteritems(): # rid : room id
		if standard(room):
			room_guidance[rid] = rid
			queue.insert(0, room)
	while queue:
		prev_room = queue.pop()
		prid = prev_room["room"] # previous room id
		for rid in prev_room["connectedRooms"]:
			if not room_guidance.get(rid):
				room_guidance[rid] = prid
				queue.insert(0, rooms[rid])
	return room_guidance

def nextFoodList(rooms):
	standard = lambda room: "FOOD" in room["resources"]
	return nextGuidance(rooms, standard)

def nextSeatList(rooms):
	standard = lambda room: room["seatsTotal"]>=6
	return nextGuidance(rooms, standard)

def nextNearestList(rooms):
	guidance = dict()
	for rid,room in rooms.iteritems():
		standard = lambda room: room["room"] == rid
		guidance[rid] = nextGuidance(rooms, standard)
	return guidance

if __name__ == '__main__':
	room_file = open("room")
	rooms = json.loads(room_file.read())
	room_file.close()
	guidance = dict()
	guidance["food"] = nextFoodList(rooms)
	guidance["seat"] = nextSeatList(rooms)
	guidance["path"] = nextNearestList(rooms)
	guidance_file = open("guidance", "w")
	json.dump(guidance, guidance_file)
	guidance_file.close()
