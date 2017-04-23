import os

n = 248
for i in range(1, 248):
	print("processing flow "+str(i))
	t = "tshark -r"+" \"final2.pcap\""+ " -Y "+"\"(tcp.stream eq "+str(i)+" )\""+" -w "+"./flows/"+str(i)+".pcap"
	print(t)
	os.system(t)