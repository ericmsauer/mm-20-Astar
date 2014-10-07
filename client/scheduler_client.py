from Scheduler import Scheduler
#!/usr/bin/python2
import socket
import json
import random
import sys


if __name__ == "__main__":
	dumpfile = open("dumps", "w")
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
				#print 'Received', repr(data[0])
				if 'winner' in value:
					print value
					game_running = False
				else:
					scheduler.update(value)
					actions = scheduler.actions.values()
					dumpfile.write(str(actions)+"\n")
					s.sendall(json.dumps(actions)+'\n')
					data = s.recv(1024)
		else:
			data += s.recv(1024)
	s.close()
