#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Importing necessary modules from GNU Library, Python and current directory. 
from gnuradio import uhd
from gnuradio import gr, blks2
from gnuradio import window ,digital
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
# Python modules
import string
import os
import time, struct, sys
# Modules from the current directory
import ofdm
import usrp_transmit_path
#sys.path.append('/home/kranthi/gnuradio-3.6.0/gr-digital/examples')		# Added Line
sys.path.append('/usr/local/lib/python2.7/dist-packages/gnuradio/digital')
import _digital_swig

class transmit(gr.top_block):				
      def __init__(self, options):
	  gr.top_block.__init__(self)
	  self.txpath = usrp_transmit_path.usrp_transmit_path(options)       # Define the transmitter_path -- Initializes and connects blocks and pass the options to transmit_path
	  self.connect(self.txpath)		# Adding txpath block to flowgraph

      def _print_verbage(self):		# verbage options 
	  print "Using TX d'board %s"    % (self.subdev.side_and_name(),)
	  print "modulation:      %s"    % (self._modulator_class.__name__)
	  print "interp:          %3d"   % (self._interp)
	  print "Tx Frequency:    %s"    % (eng_notation.num_to_str(self._tx_freq))

      def string_pass(): 
	  fd=open('string_pipe','r')
	  string=fd.read()
	  usrp_transmit_path.string_pass_l2(string) 
                  
#def parse_sen_trn():
        #parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
	#expert_grp = parser.add_option_group("Expert")
	#parser.add_option("-s", "--size", type="eng_float", default=400, help="set packet size [default=%default]")
	#parser.add_option("-M", "--megabytes", type="eng_float", default=1.0, help="set megabytes to transmit [default=%default]")
	#parser.add_option("","--discontinuous", action="store_true", default=False, help="enable discontinuous mode")
	#parser.add_option("","--from-file", default=None, help="use file for packet contents")
	#parser.add_option("-e", "--interface", type="string", default="eth0", help="Select ethernet interface. Default is eth0")
	#parser.add_option("-m", "--MAC_addr", type="string", default="", help="Select USRP2 by its MAC address.Default is auto-select")
	#parser.add_option("-a", "--start", type="eng_float", default=1e7, help="Start ferquency [default = %default]")
	#parser.add_option("-b", "--stop", type="eng_float", default=1e8,help="Stop ferquency [default = %default]")
	#parser.add_option("", "--tune-delay", type="eng_float", default=1e-3, metavar="SECS", help="time to delay (in seconds) after changing frequency[default=%default]")
	#parser.add_option("", "--dwell-delay", type="eng_float",default=10e-3, metavar="SECS", help="time to dwell (in seconds) at a given frequncy[default=%default]")
	#parser.add_option("-g", "--gain", type="eng_float", default=None,help="set gain in dB (default is midpoint)")
	#parser.add_option("-s", "--fft-size", type="int", default=256, help="specify number of FFT bins [default=%default]")
	#parser.add_option("-d", "--decim", type="intx", default=16, help="set decimation to DECIM [default=%default]")
        #parser.add_option("-i", "--input_file", default="", help="radio input file",metavar="FILE")
        #parser.add_option("-S", "--sense-bins", type="int", default=64, help="set number of bins in the OFDM block [default=%default]")
        
        #usrp_transmit_path.add_options(parser, expert_grp)
	#blks2.ofdm_mod.add_options(parser, expert_grp)
	
	#print "in parser functon"
	
	#(options, args) = parser.parse_args ()
	
	#if len(args) != 0:
		#parser.print_help()
		#sys.exit(1)
        #return options
        
