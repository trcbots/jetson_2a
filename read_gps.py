import serial
import pynmea2
import sys
serial_gps = serial.Serial()

serial_gps.port = '/dev/ttyUSB0'
serial_gps.baudrate = 9600
serial_gps.open()

# GPS CONFIG MACROS
PMTK_SET_NMEA_BAUDRATE = '$PMTK251,9600*17'
PMTK_SET_NMEA_UPDATE_5HZ = "$PMTK220,200*2C"
PMTK_SET_NMEA_OUTPUT_RMCONLY = '$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29'
PMTK_SET_NMEA_OUTPUT_RMCGGA = "$PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28"
PMTK_SET_NMEA_OUTPUT_GGAONLY = "$PMTK314,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29"
NUM_SATS_NEEDED = 8


# GPS CONFIG ROUTINE
serial_gps.write(PMTK_SET_NMEA_BAUDRATE + '\r\n')
serial_gps.write(PMTK_SET_NMEA_OUTPUT_GGAONLY + '\r\n')
serial_gps.write(PMTK_SET_NMEA_UPDATE_5HZ + '\r\n')


while True:

	for line in serial_gps.read():
		line = serial_gps.readline()
		isline = False
		try: # try statement so that GGAONLY doesn't catch the initial line and crash
			msg = pynmea2.parse(line, check=True)
		except:
			print('bad line for GGAONLY')
		try:
			lat = msg.lat
			lon = msg.lon
			num_sats = msg.num_sats
			
			if num_sats >= NUM_SATS_NEEDED:
				numSats = True
			print('lat: ' + lat + ' lon: ' + lon + ' Satelites: ' + num_sats)
		except:
			print("bad GPS signal or GGAONLY invoked")
			#ser.close()




