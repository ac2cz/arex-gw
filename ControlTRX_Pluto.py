
##################################################
# AREX Gateway Control Thread
# Adapted from Piped Commands TRx Control Thread for Hayling Transceiver Pluto Version 
# Many thanks to original Author: G4EML
# Author: Chris Thompson VE2TCP
#
# Needs to be manually added into Gnu Radio Flowgraph
##################################################

####################################################
#Add these imports to the top
#####################################################
 
import os
import errno

#######################################################
# Add these lines at the start of the Variables section
#######################################################

        plutoip=os.environ.get('PLUTO_IP')
        if plutoip==None :
          plutoip='pluto.local'
        plutoip='ip:' + plutoip
        
########################################################
# change the audio definition if needed to this for linux (leave as is for PI)
########################################################

        self.alsa_audio_source = alsa_audio_source = "plughw:3,0,1"
        self.alsa_audio_sink = alsa_audio_sink = "plughw:3,0,0"
        
#######################################################
# Manually inserted Functions
# to provide support for Piped commands
#######################################################
def docommands(tb):
  try:
    os.mkfifo("/tmp/arex_gw_rx") # Commands Received by Radio
  except OSError as oe:
    if oe.errno != errno.EEXIST:
      raise    
  try:
    os.mkfifo("/tmp/arex_gw_tx") # Commands Sent to Radio
  except OSError as oe:
    if oe.errno != errno.EEXIST:
      raise    
  ex=False
  lastbase=0
  while not ex:
    fifoin=open("/tmp/arex_gw_rx",'r')
    while True:
       try:
        with fifoin as filein:
         for line in filein:
           line=line.strip()
           #print(line);
           if line[0]=='Q':
              ex=True                  
           if line[0]=='U':
              value=int(line[1:])
              tb.set_Rx_Mute(value)
           if line[0]=='H':
              value=int(line[1:])
              if value==1:   
                  tb.lock()
              if value==0:
                  tb.unlock() 
           if line[0]=='O':
              value=int(line[1:])
              tb.set_RxOffset(value)  
           if line[0]=='V':
              value=int(line[1:])
              tb.set_AFGain(value)
           if line[0]=='L':
              value=int(line[1:])
              tb.set_Rx_LO(value)
           if line[0]=='A':
              value=int(line[1:])
              tb.set_Rx_Gain(value) 
           if line[0]=='F':
              value=int(line[1:])
              tb.set_Rx_Filt_High(value) 
           if line[0]=='I':
              value=int(line[1:])
              tb.set_Rx_Filt_Low(value) 
           if line[0]=='M':
              value=int(line[1:])
              tb.set_Rx_Mode(value) 
              tb.set_Tx_Mode(value)
           if line=='R':
              tb.set_PTT(False) 
           if line=='T':
              tb.set_PTT(True)
           if line[0]=='K':
              value=int(line[1:])
              tb.set_KEY(value) 
           if line[0]=='B':
              value=int(line[1:])
              tb.set_ToneBurst(value) 
           if line[0]=='G':
              value=int(line[1:])
              tb.set_MicGain(value) 
           if line[0]=='g':
              value=int(line[1:])
              tb.set_FMMIC(value)
           if line[0]=='d':
              value=int(line[1:])
              tb.set_AMMIC(value)
           if line[0]=='f':
              value=int(line[1:])
              tb.set_Tx_Filt_High(value) 
           if line[0]=='i':
              value=int(line[1:])
              tb.set_Tx_Filt_Low(value)     
           if line[0]=='l':
              value=int(line[1:])
              tb.set_Tx_LO(value)  
           if line[0]=='a':
              value=int(line[1:])
              tb.set_Tx_Gain(value)     
           if line[0]=='C':
              value=int(line[1:])
              tb.set_CTCSS(value)   
           if line[0]=='W':
              value=int(line[1:])
              tb.set_FFT_SEL(value) 
           if line[0]=='S':
               fifoout=open("/tmp/arex_gw_tx",'w')
               fifoout.write(str(int(4096*tb.rx_mag_level))+'\n')
               close(fifoout)
                                                                                
       except:
         break


#########################################################
# Manually Replaced Main() function
########################################################
def main(top_block_cls=arex_lang_trx_pluto, options=None):
    tb = top_block_cls()
    tb.start()
    docommands(tb)
    tb.stop()
    tb.wait()

#########################################################