class trans_init():
    def __init__(self):
	# Creating the optionparser
        global parser
        parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
	expert_grp = parser.add_option_group("Expert")
	
	parser.add_option("-a", "--args", type="string", default="", help="UHD device address [default=%default]")
	parser.add_option("-s", "--size", type="eng_float", default=400, help="set packet size [default=%default]")
	parser.add_option("-M", "--megabytes", type="eng_float", default=1.0, help="set megabytes to transmit [default=%default]")
	parser.add_option("","--discontinuous", action="store_true", default=False, help="enable discontinuous mode")
	parser.add_option("","--from-file", default=None, help="use file for packet contents")
        parser.add_option("-e", "--interface", type="string", default="eth0", help="Select ethernet interface. Default is eth0")
	parser.add_option("-m", "--MAC_addr", type="string", default="", help="Select USRP2 by its MAC address.Default is auto-select")
	parser.add_option("-j", "--start", type="eng_float", default=1e7, help="Start ferquency [default = %default]")
	parser.add_option("-k", "--stop", type="eng_float", default=1e8,help="Stop ferquency [default = %default]")
	parser.add_option("", "--tune-delay", type="eng_float", default=1e-3, metavar="SECS", help="time to delay (in seconds) after changing frequency[default=%default]")
	parser.add_option("", "--dwell-delay", type="eng_float",default=20e-3, metavar="SECS", help="time to dwell (in seconds) at a given frequncy[default=%default]")
	parser.add_option("-G", "--gain", type="eng_float", default=None,help="set gain in dB (default is midpoint)")
	parser.add_option("-s", "--fft-size", type="int", default=256, help="specify number of FFT bins [default=%default]")
	parser.add_option("-d", "--decim", type="intx", default=16, help="set decimation to DECIM [default=%default]")
        parser.add_option("-i", "--input_file", default="", help="radio input file",metavar="FILE")
        parser.add_option("-S", "--sense-bins", type="int", default=128, help="set number of bins in the OFDM block [default=%default]")
	
	usrp_transmit_path.add_options(parser, expert_grp)
	ofdm.ofdm_demod.add_options(parser, expert_grp)

	(self.options, self.args) = parser.parse_args ()
	#fd= os.open('/home/spann/Dropbox/spec_sense/fifo',os.O_RDONLY) # Open the named pipe to pass on the sensed info to the transmitter part

	if len(self.args) != 0:			# if no arguments are given display help options
		parser.print_help()
		sys.exit(1)

	if self.options.tx_freq is None:	# if transmitter frequency is not mentioned
		sys.stderr.write("You must specify -f FREQ or --freq FREQ\n")
		#parser.print_help(sys.stderr)
		sys.exit(1)

	if self.options.from_file is not None:	# if source file is mentioned
		source_file = open(options.from_file, 'r')

	self.tb = transmit(self.options)	# Constructing the flowgraph with the given options

	r = gr.enable_realtime_scheduling() 	# Enable the real time scheduling for flowgraph to be able to run.
	if r != gr.RT_OK:			# Checking error in the status of real time scheduling enabling.
	    print "Warning: failed to enable realtime scheduling"
    
    def Data(self):    
            return self.options.megabytes     
    def return_obj(self):
           return self.tb     
    def return_options(self):
           return self.options
        
######################################################################################################################
						   #SENSING CODE 
######################################################################################################################                                                             
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
class parse_msg(object):					# Original Line
    def __init__(self, msg):
	self.center_freq = msg.arg1()
	self.vlen = int(msg.arg2())
	print "\nHello\n"					# Added Line
	assert(msg.length() == self.vlen * gr.sizeof_float)
	t = msg.to_string()
	self.raw_data = t
	self.data = struct.unpack('%df' % (self.vlen,), t)

class parse_msg2():						# Added class
    def __init__(self):
      self.center_freq = 910000000
      self.vlen = 64
      t = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
      self.data = struct.unpack('%df' % (self.vlen,),t)

class sensor(gr.top_block):
    def __init__(self,options):
	gr.top_block.__init__(self)
	#global parser
	#parser = OptionParser(option_class=eng_option)
	#parser.add_option("-e", "--interface", type="string", default="eth0", help="Select ethernet interface. Default is eth0")
	#parser.add_option("-m", "--MAC_addr", type="string", default="", help="Select USRP2 by its MAC address.Default is auto-select")
	#parser.add_option("-a", "--start", type="eng_float", default=1e7, help="Start ferquency [default = %default]")
	#parser.add_option("-b", "--stop", type="eng_float", default=1e8,help="Stop ferquency [default = %default]")
	#parser.add_option("", "--tune-delay", type="eng_float", default=1e-3, metavar="SECS", help="time to delay (in seconds) after changing frequency[default=%default]")
	#parser.add_option("", "--dwell-delay", type="eng_float",default=10e-3, metavar="SECS", help="time to dwell (in seconds) at a given frequncy[default=%default]")
	#parser.add_option("-g", "--gain", type="eng_float", default=None,help="set gain in dB (default is midpoint)")
	#parser.add_option("-s", "--fft-size", type="int", default=256, help="specify number of FFT bins [default=%default]")
	#parser.add_option("-d", "--decim", type="intx", default=16, help="set decimation to DECIM [default=%default]")
        #parser.add_option("-i", "--input_file", default="", help="radio input file",metavar="FILE")
        #parser.add_option("-S", "--sense-bins", type="int", default=64, help="set number of bins in the OFDM block [default=%default]")
	#(options, args) = parser.parse_args()
	if options.input_file == "":
	    self.IS_USRP2 = True
	else:
	    self.IS_USRP2 = False

	
	self.min_freq = options.start
	self.max_freq = options.stop
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
#log = gr.nlog10_ff(10, self.fft_size, -20*math.log10(self.fft_size)-10*math.log10(power/self.fft_size))

