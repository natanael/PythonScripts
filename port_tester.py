import threading
import socket
import time
"""
This tests all ports on a hardcoded network address.
Works and is kind of fast. 

I used code I found on the internet, changed some small things.
"""


target = 'ep500-be'
s = time.time()
threads = {}
t_range = 65535
t_ports = range(t_range)
ports = []
dead_threads = []

def garbage_collector():
  while len(t_ports) or len(dead_threads):
		while len(dead_threads):
			pp = dead_threads.pop()
			threads[pp].join()
			if len(t_ports):
				print "A T dies another T rises. %d left" % len(t_ports)
				np =t_ports.pop()
				try:
					t = threading.Thread(target=check_port,args=(target,np))
					t.start()
					threads[np] = t
				except:
					t_ports.append(np)
	print "Finished..."

gc = threading.Thread(target=garbage_collector)			
		
def close_ts(p):
	dead_threads.append(p)

def check_port(ip,port):
	s = socket.socket()
	if s.connect_ex((ip,port)) == 0:
		ports.append(port)
	s.close()
	close_ts(port)

print "Starting.."
gc.start()
while len(t_ports):
	p = t_ports.pop()
	t = threading.Thread(target=check_port,args=(target,p))
	try:
		t.start()
		threads[p]=t
	except:
		t_ports.append(p)
		print "Max threads: %d" % (len(threads.keys()) + 1)
		break
		
print "Commiting..."
for x in threads.keys():
	threads[x].join()
gc.join()
	
print ports
print time.time() - s
