#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gnuradio import gr, blks2
from gnuradio import uhd,window,audio,digital
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import string, time, struct,sys, math, os
import ofdm
import usrp_transmit_path
from multiprocessing import Process,Value

class transmit(gr.top_block):
	def __init__(self, options):
	    gr.top_block.__init__(self)
	    self.txpath = usrp_transmit_path.usrp_transmit_path(options)
	    self.connect(self.txpath)

	def _print_verbage(self):
	    print "Using TX d'board %s"    % (self.subdev.side_and_name(),)
	    print "modulation:      %s"    % (self._modulator_class.__name__)
	    print "interp:          %3d"   % (self._interp)
	    print "Tx Frequency:    %s"    % (eng_notation.num_to_str(self._tx_freq))

        def string_pass(): 
	    fd=open('string_pipe','r')
	    string=fd.read()
	    usrp_transmit_path.string_pass_l2(string) 
                
def transmitter_control(mp,Freq,norestart,sync,Frequency,position):
    while(1):
	sys.stderr.write('\nIn transmitter_control:\n')
	while (norestart.value==1):
		time.sleep(2)
	norestart.value = 1       
	mp.terminate()
	if (sync.value ==1):
	    Freq.value = 920*10**6
	else:
	    Freq.value = Frequency.value
	#trans = trans_init(Freq)
	#tb = trans.return_obj()
	#mp = Process(target = sync , args = (tb))
	#mp.start()
	#time.sleep(1)
	#mp.terminate()
	#n = sync(tb)
	#Freq.value = Frequency
	#print 'before starting'
	mp = Process(target = Start_transmitter,args=(Freq,norestart,sync,Frequency,position))
	mp.start() 
	
def synchronization(tb):    
	time.sleep(2)
	tb.start() 
	n= 0
	pktno = 150
	print "\nTransmitting in", Freq.value ,"Hz", " containing synchronization packet"
	preamble = 11111
	while n < 100:
	      data = struct.pack('!L', Frequency.value & 0xffffffff)#str(Frequency.value)
	      payload = struct.pack('!H', pktno & 0xffff) + struct.pack('!H', preamble & 0xffff) + data # Constructing a packet. Pack a string in to given format. http://docs.python.org/library/struct.html
	      send_pkt(tb,payload)				     # Sending packet
	      n += 1
	      pktno += 1
	      sys.stderr.write('.')				     # error message
	time.sleep(1)
	sync.value = 0
	norestart.value=0
	tb.stop()
	tb.wait()
	return n
        		   
class trans_init():
    def __init__(self,Freq): 
        global parser
        parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
	expert_grp = parser.add_option_group("Expert")
	parser.add_option("-s", "--size", type="eng_float", default=1024, help="set packet size [default=%default]")
	parser.add_option("-M", "--megabytes", type="eng_float", default=10.0, help="set megabytes to transmit [default=%default]")
	parser.add_option("","--discontinuous", action="store_true", default=False, help="enable discontinuous mode")
	parser.add_option("","--from-file", default=None, help="use file for packet contents")
        parser.add_option("-e", "--interface", type="string", default="eth0", help="Select ethernet interface. Default is eth0")
	parser.add_option("-m", "--MAC_addr", type="string", default="", help="Select USRP2 by its MAC address.Default is auto-select")
	parser.add_option("-j", "--start", type="eng_float", default=1e7, help="Start ferquency [default = %default]")
	parser.add_option("-k", "--stop", type="eng_float", default=1e8,help="Stop ferquency [default = %default]")
	parser.add_option("", "--tune-delay", type="eng_float", default=20e-3, metavar="SECS", help="time to delay (in seconds) after changing frequency[default=%default]")
	parser.add_option("", "--dwell-delay", type="eng_float",default=1e-3, metavar="SECS", help="time to dwell (in seconds) at a given frequency[default=%default]")
	parser.add_option("-G", "--gain", type="eng_float", default=None,help="set gain in dB (default is midpoint)")
	parser.add_option("-s", "--fft-size", type="int", default=2048, help="specify number of FFT bins [default=%default]")# changed default value(256)
	parser.add_option("-d", "--decim", type="intx", default=4, help="set decimation to DECIM [default=%default]")	# changed default value(16)
        parser.add_option("-i", "--input_file", default="", help="radio input file",metavar="FILE")
        parser.add_option("-S", "--sense-bins", type="int", default=128, help="set number of bins in the OFDM block [default=%default]")
	
	usrp_transmit_path.add_options(parser, expert_grp)
	ofdm.ofdm_mod.add_options(parser, expert_grp)
	(self.options, self.args) = parser.parse_args ()
	if len(self.args) != 0:
		parser.print_help()
		sys.exit(1)
	if self.options.tx_freq is None:
		sys.stderr.write("You must specify -f FREQ or --freq FREQ\n")
		parser.print_help(sys.stderr)
		sys.exit(1)
	self.options.tx_freq=Freq.value
	self.tb = transmit(self.options)
	r = gr.enable_realtime_scheduling()
	if r != gr.RT_OK:
		print "Warning: failed to enable realtime scheduling"
    
    def Data(self):    
            return self.options.megabytes 
            
    def return_obj(self):
           return self.tb     
    
    def return_options(self):
           return self.options
        
