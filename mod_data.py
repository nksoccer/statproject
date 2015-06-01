with open('data.txt') as f:
    lines = f.readlines()
newlines = []
pastamt = 0
amt = 500

num = 0
while num < len(lines):
	if lines[num].find("Drama Movies") != -1:
		pastamt = amt
		amt = 500
		
	if lines[num].find("Name: ") != -1:
		if lines[num+1].find("Critic Score: 0") != -1 or lines[num+1].find("User Score: 0") != -1:
			amt += -1
			print amt
			num+= 4
			
		else:
			newlines += lines[num]
			newlines += lines[num+1]
			newlines += lines[num+2]
			num += 3
	else:
		newlines += lines[num]
		num+=1

fo = open("data2.txt", 'wb')
for l in newlines:
	fo.write(l)
fo.write("\r\n"+ "n-Values: Action Proccessed - %i, Drama Proccessed - %i" % (pastamt, amt))