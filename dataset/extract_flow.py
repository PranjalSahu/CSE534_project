import os
import glob
import sys
import pcapy
import pcap
from shutil import copyfile
import shutil
from random import randint

events = ['open_user_profile', 'send_message', 'post_on_wall']

def make_folder(path):
	if os.path.exists(path):
		shutil.rmtree(path)
		os.makedirs(path)
	else:
		os.makedirs(path)
	return

def get_flow_time(inputfile):
	f = open(inputfile)
	r = f.read()
	r = r.split("\n")
	l = r[0].split(":")[0]
	start_time  = float(l)
	event_times = []
	start_int   = randint(0, 100000)
	global events
	for line in r:
		for event in events:
			if event in line and ' ends' in line:
				p = line.split(":")
				p = p[0]
				p = float(p)
				event_times.append([event, p-start_time, start_int])
				start_int = start_int + 1
	return event_times


def get_time(filename):
	a = pcap.pcap(filename)
	pcap_packets = a.readpkts()
	t = pcap_packets[0][0]
	tp = pcap_packets[-1][0]
	return [t, tp]

if __name__ == '__main__':
	n 		  = int(sys.argv[1]) # number of flows
	filename  = sys.argv[2] # input pcap file
	inputfile = sys.argv[3] # events file
	event_sec = int(sys.argv[4]) # time to consider from the end of event to capture flows

	make_folder('./flows')

	for i in range(0, n):
		print("processing flow "+str(i))
		t = "tshark -r "+filename+" -Y "+"\"(tcp.stream eq "+str(i)+" )\""+" -w "+"./flows/"+str(i)+".pcap"
		print(t)
		os.system(t)
	event_times = get_flow_time(inputfile)

	[start_time, end_time] = get_time('./flows/0.pcap')

	arr = []
	arr_event_id = []
	for i in range(0, n):
		f = './flows/'+str(i)+'.pcap'
		
		[st, et] = get_time(f)
		
		st = st-start_time
		et = et-start_time

		#if t >= event[1] and t <= event[1]+event_sec:

		flag_event = 'garbage'
		event_id   = 0 
		for event in event_times:
			if not((et < event[1]) or (st > event[1]+event_sec)):
				flag_event = event[0]
				event_id   = event[2]
				break
		arr.append(str(i)+" "+flag_event)
		arr_event_id.append(str(i)+" "+str(event_id))

	s = '\n'.join(arr)
	f = open('output', 'w')
	f.write(s)
	f.close()

	s = '\n'.join(arr_event_id)
	f = open('output_event_ids', 'w')
	f.write(s)
	f.close()