#################################################)##################################################################################################################
                                                              #SENSING CODE 
###################################################################################################################################################################
                                                                                                           
class tune(gr.feval_dd):
    def __init__(self, tb):
	gr.feval_dd.__init__(self)
	self.tb = tb
	
    def eval(self, ignore):
	try:
	    new_freq = self.tb.set_next_freq()
	    return new_freq
	except Exception, e:
	    print "tune: Exception: ", e
	    
class parse_msg(object):
    def __init__(self, msg):
	self.center_freq = msg.arg1()
	self.vlen = int(msg.arg2())
	assert(msg.length() == self.vlen * gr.sizeof_float)
	t = msg.to_string()
	self.raw_data = t
	self.data = struct.unpack('%df' % (self.vlen,), t)

class sensor(gr.top_block):
    def __init__(self,options):
	gr.top_block.__init__(self)
	if options.input_file == "":
	    self.IS_USRP2 = True
	else:
	    self.IS_USRP2 = False
	#self.min_freq = options.start
	#self.max_freq = options.stop
	self.min_freq = 905*10**6-(10*10**6) # same as that of the transmitter bandwidth ie 6MHZ approx for a given value of decimation line option any more
	self.max_freq = 905*10**6+(10*10**6)
	if self.min_freq > self.max_freq:
	    self.min_freq, self.max_freq = self.max_freq, self.min_freq # swap them
	    print "Start and stop frequencies order swapped!"
	self.fft_size = options.fft_size
	self.ofdm_bins = options.sense_bins
	# build graph
	s2v = gr.stream_to_vector(gr.sizeof_gr_complex, self.fft_size)
	mywindow = window.blackmanharris(self.fft_size)
	fft = gr.fft_vcc(self.fft_size, True, mywindow)
	power = 0
	for tap in mywindow:
	    power += tap*tap
	c2mag = gr.complex_to_mag_squared(self.fft_size)
	# modifications for USRP2 
	if self.IS_USRP2:	
	    self.u = uhd.usrp_source(options.args,uhd.io_type.COMPLEX_FLOAT32,num_channels=1)		# Modified Line
	    # self.u.set_decim(options.decim)
	    # samp_rate = self.u.adc_rate()/self.u.decim()
	    samp_rate = 100e6/options.decim		# modified sampling rate
	    self.u.set_samp_rate(samp_rate)
	else:
	    self.u = gr.file_source(gr.sizeof_gr_complex,options.input_file, True)
	    samp_rate = 100e6 /options.decim		# modified sampling rate

	self.freq_step =0 #0.75* samp_rate
	self.min_center_freq = (self.min_freq + self.max_freq)/2
	
	global BW
	BW = self.max_freq - self.min_freq
	global size
	size=self.fft_size
	global ofdm_bins
	ofdm_bins = self.ofdm_bins
	global usr
	#global thrshold_inorder
	usr=samp_rate
	nsteps = 10 
	self.max_center_freq = self.min_center_freq + (nsteps * self.freq_step)
	self.next_freq = self.min_center_freq
	tune_delay = max(0, int(round(options.tune_delay * samp_rate / self.fft_size))) # in fft_frames
	dwell_delay = max(1, int(round(options.dwell_delay * samp_rate / self.fft_size))) # in fft_frames
	self.msgq = gr.msg_queue(16)					# thread-safe message queue
	self._tune_callback = tune(self) 				# hang on to this to keep it from being GC'd
	stats = gr.bin_statistics_f(self.fft_size, self.msgq, self._tune_callback, tune_delay,
				      dwell_delay)			# control scanning and record frequency domain statistics
	self.connect(self.u, s2v, fft,c2mag,stats)
	if options.gain is None:
	    g = self.u.get_gain_range()
	    options.gain = float(g.start()+g.stop())/2			# if no gain was specified, use the mid-point in dB
	    
    def set_next_freq(self):
	target_freq = self.next_freq
	self.next_freq = self.next_freq + self.freq_step
	if self.next_freq >= self.max_center_freq:
	    self.next_freq = self.min_center_freq
	if self.IS_USRP2:
	    if not self.set_freq(target_freq):
	        print "Failed to set frequency to ", target_freq, "Hz"
	return target_freq
	
    def set_freq(self, target_freq):
	#return self.u.set_center_freq(target_freq)
	return self.u.set_center_freq(target_freq,0)
    def set_gain(self, gain):
	#self.u.set_gain(gain)
	self.u.set_gain(gain,0)
	
