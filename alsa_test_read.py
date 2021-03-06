#!/usr/bin/env python
from alsaaudio import *
from gnuradio import gr, blks2
from gnuradio import usrp
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import struct

class sound_rcv(gr.top_block):
         def __init__(self):
	    gr.top_block.__init__(self)
            self.sample_rate=8000
	    self.sound_sink=PCM(type=PCM_CAPTURE,mode=PCM_NORMAL,card='default')
	    self.sound_sink.setrate(self.sample_rate)
	    self.sound_sink.setperiodsize(32)
	    self.sound_sink.setformat(PCM_FORMAT_FLOAT_LE)
	    self.sound_sink.setchannels(1)


def main():
  sound_obj=sound_rcv()
  f=open("/usr/local/share/gnuradio/examples/audio/sound",'w')
  count=9000000
  while(1):
    data=""
    data=sound_obj.sound_sink.read()
    print "print length of data=",len(data[1])
    sdata=""
    sdata=sdata+data[1]   
    f.write(sdata)
    count=count-1 

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		packet_file.close()
		pass