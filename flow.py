import pcapy
import struct
import pcap

def get_port(address_port):
	sa = bin(address_port[0])[2:].zfill(8)
	sb = bin(address_port[1])[2:].zfill(8)
	s  = sa+sb
	i  = 15
	su = 0
	for c in s:
		n = int(c)
		t = pow(2, i)*n
		su = su + t
		i = i - 1
	return su

def get_seq_and_ack(num):
	sa = bin(num[0])[2:].zfill(8)
	sb = bin(num[1])[2:].zfill(8)
	sc = bin(num[2])[2:].zfill(8)
	sd = bin(num[3])[2:].zfill(8)
	s = sa+sb+sc+sd
	i = 31
	su = 0
	for c in s:
		n  = int(c)
		t  = pow(2, i)*n
		su = su+t
		i  = i-1
	return su

# gets the next packet index for a packet
# returns -1 if not found
def get_next_packet(packet, packet_list):
	print 'hello'

# returns number of flows
# and the source for all the flows
def get_flow(packet_list):
	n = len(packet_list)
	flows_list = []
	count = 0
	for i in range(0, n):# search for syn ack
		if packet_list[i][2] == True and packet_list[i][4] ==  True:
			#print(packet_list[i])
			for j in range(i, n):
				if packet_list[j][4] == True and packet_list[i][5] == packet_list[j][6]:
					#print(packet_list[j])
					flows_list.append(packet_list[j][5])
					count = count +1
					break
	return [count, flows_list]

# seq, ack, syn, fin, ack, source_ip, dest_ip
def get_info(barr, count, tts):
	tcpdata = barr[34:]
	source_ip   = barr[26:30]
	source_ip_s = str(source_ip[0])+'.'+str(source_ip[1])+'.'+str(source_ip[2])+'.'+str(source_ip[3])
	dest_ip     = barr[30:34]
	dest_ip_s   = str(dest_ip[0])+'.'+str(dest_ip[1])+'.'+str(dest_ip[2])+'.'+str(dest_ip[3])
	source_port = barr[34:36]
	dest_port   = barr[36:38]
	source_port_s = get_port(source_port)
	dest_port_s   = get_port(dest_port)
	seq_num = barr[38:42]
	ack_num = barr[42:46]
	seqn = get_seq_and_ack(seq_num)
	ackn = get_seq_and_ack(ack_num)
	syn = ord(tcpdata[13:14]) & 0x02 == 0x02
	fin = ord(tcpdata[13:14]) & 0x01 == 0x01
	ack = ord(tcpdata[13:14]) & 0x10 == 0x10
	window = struct.unpack('H', tcpdata[14:16])[0]
	total_length     = get_port(barr[16:18])
	header_length    = ((ord(tcpdata[12:13]) & 0xf0) >> 4) * 32 / 8
	ip_header_length = (ord(barr[14:15]) & 0x0f) * 32 / 8
	window_size = get_port(barr[48:50])
	pa = total_length-(header_length+ip_header_length)
	pb = len(barr)
	payload = (barr[pb-pa:])
	return [seqn, ackn, syn, fin, ack, str(source_ip_s)+":"+str(source_port_s), str(dest_ip_s)+":"+str(dest_port_s), pa, count, window_size*16384, pb, tts, payload]


#gets the first packet after which to start searching for the flow packets
def get_first_packet_index(allpackets, source):
	packet_list = allpackets
	n = len(packet_list)
	for i in range(0, n):
		if packet_list[i][2] == True and packet_list[i][4] ==  True and packet_list[i][6] == source:
			for j in range(i, n):
				if packet_list[j][4] == True and packet_list[i][5] == packet_list[j][6] and (packet_list[j][1]-packet_list[i][0] == 1):
					return j+1



