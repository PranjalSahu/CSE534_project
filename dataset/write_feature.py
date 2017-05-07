import os
import glob
import sys
import pcapy
import pcap
from shutil import copyfile
import shutil

def get_info(barr):
	tcpdata = barr[34:]
	source_ip   = barr[26:30]
	source_ip_s = str(source_ip[0])+'.'+str(source_ip[1])+'.'+str(source_ip[2])+'.'+str(source_ip[3])
	dest_ip     = barr[30:34]
	dest_ip_s   = str(dest_ip[0])+'.'+str(dest_ip[1])+'.'+str(dest_ip[2])+'.'+str(dest_ip[3])
	source_port = barr[34:36]
	dest_port   = barr[36:38]
	return [str(source_ip_s), str(dest_ip_s)]

def make_folder(path):
	if os.path.exists(path):
		shutil.rmtree(path)
		os.makedirs(path)
	else:
		os.makedirs(path)
	return

def get_event_names():
	f = open('output', 'r')
	r = f.read()
	r = r.split("\n")
	h = {}
	for line in r:
		a = line.split(" ")[0]
		b = line.split(" ")[1]
		h[a] = b
	return h

def get_valid_events():
	f = open('output', 'r')
	r = f.read()
	r = r.split("\n")

	h = {}
	ans = []
	for line in r:
		a = line.split(" ")[0]
		b = line.split(" ")[1]
		if 'garbage' not in b:
			ans.append(a)
	return ans


if __name__ == '__main__':
	all_files   = glob.glob("./filter/*.pcap")
	make_folder('./feature')

	valid_events = get_valid_events()
	event_name_hash = get_event_names()
	print(valid_events)

	events = ['open_user_profile', 'send_message', 'post_on_wall']
	facebook_ips = ['31.13.71.7', '31.13.71.1', '31.13.69.195']

	for filename in all_files:
		print("processing flow "+filename)

		dst = filename.split("/")[2]
		dst = dst.split(".")[0]

		if dst in valid_events:
			reader = pcapy.open_offline(filename)
			client_packets = []
			dest_packets   = []
			total_packets  = []

			while True:
				try:
					(header, payload) = reader.next()
					[source, dest] = get_info(bytearray(payload))
					if source in facebook_ips:
						dest_packets.append(str(len(payload)))
						total_packets.append(str(-1*len(payload)))
					else:
						client_packets.append(str(len(payload)))
						total_packets.append(str(len(payload)))
				except pcapy.PcapError:
					break
			stra = ",".join(client_packets)
			strb = ",".join(dest_packets)
			strc = ",".join(total_packets)

			p = stra+"\n"+strb+"\n"+strc+"\n"+event_name_hash[dst]

			if len(total_packets) >= 8:
				fp = open('./feature/'+dst, 'w')
				fp.write(p)
				fp.close()