def sensor_init(options):
    tb1=sensor(options)
    return tb1
    
def sense_loop(tb,Frequency):
    print "\n\nSensing the spectrum"
    time.sleep(2)
    tb.start()						# Added Line
    moving_avg_data = [0]*(size)
    count = 11
    avg_iterations = avg_iter_count = 10
    while count>0:
	count=count-1
	#hexa_thr=""
	m = parse_msg(tb.msgq.delete_head())
	if avg_iter_count > 0:
		for i in range(0,size):
		      moving_avg_data[i] = moving_avg_data[i] + m.data[i]
		avg_iter_count = avg_iter_count - 1
	else: 
		for i in range(0,len(moving_avg_data)):
			moving_avg_data[i] = moving_avg_data[i]/float(avg_iterations)
		thrshold = map(lambda x: 0 if x>0.001 else 1, moving_avg_data)		# Modified threshold	
		thrshold_inorder= [0]*size
		sensed_freq = [0]*size
		avg_data = [0]*(size)
		ofdm_center_freq = m.center_freq # For now we are keeping the center freq of the ofdm same as that of sensing, will have to modify this later
		freq_resolution = usr/size
		p = m.center_freq - freq_resolution*((size/2)-1)
		for i in range(0,size/2):
			sensed_freq[i]= p	
			print p,  moving_avg_data[i+size/2], thrshold[i+size/2]
			p=p+freq_resolution
			thrshold_inorder[i] = thrshold[i+size/2]
			avg_data[i] = moving_avg_data[i+(size/2)]
		
		for i in range(0,size/2):
			sensed_freq[i+size/2] = p
			print p,  moving_avg_data[i], thrshold[i]
			p=p+freq_resolution
			thrshold_inorder[i+size/2]= thrshold[i]
			avg_data[i+(size/2)] = moving_avg_data[i]		
		hexa_thr = hex_conv(thrshold_inorder)
		
		print hexa_thr
	
		required_index = int(math.ceil((Frequency.value - 8925*10**5)*size/(usr)))
		carrier_map = thrshold_inorder[required_index-16:required_index+16]		
		print "\n\nCarrier map = ", carrier_map
		
		test = 0
		for i in range(0,len(carrier_map)):
		    if carrier_map[i]==0:
			test+=1
		print test
		if test >= 9:
		    sys.stderr.write('\nPrimary Transmission detected')
		    #---------------------------
		    # Finding best 200KHz spectrum band
		    #---------------------------
		    n = 0
		    power_temp = 50
		    for i in range(200,size-217):
			power = 0
			for j in range(0,17):
			    power = power + avg_data[i+j]
			#print sensed_freq[i+16],'\t', power
			if power < power_temp:
			    power_temp = power
			    index = i+8
		    Frequency.value = int(1e5*math.ceil(sensed_freq[index]/1e5))
		    print 'Frequency',Frequency.value
		    norestart.value=0
		    sync.value = 1
		    time.sleep(2)
		moving_avg_data = [0]*(size)
		avg_iter_count = avg_iterations
    tb.stop()
    tb.wait()
    return hexa_thr

