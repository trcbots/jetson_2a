import serial
import pynmea2
import sys
ser = serial.Serial()

ser.port = '/dev/ttyUSB0'
ser.baudrate = 9600
ser.open()

# CONFIG MACROS
PMTK_SET_NMEA_BAUDRATE = '$PMTK251,9600*17'
PMTK_SET_NMEA_OUTPUT_RMCONLY = '$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29'
PMTK_SET_NMEA_UPDATE_5HZ = "$PMTK220,200*2C"
PMTK_SET_NMEA_OUTPUT_RMCGGA = "$PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28"
PMTK_SET_NMEA_OUTPUT_GGAONLY = "$PMTK314,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29"
NUM_SATS_NEEDED = 8


# CONFIG ROUTINE
ser.write(PMTK_SET_NMEA_BAUDRATE + '\r\n')
ser.write(PMTK_SET_NMEA_OUTPUT_GGAONLY + '\r\n')
ser.write(PMTK_SET_NMEA_UPDATE_5HZ + '\r\n')

# Note: when using GGAONLY, dollar sign must be prepended to gps line

while True:


	for line in ser.read():
		line = ser.readline()
		isline = False
		try: # try statement so that GGAONLY doesn't catch the initial line and crash
			msg = pynmea2.parse('$' + line, check=True)
		except:
			print('bad line for GGAONLY')
		try:
			lat = msg.lat
			lon = msg.lon
			num_sats = msg.num_sats
			
			if num_sats >= NUM_SATS_NEEDED:
				numSats = True
			print('lat: ', lat, 'lon: ', lon, 'timestamp: ', times)
		except:
			print("bad GPS signal or GGAONLY invoked")
			#ser.close()




