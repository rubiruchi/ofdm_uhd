#
# Copyright 2009 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr
#import usrp_options
import receive_path
from gnuradio import eng_notation
from uhd_interface import uhd_receiver

def add_freq_option(parser):
	def freq_callback(option, opt_str, value, parser):
		parser.values.rx_freq = value
		parser.values.tx_freq = value

	if not parser.has_option('--freq'):
		parser.add_option('-f', '--freq', type="eng_float",
					action="callback", callback=freq_callback,
					help="set Tx and/or Rx frequency to FREQ [default=%default]",
					metavar="FREQ")

def add_options(parser, expert):
	add_freq_option(parser)
	uhd_receiver.add_options(parser)
	receive_path.receive_path.add_options(parser, expert)
	expert.add_option("", "--rx-freq", type="eng_float", default=None,
					help="set Rx frequency to FREQ [default=%default]", metavar="FREQ")
	parser.add_option("-v", "--verbose", action="store_true", default=False)


class usrp_receive_path(gr.hier_block2):
	def __init__(self, rx_callback, options):
		gr.hier_block2.__init__(self, "usrp_receive_path",
			gr.io_signature(0, 0, 0),                    # Input signature
			gr.io_signature(0, 0, 0)) # Output signature
		if options.rx_freq is None:
			sys.stderr.write("-f FREQ or --freq FREQ or --rx-freq FREQ must be specified\n")
			raise SystemExit
		rx_path = receive_path.receive_path(rx_callback, options)
		for attr in dir(rx_path): #forward the methods
			if not attr.startswith('_') and not hasattr(self, attr):
				setattr(self, attr, getattr(rx_path, attr))

		self._setup_source(options)
		self.connect(self.u, rx_path)

		if options.verbose:
			print 'USRP Source:', self.u
	
	def _setup_source(self, options):
	        self.symbol_rate=2; #for bpsk will edit the code later to set this automaticly based on the selected modulation scheme
	        self.u=uhd_receiver(options.args, self.symbol_rate,
                                        options.samples_per_symbol,
                                        options.rx_freq, options.rx_gain,
                                        options.spec, options.antenna,
                                        options.verbose)
                #options.samples_per_symbol = self.sink._sps
		#self.u = usrp_options.create_usrp_source(options)
		#adc_rate = self.u.adc_rate()
		#self.u.set_decim(options.decim)
		#self.u.set_bandwidth(options.bandwidth)
		#self.u.set_samp_rate(options.sample_rate)
		#if not self.u.set_center_freq(options.rx_freq):
			#print "Failed to set Rx frequency to %s" % (eng_notation.num_to_str(options.rx_freq))
			#raise ValueError, eng_notation.num_to_str(options.rx_freq)
