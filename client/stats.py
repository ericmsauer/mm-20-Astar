AI = {'optimization':0.0,'stability':1.0,'complexity':1.0,'theory':0.0,'implementation':0.0}
AI_after = {'optimization':0.0,'stability':1.0,'complexity':1.0,'theory':0.0,'implementation':0.0}
p1 = {'action':'implement','stats':{'coding':10,'refractor':7,'test':7,'optimize':5,'theorize':3}}
p2 = {'action':'optimize','stats':{'coding':5,'refractor':5,'test':7,'optimize':5,'theorize':10}}
p3 = {'action':'implement','stats':{'coding':7,'refractor':10,'test':10,'optimize':5,'theorize':3}}

def change_ai(pa):
	if(pa['action'] == 'theorize'):
		AI_after['theory'] += pa['stats']['theorize']
	elif(pa['action'] == 'refractor'):
		AI_after['complexity'] -= pa['stats']['refractor']
		if(AI_after['complexity'] < 1):
			AI_after['complexity'] = 1.0
	elif(pa['action'] == 'test'):
		AI_after['stability'] += pa['stats']['test']/(AI['complexity']/100)
		if(AI_after['stability'] > 1):
			AI_after['stability'] = 1
	elif(pa['action'] == 'implement'):
		AI_after['implementation'] += pa['stats']['coding']/(AI['complexity']/10)
		AI_after['complexity'] += pa['stats']['coding']/(AI['complexity']/10)
		AI_after['optimization'] -= pa['stats']['coding']/(AI['complexity']/10)/10
		AI_after['stability'] -= pa['stats']['coding']/(AI['complexity']/10)/200
		if(AI_after['stability'] < 0):
			AI_after['stability'] = 0
		if(AI_after['optimization'] < 0):
			AI_after['optimization'] = 0
	elif(pa['action'] == 'optimize'):
		AI_after['optimization'] += pa['stats']['test']/(AI['complexity']/10)
		AI_after['complexity'] += pa['stats']['test']/(AI['complexity']/10)

for i in range(0,600):
	change_ai(p1)
	change_ai(p2)
	change_ai(p3)
	if(AI_after['complexity'] > 1):
		p1['action'] = 'refractor'
		p2['action'] = 'refractor'
		p3['action'] = 'refractor'
	elif(AI_after['implementation'] > AI_after['theory']):
		p1['action'] = 'theorize'
		p2['action'] = 'theorize'
		p3['action'] = 'theorize'		
	elif(AI_after['optimization'] > AI_after['implementation']):
		p1['action'] = 'implement'
		p2['action'] = 'implement'
		p3['action'] = 'implement'
	else:
		p1['action'] = 'optimize'
		p2['action'] = 'optimize'
		p3['action'] = 'optimize'
	AI['optimization'] = AI_after['optimization']
	AI['stability'] = AI_after['stability']
	AI['complexity'] = AI_after['complexity']
	AI['stability'] = AI_after['stability']
	AI['implementation'] = AI_after['implementation']
	AI['theory'] = AI_after['theory']

print AI