# modifications for USRP2
        print "*******************in sensor init********************"   
	if self.IS_USRP2:
	
	    self.u=uhd.usrp_source(device_addr=options.args,io_type=uhd.io_type.COMPLEX_FLOAT32,
                             num_channels=1)

	    samp_rate = 100**6/options.decim
	    self.u.set_samp_rate(samp_rate)
	else:
	    self.u = gr.file_source(gr.sizeof_gr_complex,options.input_file, True)
	    samp_rate = 100e6 / options.decim

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
	nsteps = 10 #math.ceil((self.max_freq - self.min_freq) / self.freq_step)
	self.max_center_freq = self.min_center_freq + (nsteps * self.freq_step)
	self.next_freq = self.min_center_freq
	tune_delay = max(0, int(round(options.tune_delay * samp_rate / self.fft_size))) # in fft_frames
	print tune_delay
	dwell_delay = max(1, int(round(options.dwell_delay * samp_rate / self.fft_size))) # in fft_frames
	print dwell_delay
	self.msgq = gr.msg_queue(16)				# thread-safe message queue
	self._tune_callback = tune(self)
	# hang on to this to keep it from being GC'd
	stats = gr.bin_statistics_f(self.fft_size, self.msgq, self._tune_callback, tune_delay,
				      dwell_delay)
	self.connect(self.u, s2v, fft,c2mag,stats)
	if options.gain is None:
# if no gain was specified, use the mid-point in dB
	    g = self.u.get_gain_range()
	    options.gain = float(g.start()+g.stop())/2
    def set_next_freq(self):
	target_freq = self.next_freq
	self.next_freq = self.next_freq + self.freq_step
	if self.next_freq >= self.max_center_freq:
	    self.next_freq = self.min_center_freq
	if self.IS_USRP2:
	    if not self.set_freq(target_freq):
	        print "Failed to set frequency to ", target_freq, "Hz"
		#print ""
	return target_freq
    def set_freq(self, target_freq):
	return self.u.set_center_freq(target_freq,0)
    def set_gain(self, gain):
	self.u.set_gain(gain,0)
	

def sensor_init(options):
    tb1=sensor(options)
    return tb1
    
def sense_loop(tb,count):
    #fd= os.open('/home/spann/fifo',os.O_WRONLY) # Open the named pipe to pass on the sensed info to the transmitter part
    print "in sense_loop"
    tb.start()
    global hexa_thr 
    n = 1
    new_data = [0]*(size/n) # This is decimated value of m.data avg of n terms at a time
    moving_avg_data = [0]*(size)
    avg_iterations = avg_iter_count = 10
   
    #show()
    while count>0:
	count=count-1
        hexa_thr="" 
#	m = parse_msg(tb.msgq.delete_head())		# msg_queue.delete_head() - Delete message from head of queue and return it. Block if no message is available.
	#for i in range(0,len(new_data)):
		#new_data[i] = sum(m.data[i*n:n*(i+1)])/float(n)
	m = parse_msg2()				# Added Line
	if avg_iter_count > 0:
		print avg_iter_count
#		for i in range(0,size):
		for i in range(0,64):
		      moving_avg_data[i] = moving_avg_data[i] + m.data[i]
		avg_iter_count = avg_iter_count - 1
	else: 
	
		for i in range(0,len(moving_avg_data)):
			moving_avg_data[i] = moving_avg_data[i]/float(avg_iterations)
		
		#new_data= decimate_data(m.data,n)
		thrshold = map(lambda x: 0 if x>0.00010 else 1, moving_avg_data)
		
		
		size2 = size/n
		thrshold_inorder= [0]*size2
		sensed_freq = [0]*size2
		ofdm_center_freq = m.center_freq # For now we are keeping the center freq of the ofdm same as that of sensing, will have to modify this later
		
		freq_resolution = usr/size2
		p2=m.center_freq-usr/2
		p = m.center_freq - freq_resolution*((size2/2)-1)
		print p2
		print usr
		
		for i in range(0,size2/2):
			sensed_freq[i]= p	
			print p,m.center_freq,moving_avg_data[i+size2/2],thrshold[i+size2/2]
			#p=p+usr/(size2-1)
			p=p+freq_resolution
			thrshold_inorder[i] = thrshold[i+size2/2]
		
		for i in range(0,size2/2):
			sensed_freq[i+size2/2] = p
			print p,m.center_freq,moving_avg_data[i],thrshold[i]
			#p=p+usr/(size2-1)
			p=p+freq_resolution
			thrshold_inorder[i+size2/2]= thrshold[i]
		#print 'End of one iteration'
		#print new_data
		#print m.data
		#print thrshold_inorder
		#Convert the vector into a string of Hexadecimal number
		hexa_thr = hex_conv(thrshold_inorder)
		
		#print hexa_thr
		avg_iter_count = avg_iterations
		moving_avg_data = [0]*(size)
		#os.write(fd,hexa_thr)
        
        #cla()
        #plot(thrshold_inorder)
    tb.stop()
    tb.wait()
    return hexa_thr
        
