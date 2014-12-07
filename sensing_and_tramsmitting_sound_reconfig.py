#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gnuradio import gr, blks2
from gnuradio import uhd,window,audio
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import string
import os
import time, struct,sys
import ofdm
import usrp_transmit_path
sys.path.append('/usr/local/lib/python2.6/dist-packages/gnuradio')
import digital
from alsaaudio import *
from multiprocessing import Process ,Value

def transmitter_control(mp,Freq,norestart):
             while(1):
                while(norestart.value==1):
                       time.sleep(2)
                norestart.value=1       
                mp.terminate()
                f_set=Freq.value
	        if(f_set==920*10**6):
	            Freq.value=900*10**6
	        else:
	            Freq.value=920*10**6
	        sys.stderr.write('changing frequency')    
	        print "frequency changed to ",Freq.value    
	        mp=Process(target=Start_transmitter,args=(Freq,norestart))
                mp.start()
	        
def Start_transmitter(Freq,norestart):
                trans=trans_init(Freq)
		Data_in_MB=trans.Data()
		options=trans.return_options()
		occupied_tones=options.occupied_tones
		print "occupied_tones=",occupied_tones
		tb1=sensor_init(options,Freq)
		print "returned from sensor_init"
		pkt_size=int(options.size)
		global sound_rcv
		sound_rcv=sound_data()
                print "created sound object"
                offset=sound_data_offset()
		tb=trans.return_obj()
		global npilot
		npilot=19
		nbytes = int(1e6 * Data_in_MB)
		count=200 #number of packets to send before sensing
		count1=55 #number of times the sensor loop will run
		carrier_map_new="FFFFFE7FFFFFF" #initial carrier map 
		n=0
		pktno=0
		a=()
		while(n < nbytes):
                       a=run_transmiter(n,nbytes,count,carrier_map_new,tb,sound_rcv,offset,pktno,pkt_size,norestart)
                       n=a[0]
                       pktno=a[1]
                       #print "count after returning form trans call=",count
                       #run the sensing code now and return the new carier map
                       carrier_map_new=sense_loop(tb1,count1)
                       #print "carrier_map_new_before_clipping",carrier_map_new
                       carrier_map_new=carrier_map_new[0:50]
                       #carrier_map_new=carrier_map_new[0:24]+'0'+carrier_map_new[25:]
                       #print "carrier_map_new",carrier_map_new
                


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
                  
class sound_data(gr.top_block):
         def __init__(self):
	    gr.top_block.__init__(self)
            self.sample_rate=8000
	    self.sound_sink=PCM(type=PCM_CAPTURE,mode=PCM_NORMAL,card='default')
	    self.sound_sink.setrate(self.sample_rate)
	    self.sound_sink.setperiodsize(32)
	    self.sound_sink.setformat(PCM_FORMAT_FLOAT_LE)
	    self.sound_sink.setchannels(1)        		






#class sound_data(gr.top_block):
  #def __init__(self,pkt_size):
         #gr.top_block.__init__(self)   
         #sample_rate=48000
         #vlen=512
         #print "in sound init" 
         #print "vlen=",vlen
         #self.sound_src=audio.source (sample_rate,"hw:0,0")
         ##self.conv=gr.float_to_uchar()
         ##self.msgq = gr.msg_queue(100)
         #self.stream_to_vec=gr.stream_to_vector(gr.sizeof_float,vlen)
         #self.vec_sink=gr.vector_sink_f(vlen)
         ##self.msg_sink=gr.message_sink(gr.sizeof_float,self.msgq,1)
         #self.connect(self.sound_src,self.stream_to_vec,self.vec_sink)
 


        
