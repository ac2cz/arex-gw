#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: AREX Gateway Pluto SDR
# Author: Chris Thompson VE2TCP
# Copyright: 2024 ARISS
# Description: AREX Gateway Demonstration of full duplex radio
# GNU Radio version: 3.10.1.1

from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio




class arex_gw_pluto(gr.top_block):

    def __init__(self, decimation=1, fm_station=145990000, rx_audio_device="plughw:3,0,0", tx_audio_device="plughw:3,0,1", uri='ip:pluto.local'):
        gr.top_block.__init__(self, "AREX Gateway Pluto SDR", catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.decimation = decimation
        self.fm_station = fm_station
        self.rx_audio_device = rx_audio_device
        self.tx_audio_device = tx_audio_device
        self.uri = uri

        ##################################################
        # Variables
        ##################################################
        self.tx_mode = tx_mode = 4
        self.tx_fm_mic_gain = tx_fm_mic_gain = 1
        self.sample_rate = sample_rate = 576000
        self.audio_sample_rate = audio_sample_rate = 48000
        self.PTT = PTT = 1

        ##################################################
        # Blocks
        ##################################################
        self.low_pass_filter_1 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                576000,
                5000,
                2000,
                window.WIN_HAMMING,
                6.76))
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            4,
            firdes.low_pass(
                1,
                sample_rate,
                8000,
                5000,
                window.WIN_HAMMING,
                6.76))
        self.iio_pluto_source_0 = iio.fmcomms2_source_fc32(uri if uri else iio.get_pluto_uri(), [True, True], 0x20000)
        self.iio_pluto_source_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0.set_frequency(fm_station)
        self.iio_pluto_source_0.set_samplerate(sample_rate)
        self.iio_pluto_source_0.set_gain_mode(0, 'manual')
        self.iio_pluto_source_0.set_gain(0, 64)
        self.iio_pluto_source_0.set_quadrature(True)
        self.iio_pluto_source_0.set_rfdc(True)
        self.iio_pluto_source_0.set_bbdc(True)
        self.iio_pluto_source_0.set_filter_params('Auto', '', 0, 0)
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32(uri if uri else iio.get_pluto_uri(), [True, True], 32768, False)
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(20000000)
        self.iio_pluto_sink_0.set_frequency(437800000)
        self.iio_pluto_sink_0.set_samplerate(576000)
        self.iio_pluto_sink_0.set_attenuation(0, 0)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.blocks_mute_xx_0 = blocks.mute_cc(bool(not PTT))
        self.blocks_multiply_const_xx_0 = blocks.multiply_const_ff(0.5, 1)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_cc(tx_mode==4)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(tx_fm_mic_gain/10)
        self.band_pass_filter_0 = filter.fir_filter_fff(
            1,
            firdes.band_pass(
                1,
                audio_sample_rate,
                10,
                3500,
                100,
                window.WIN_HAMMING,
                6.76))
        self.audio_source_0 = audio.source(audio_sample_rate, tx_audio_device, True)
        self.audio_sink_0 = audio.sink(audio_sample_rate, rx_audio_device, True)
        self.analog_rail_ff_0 = analog.rail_ff(-1, 1)
        self.analog_nbfm_tx_0 = analog.nbfm_tx(
        	audio_rate=audio_sample_rate,
        	quad_rate=576000,
        	tau=75e-6,
        	max_dev=5e3,
        	fh=-1,
                )
        self.analog_nbfm_rx_0 = analog.nbfm_rx(
        	audio_rate=48000,
        	quad_rate=144000,
        	tau=75e-6,
        	max_dev=5e3,
          )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_nbfm_rx_0, 0), (self.blocks_multiply_const_xx_0, 0))
        self.connect((self.analog_nbfm_tx_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.analog_rail_ff_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.audio_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.analog_nbfm_tx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.analog_rail_ff_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_mute_xx_0, 0))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_mute_xx_0, 0), (self.low_pass_filter_1, 0))
        self.connect((self.iio_pluto_source_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_nbfm_rx_0, 0))
        self.connect((self.low_pass_filter_1, 0), (self.iio_pluto_sink_0, 0))


    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation

    def get_fm_station(self):
        return self.fm_station

    def set_fm_station(self, fm_station):
        self.fm_station = fm_station
        self.iio_pluto_source_0.set_frequency(self.fm_station)

    def get_rx_audio_device(self):
        return self.rx_audio_device

    def set_rx_audio_device(self, rx_audio_device):
        self.rx_audio_device = rx_audio_device

    def get_tx_audio_device(self):
        return self.tx_audio_device

    def set_tx_audio_device(self, tx_audio_device):
        self.tx_audio_device = tx_audio_device

    def get_uri(self):
        return self.uri

    def set_uri(self, uri):
        self.uri = uri

    def get_tx_mode(self):
        return self.tx_mode

    def set_tx_mode(self, tx_mode):
        self.tx_mode = tx_mode
        self.blocks_multiply_const_vxx_0_0.set_k(self.tx_mode==4)

    def get_tx_fm_mic_gain(self):
        return self.tx_fm_mic_gain

    def set_tx_fm_mic_gain(self, tx_fm_mic_gain):
        self.tx_fm_mic_gain = tx_fm_mic_gain
        self.blocks_multiply_const_vxx_0.set_k(self.tx_fm_mic_gain/10)

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.iio_pluto_source_0.set_samplerate(self.sample_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.sample_rate, 8000, 5000, window.WIN_HAMMING, 6.76))

    def get_audio_sample_rate(self):
        return self.audio_sample_rate

    def set_audio_sample_rate(self, audio_sample_rate):
        self.audio_sample_rate = audio_sample_rate
        self.band_pass_filter_0.set_taps(firdes.band_pass(1, self.audio_sample_rate, 10, 3500, 100, window.WIN_HAMMING, 6.76))

    def get_PTT(self):
        return self.PTT

    def set_PTT(self, PTT):
        self.PTT = PTT
        self.blocks_mute_xx_0.set_mute(bool(not self.PTT))



def argument_parser():
    description = 'AREX Gateway Demonstration of full duplex radio'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--decimation", dest="decimation", type=intx, default=1,
        help="Set Decimation [default=%(default)r]")
    parser.add_argument(
        "--fm-station", dest="fm_station", type=intx, default=145990000,
        help="Set FM station [default=%(default)r]")
    parser.add_argument(
        "--rx-audio-device", dest="rx_audio_device", type=str, default="plughw:3,0,0",
        help="Set Audio device [default=%(default)r]")
    parser.add_argument(
        "--tx-audio-device", dest="tx_audio_device", type=str, default="plughw:3,0,1",
        help="Set Audio device [default=%(default)r]")
    parser.add_argument(
        "--uri", dest="uri", type=str, default='ip:pluto.local',
        help="Set URI [default=%(default)r]")
    return parser


def main(top_block_cls=arex_gw_pluto, options=None):
    if options is None:
        options = argument_parser().parse_args()
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print("Error: failed to enable real-time scheduling.")
    tb = top_block_cls(decimation=options.decimation, fm_station=options.fm_station, rx_audio_device=options.rx_audio_device, tx_audio_device=options.tx_audio_device, uri=options.uri)

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