#seq = 1, ack = 1 len = 24
#seq = 1, ack = 25
# part A 2. (a)
def get_first_two_packets(allpackets):
	dest   = '128.208.2.198:80'
	[t, flows_list] = get_flow(allpackets)
	packet_list = allpackets
	n = len(packet_list)
	print('Sequence Number | Ack Number | Receive Window Size')
	for source in flows_list: 	# do for each flow
		foundf = 0
		print('----------------------------------------------')
		j = get_first_packet_index(allpackets, source)
		pl = {}
		for k in range(j, n):
			if packet_list[k][5].startswith(source):# hash by port and sequnce number
				pl[packet_list[k][5]+':'+str(packet_list[k][0]+packet_list[k][7])] = packet_list[k]
			if packet_list[k][5].startswith(dest): # check if pair already present
				if (packet_list[k][6]+':'+str(packet_list[k][1])) in pl:
					p1 = pl[packet_list[k][6]+':'+str(packet_list[k][1])]
					p2 = packet_list[k]
					print(str(p1[0])+' | '+str(p1[1])+' | '+str(p1[9]))
					print(str(p2[0])+' | '+str(p2[1])+' | '+str(p2[9]))
					#print(pl[packet_list[k][6]+':'+str(packet_list[k][1])])
					#print(packet_list[k])
					foundf = foundf+1
					print('-----------------------------')
					pl.pop(packet_list[k][6]+':'+str(packet_list[k][1]), None)
					if foundf == 2:
						break

def getalldata(filename):
	allpackets   = []
	a            = pcap.pcap(filename)
	pcap_packets = a.readpkts()
	reader       = pcapy.open_offline(filename)
	allpackets   = []
	(header, payload) = reader.next()
	tts_start         = pcap_packets[0][0]
	count  = 0
	reader = pcapy.open_offline(filename)
	print('Reading data ............')
	while True:
		try:
			(header, payload) = reader.next()
			allpackets.append(get_info(bytearray(payload), count, pcap_packets[count][0]))
			count = count + 1
		except pcapy.PcapError:
			break
	return allpackets

def filter_by_server(allpackets, port):
	n = len(allpackets)
	selected_packets = []
	for i in range(0, n):
		if port in allpackets[i][5] or port in allpackets[i][6]:
			selected_packets.append(allpackets[i])
	return selected_packets

if __name__ == '__main__':
	filename   =  'fb1.pcap'
	# allpackets = getalldata(filename)
	# get_first_two_packets(allpackets)
	# get_throughput(allpackets)
	# get_average_rtt(allpackets)
	# http_packets     = get_http_data(allpackets)
	# request_response = get_request_response(http_packets, ':8092')
	# flows = get_flow(allpackets)[1]
	print('---------------------------------------------------------------------------------------------------------------')
	print('HTTP VERSIONS')
	filename_a = 'http_8092.pcap'
	filename_b = 'http_8093.pcap'
	filename_c = 'http_8094.pcap'
	allpackets_a = getalldata(filename_a)
	allpackets_b = getalldata(filename_b)
	allpackets_c = getalldata(filename_c)
	flows_a = get_flow(allpackets_a)[1]
	flows_b = get_flow(allpackets_b)[1]
	flows_c = get_flow(allpackets_c)[1]
	if len(flows_b) < len(flows_c):
		print filename_b, 'HTTP 2.0'
		print filename_c, 'HTTP 1.1'
	else:
		print filename_b, 'HTTP 1.1'
		print filename_c, 'HTTP 2.0'
	print('---------------------------------------------------------------------------------------------------------------')
	[bytes_a, count_a] = packets_count_and_size(allpackets_a, ':8092')
	[bytes_b, count_b] = packets_count_and_size(allpackets_b, ':8093')
	[bytes_c, count_c] = packets_count_and_size(allpackets_c, ':8094')
	print('PORT | BYTES SENT | PACKETS SENT')
	print('8092', bytes_a, count_a)
	print('8093', bytes_b, count_b)
	print('8094', bytes_c, count_c)
	print('---------------------------------------------------------------------------------------------------------------')
	filename   = 'assignment2.pcap'
	allpackets = getalldata(filename)
	flows 	   = get_flow(allpackets)[1]
	[retransmissions, ret_keys] = get_total_retransmission(allpackets)
	[retra, triples] = get_triple_and_timeout_ret(allpackets, retransmissions, ret_keys)
	print('SOURCE | TRIPLE DUPLICATE ACK RETRANSMISSIONS | TIMEOUT RETRANSMISSIONS')
	for flow in flows:
		print(flow, retra[flow], triples[flow])
















