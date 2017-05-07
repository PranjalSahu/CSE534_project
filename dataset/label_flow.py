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

if __name__ == '__main__':
	ip_to_check = sys.argv[1]
	all_files   = glob.glob("./flows/*.pcap")
	allips = {}
	facebook_ips = ['31.13.71.7', '31.13.71.1', '31.13.69.195']
	
	make_folder("./domain")
	for filename in all_files:
		reader = pcapy.open_offline(filename)
		(header, payload) = reader.next()
		pinfo = get_info(bytearray(payload))
		if (pinfo[0] in facebook_ips) or (pinfo[1] in facebook_ips):
			dst = filename.split("/")[2]
			dst = './domain/'+dst
			copyfile(filename, dst)