class trans_init():
    def __init__(self,Freq): 
        global parser
        parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
        parser.add_option("-a", "--args", type="string", default="", help="UHD device address [default=%default]")
	expert_grp = parser.add_option_group("Expert")
	parser.add_option("-s", "--size", type="eng_float", default=400, help="set packet size [default=%default]")
	parser.add_option("-M", "--megabytes", type="eng_float", default=1.0, help="set megabytes to transmit [default=%default]")
	parser.add_option("","--discontinuous", action="store_true", default=False, help="enable discontinuous mode")
	parser.add_option("","--from-file", default=None, help="use file for packet contents")
        parser.add_option("-e", "--interface", type="string", default="eth0", help="Select ethernet interface. Default is eth0")
	parser.add_option("-m", "--MAC_addr", type="string", default="", help="Select USRP2 by its MAC address.Default is auto-select")
	parser.add_option("-j", "--start", type="eng_float", default=1e7, help="Start ferquency [default = %default]")
	parser.add_option("-k", "--stop", type="eng_float", default=1e8,help="Stop ferquency [default = %default]")
	parser.add_option("", "--tune-delay", type="eng_float", default=1e-3, metavar="SECS", help="time to delay (in seconds) after changing frequency[default=%default]")
	parser.add_option("", "--dwell-delay", type="eng_float",default=1e-3, metavar="SECS", help="time to dwell (in seconds) at a given frequncy[default=%default]")
	parser.add_option("-G", "--gain", type="eng_float", default=None,help="set gain in dB (default is midpoint)")
	parser.add_option("-s", "--fft-size", type="int", default=512, help="specify number of FFT bins [default=%default]")
	parser.add_option("-d", "--decim", type="intx", default=16, help="set decimation to DECIM [default=%default]")
        parser.add_option("-i", "--input_file", default="", help="radio input file",metavar="FILE")
        parser.add_option("-S", "--sense-bins", type="int", default=128, help="set number of bins in the OFDM block [default=%default]")
	
	usrp_transmit_path.add_options(parser, expert_grp)
	ofdm.ofdm_mod.add_options(parser, expert_grp)

	(self.options, self.args) = parser.parse_args ()
	#fd= os.open('/home/spann/Dropbox/spec_sense/fifo',os.O_RDONLY) # Open the named pipe to pass on the sensed info to the transmitter part

	if len(self.args) != 0:
		parser.print_help()
		sys.exit(1)

	#if self.options.tx_freq is None:
		#sys.stderr.write("You must specify -f FREQ or --freq FREQ\n")
		##parser.print_help(sys.stderr)
		#sys.exit(1)
	self.options.tx_freq=Freq.value ###value to set when restarted hard coded ie not a command line option any more		
        print "trying to open the source file",self.options.input_file
	#if self.options.input_file is not "":
		#print "reading from file:",self.options.input_file 
		#global source_file
		#source_file = open(self.options.input_file, 'r')


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
        
###################################################################################################################################################################

                                                              #SENSING CODE 
                                                             
                                                             
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
    def __init__(self,options,Freq):
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

	
	#self.min_freq = options.start
	#self.max_freq = options.stop
        #print "min_freq=",self.min_freq
        #print "max_freq=",self.max_freq
        self.min_freq = Freq.value-(3*10**6) #hard coded not a command line option any more
	self.max_freq = Freq.value+(3*10**6)
        
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
        print "bandwidth=",BW 
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
	self.msgq = gr.msg_queue(16)
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
	

def sensor_init(options,Freq):
    tb1=sensor(options,Freq)
    return tb1
    
    
def sense_loop(tb,count):
    #fd= os.open('/home/spann/fifo',os.O_WRONLY) # Open the named pipe to pass on the sensed info to the transmitter part
    #print "in sense_loop"
    tb.start()
    global hexa_thr
    n = 1
    new_data = [0]*(size/n) # This is decimated value of m.data avg of n terms at a time
    moving_avg_data = [0]*(size)
    avg_iterations = avg_iter_count = 10
   
    #show()
    while count>0:
	count=count-1
	m = parse_msg(tb.msgq.delete_head())
	
	#for i in range(0,len(new_data)):
		#new_data[i] = sum(m.data[i*n:n*(i+1)])/float(n)
	#print "count in sense_loop=",count
	if avg_iter_count > 0:
		#print avg_iter_count
		for i in range(0,size):
		      moving_avg_data[i] = moving_avg_data[i] + m.data[i]
		avg_iter_count = avg_iter_count - 1
		
	else: 
	        #print "in else blok of sense" 
		for i in range(0,len(moving_avg_data)):
			moving_avg_data[i] = moving_avg_data[i]/float(avg_iterations)
		
		new_data= decimate_data(m.data,n)
		thrshold = map(lambda x: 0 if x>0.00010 else 1, moving_avg_data)
		
		
		size2 = size/n
		thrshold_inorder= [0]*size2
		sensed_freq = [0]*size2
		ofdm_center_freq = m.center_freq # For now we are keeping the center freq of the ofdm same as that of sensing, will have to modify this later
		
		freq_resolution = usr/size2
		p2=m.center_freq-usr/2
		p = m.center_freq - freq_resolution*((size2/2)-1)
		##print p2
		#print usr
		
		for i in range(0,size2/2):
			sensed_freq[i]= p	
			#print p,m.center_freq,moving_avg_data[i+size2/2],thrshold[i+size2/2]
			p=p+usr/(size2-1)
			p=p+freq_resolution
			thrshold_inorder[i] = thrshold[i+size2/2]
		
		for i in range(0,size2/2):
			sensed_freq[i+size2/2] = p
			#print p,m.center_freq,moving_avg_data[i],thrshold[i]
			p=p+usr/(size2-1)
			p=p+freq_resolution
			thrshold_inorder[i+size2/2]= thrshold[i]
		#print 'End of one iteration'
		#print new_data
		#print m.data
		#print thrshold_inorder
		#Convert the vector into a string of Hexadecimal number
	
		hexa_thr = hex_conv(thrshold_inorder)
		
		
		avg_iter_count = avg_iterations
		moving_avg_data = [0]*(size)
		#print hexa_thr
		#os.write(fd,hexa_thr)
        
        #cla()
        #plot(thrshold_inorder)
    tb.stop()
    #print "sense graph stop executed" 
    tb.wait()
    #print "returning from sense_loop"
    return hexa_thr
        
