import os
import glob
import sys
import pcapy
import pcap
from shutil import copyfile
import shutil

def make_folder(path):
	if os.path.exists(path):
		shutil.rmtree(path)
		os.makedirs(path)
	else:
		os.makedirs(path)
	return

if __name__ == '__main__':
	all_files   = glob.glob("./domain/*.pcap")
	make_folder('./filter')
	for filename in all_files:
		print("processing flow "+filename)
		dst = filename.split("/")[2]
		filter_str = "\"not tcp.analysis.retransmission && not (tcp.flags.ack==1 && tcp.len == 0) && not mdns && not tcp.flags.reset ==1 && not dns && not igmp && not tcp.flags.syn==1\""
		t = "tshark -r "+filename+ " -Y "+filter_str+" -w "+"./filter/"+dst
		os.system(t)