# This function converts the vector of 1s and 0s into hexadecimal string for transmission  
def hex_conv(thrshold_inorder):
	dec_thr=0
	i=0
	hexa_thr=''
	abc = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
	length=len(thrshold_inorder)
	while ((i<length) & ((length-i)>=4)):
	    j=4
	    while(j>0):
		if thrshold_inorder[i]==1:
		  dec_thr+= (2)**(4-j)
		  #print "dec_thr=",dec_thr
		i=i+1
		j=j-1
	    mul=dec_thr
	    #print "mul=",mul
	    dec_thr=0
	    hexa_thr_part = ''
	    while mul >15:
		c = abc[mul%16]
		hexa_thr_part = c+hexa_thr_part
		mul = mul/16  
	    hexa_thr_part= abc[mul]+hexa_thr_part 
	    hexa_thr=hexa_thr+hexa_thr_part	   
	# print "hexa_thr=",hexa_thr
	return hexa_thr
	    
###################################################################################################################################################################        
	                                                 # Transmitter code
###################################################################################################################################################################        

def send_pkt(tb,payload='',carrier_map="FE7F",eof=False):
	#print "carrier_map_in_send_pkt=",carrier_map
	return tb.txpath.send_pkt(payload, eof,carrier_map) 

def run_transmiter(n,nbytes,tb,norestart,pkt_size,position):    
	if (norestart.value==1):
	      time.sleep(1)
	      tb.start()                       # start flow graph
	      n= 0
	      pktno = 0
	      print "\nTransmitting in", Freq.value ,"Hz"
	      source_file = open("/home/kranthi/documents/sound_cognition/test.raw",'r') # Source file location	# Added Line
	      source_file.seek(position.value,0)
	      file_size = os.path.getsize("/home/kranthi/documents/sound_cognition/test.raw")
	      print file_size
	      no_packets = int(math.ceil(file_size/pkt_size))
	      print no_packets
	      preamble = 11111
	      #temp = 100*pkt_size
	      while n < 120:
		    if (pktno < 20):
			data = "This is Garbage data"
		    elif (pktno == 20 ):
			data = struct.pack('!H', no_packets & 0xffff)
			#print data
		    else:
			data = source_file.read(pkt_size - 4)# data from the file		# Original Line
			position.value = source_file.tell()
			if data == '':
			    position.value = 0
			    for i in range(0,20):
				data = "This is also Garbage data"
				payload = struct.pack('!H', pktno & 0xffff) + struct.pack('!H', preamble & 0xffff) + data # Constructing a packet. Pack a string in to given format. http://docs.python.org/library/struct.html
				send_pkt(tb,payload)
				sys.stderr.write('.')
				pktno += 1
			    break;
		    #print data
		    payload = struct.pack('!H', pktno & 0xffff) + struct.pack('!H', preamble & 0xffff) + data # Constructing a packet. Pack a string in to given format. http://docs.python.org/library/struct.html
		    send_pkt(tb,payload)				     # Sending packet
		    #n += len(payload)
		    n += 1
		    sys.stderr.write('.')				     # error message
		    pktno += 1
	      print position.value
	      tb.stop()
	      tb.wait()
	      return position
 
def Start_transmitter(Freq,norestart,sync,Frequency,position):             
	  trans = trans_init(Freq)
	  tb = trans.return_obj()
	  
	  if Freq.value == 920*10**6:
		n = synchronization(tb)
	  else:
		Data_in_MB = trans.Data()
		options = trans.return_options()
		tb1 = sensor_init(options)
		pkt_size = int(options.size)
		nbytes = int(1e6 * Data_in_MB)
		n=0
		while 1:
			carrier_map_new = sense_loop(tb1,Frequency)
			position = run_transmiter(n,nbytes,tb,norestart,pkt_size,position)
		send_pkt(tb,"", carrier_map_new, eof = True)                     
                
if __name__ == '__main__':
	try:
	    Frequency = Value('i',905*10**6)
	    sync = Value('i',1)
	    norestart = Value('i',1)
	    Freq = Value('i',905*10**6)
	    position = Value('i',0)
	    mp = Process(target = Start_transmitter,args = (Freq,norestart,sync,Frequency,position))
	    mp.start()
	    p = Process(target = transmitter_control,args = (mp,Freq,norestart,sync,Frequency,position))
	    p.start()	        
	except KeyboardInterrupt:
		pass