def decimate_data(data,n):
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
	    #print "thrshold_inorder",thrshold_inorder
	   #print i
	#print dec_thr  
        #if dec_thr==0:
                #hexa_thr='0'*13
                #return hexa_thr
	
		  #print c  
	#print "hexa_thr=",hexa_thr
	return hexa_thr
	    
    

	                                                 #End oF Snesing code
###################################################################################################################################################################        
def send_pkt(tb,payload='',carrier_map="FE7F",eof=False):
	#print "carrier_map_in_send_pkt=",carrier_map
	return tb.txpath.send_pkt(payload, eof,carrier_map) 


class sound_data_offset:
  def __init__(self):
        self.offset=0
        self.length=0
        self.step=2040
  def set_offset(self,offset):
       self.offset=offset
         
  def set_step(self,offset):
       if((self.length-offset)>self.step):
           return self.step
       else:
           return (self.step-offset)
       
  def ret_offset(self):
       return self.offset
        
  
      


      
def run_transmiter(n,nbytes,count,carrier_map,tb,src_sound,offset,pktno,pkt_size,norestart):
         
	tb.start() 
	global sound_rcv
	# start flow graph
	#nbytes = int(1e6 * options.megabytes)
	#n = 0
	global npilot
	tx_success=0
        loop_pktno=0
	#pkt_size = int(options.size)
        start_time = 0
	last_time = 0
	#carrier_map="FFFFFE7FFFFFF"
	#new_freq = options.tx_freq
	count_init=0
	#ofset=offset.ret_offset()
	#print "carrier_map_passed_by_main=",carrier_map
	#sound=open('sound','w')
        while n < nbytes:
	       #print "inside while"
	       if string.count(carrier_map,'0') >= 45:
		    sys.stderr.write('Waiting no bandwidth available\n')
		    norestart.value=0
		    #return n,pktno
               #if (npilot):
	       if pktno < 19:
		      data = (pkt_size - 20) * chr(pktno & 0xff)
		      #npilot=npilot-1
		      #time.sleep(2)
	       else:
		    
		     data_length=1
		     data=""
		     while(data_length):
			sdata=""
			sdata=sound_rcv.sound_sink.read()
			#print "print length of data=",len(sdata[1])
			data=data+sdata[1]   
			data_length=data_length-1 
		     print "length of complete data",len(data)		
		  
	       if data == '':
		        print "no data breaking from main loop"
			break;
	       if (count==0):
		     print "count=0 breaking from main loop"
		     break;
				
	       count=count-1
	       #data=data[0:4080]
	       #print "length of data=",len(data)
	       #count_init=count_init + 1
	       payload = struct.pack('!H', pktno) +data
	       #print "length of payload=",len(payload)
	       send_pkt(tb,payload,'FE7F')
	       n += len(payload)
	       #print "n=",n
	       print "count=",count
	       sys.stderr.write('.')
	       #if options.discontinuous and pktno % 10 == 1:
		      #time.sleep(1)
	       pktno += 1
               loop_pktno+=1
               #print "packet_number",pktno 
	       #if(ofset==offset.length):
		#offset.length=0
	    
		      #send_pkt(eof=True)
        tb.stop()
        print "waiting for the transmitter to stop"
        tb.wait()
        print "stopped transmitter"
        #print "count before returning from trans call=",count
        return n,pktno
        
 
        
	
if __name__ == '__main__':
	try:
	  norestart=Value('i',1)
	  Freq=Value('i',900*10**6)
	  mp=Process(target=Start_transmitter,args=(Freq,norestart))
          mp.start()
          p=Process(target=transmitter_control,args=(mp,Freq,norestart))
          p.start()
		#send_pkt(tb,"",carrier_map_new,eof=True)       
                       
	except KeyboardInterrupt:
		pass