def decimate_data(data,n)        :
	vec_mod = [0]*(len(data)/n)
	for i in range(0,len(vec_mod)):
	  vec_mod[i] = sum(data[i*n:n*(i+1)])/float(n)	  
	#print vec_mod 
  
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
	      print "dec_thr=",dec_thr
	     i=i+1
	     j=j-1
	    mul=dec_thr
	    print "mul=",mul
	    dec_thr=0
	    hexa_thr_part = ''
	    while mul >15:
	     c = abc[mul%16]
	     hexa_thr_part = c+hexa_thr_part
	     mul = mul/16  
	    hexa_thr_part= abc[mul]+hexa_thr_part 
	    hexa_thr=hexa_thr+hexa_thr_part
	    #print "thrshold_inorder",thrshold_inorder
	   #print i
	#print dec_thr  
        #if dec_thr==0:
                #hexa_thr='0'*13
                #return hexa_thr
	
		  #print c  
	print "hexa_thr=",hexa_thr
	return hexa_thr
	    
    
###################################################################################################################################################################
	                                                 # End oF Snesing code
###################################################################################################################################################################        
def send_pkt(tb,payload='',carrier_map="FE7F",eof=False):
	#print "carrier_map_in_send_pkt=",carrier_map
	return tb.txpath.send_pkt(payload, eof,carrier_map) 



def run_transmiter(n,nbytes,count,carrier_map,tb):
    
	tb.start()                       # start flow graph
	#nbytes = int(1e6 * options.megabytes)
	#n = 0
	tx_success=0
	pktno = 0
	pkt_size = int(options.size)
        start_time = 0
	last_time = 0
	#carrier_map="FFFFFE7FFFFFF"
	new_freq = options.tx_freq
	count_init=0
	print "carrier_map_passed_by_main=",carrier_map
#	string_pipe=open('string_pipe','r')
        while n < nbytes:
	        #if count_init >2000:
	##	carrier_map_new=string_pipe.readline()
         ##       carrier_map_new=carrier_map[0:(len(carrier_map)-1)] 
		    #if (pktno%40000)==0:
			##carrier_map = os.read(fd,options.occupied_tones/4) #The sensor is a part of this code so no need to read from pipe 
			#if string.count(carrier_map,'0') >= 180:
			    #carrier_map="000000000000"
			    #tx_success=tb.txpath.sink.set_center_freq(new_freq+1e6)
			    #if tx_success:
			      #new_frew=new_freq+1e6
			      #print "successfully"
			    #print "Freq changed to "
			    #print new_freq
		if string.count(carrier_map,'0') >= 190:
		    print "Waiting no bandwidth available"
		    return n
                if options.from_file is None:
			data = (pkt_size - 2) * chr(pktno & 0xff) 
		else:
			if pktno < 20:
			    data = (pkt_size - 2) * chr(pktno & 0xff)
			else:
			    data = source_file.read(pkt_size - 2)
			    if data == '':
				    break;
                if (count==0):
                         break;
		count=count-1
		count_init=count_init + 1
		payload = struct.pack('!H', pktno & 0xffff) + data
		send_pkt(tb,payload,carrier_map)
		n += len(payload)
		sys.stderr.write('.')
		if options.discontinuous and pktno % 10 == 1:
			time.sleep(1)
		pktno += 1
	#send_pkt(eof=True)
        tb.stop()
        tb.wait()
        print "n before retunning from trans loop=",n
        print "nbytes after retunning from trans loop=",nbytes
        return n

##########################################################################################################################################
					# Main Function #
##########################################################################################################################################             
if __name__ == '__main__':
	try:
	    #options=parse_sen_trn()
	    trans=trans_init()
	    Data_in_MB=trans.Data()
	    options=trans.return_options()
	    occupied_tones=options.occupied_tones
	    print "occupied_tones=",occupied_tones
	    tb1=sensor_init(options)
	    tb=trans.return_obj()
	    nbytes = int(1e6 * Data_in_MB)
	    count=500 #number of packets to send before sensing
	    count1=10 #number of times the sensor loop will run
	    carrier_map_new="FFFFFE7FFFFFF" #initial carrier map 
	    n=0
	    while(n < nbytes):
		    print "nbytes=",nbytes
		    n=run_transmiter(n,nbytes,count,carrier_map_new,tb)
		    #run the sensing code now and return the new carier map
		    print "n after returning from the trans call=",n
		    carrier_map_new=sense_loop(tb1,count1)
		    print "carrier_map_new_before_clipping",carrier_map_new
		    carrier_map_new=carrier_map_new[0:50]
		    print "carrier_map_new",carrier_map_new
	    #send_pkt(tb,"",carrier_map_new,eof=True)
	except KeyboardInterrupt:
		pass