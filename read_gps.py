import serial
import pynmea2
import sys
import math

# GPS CONFIG MACROS
PMTK_SET_NMEA_BAUDRATE = '$PMTK251,9600*17'
PMTK_SET_NMEA_UPDATE_5HZ = "$PMTK220,200*2C"
PMTK_SET_NMEA_OUTPUT_RMCONLY = '$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29'
PMTK_SET_NMEA_OUTPUT_RMCGGA = "$PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28"
PMTK_SET_NMEA_OUTPUT_GGAONLY = "$PMTK314,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29"

NUM_SATS_NEEDED = 8
GPS_WAYPOINT_ARRAY = [[-26.351797, 153.007266], [-26.351816, 153.007397], [-26.351858, 153.007521], [-26.351983, 153.007560]]
GPS_WAYPOINT_TOLERANCE = 10
GPS_WAYPOINT_INDEX = 0


# GPS CONFIG ROUTINE
serial_gps = serial.Serial()
serial_gps.port = '/dev/ttyUSB0'
serial_gps.baudrate = 9600
serial_gps.open()
serial_gps.write(PMTK_SET_NMEA_BAUDRATE + '\r\n')
serial_gps.write(PMTK_SET_NMEA_OUTPUT_GGAONLY + '\r\n')
serial_gps.write(PMTK_SET_NMEA_UPDATE_5HZ + '\r\n')


def check_gps():
	for line in serial_gps.read():
		line = serial_gps.readline()
		try: # try statement so that GGAONLY doesn't catch the initial line and crash
			msg = pynmea2.parse(line, check=True)
		except:
			print('bad line for GGAONLY')
			return False, msg
		try:
			if int(msg.num_sats) >= NUM_SATS_NEEDED:
				return True, msg
			else :
				return False, msg
		except:
			print("bad GPS signal or GGAONLY invoked")
			return False, msg


def next_way_point() :
	global GPS_WAYPOINT_INDEX
	if(GPS_WAYPOINT_INDEX >= len(GPS_WAYPOINT_ARRAY) -1) :
		GPS_WAYPOINT_INDEX = 0
	else :
		GPS_WAYPOINT_INDEX += 1

def get_gps_target_lat() :
	return GPS_WAYPOINT_ARRAY[GPS_WAYPOINT_INDEX][0]

def get_gps_target_long() :
	return GPS_WAYPOINT_ARRAY[GPS_WAYPOINT_INDEX][1]


# returns distance in meters between two positions, both specified
# as signed decimal-degrees latitude and longitude. Uses great-circle
# distance computation for hypothetical sphere of radius 6372795 meters.
# Because Earth is no exact sphere, rounding errors may be up to 0.5%.
def distance_to_waypoint(current_lat, current_long) :
	delta = math.radians(current_long - get_gps_target_long())
	sdlong = math.sin(delta)
	cdlong = math.cos(delta)
	lat1 = math.radians(current_lat)
	lat2 = math.radians(get_gps_target_lat())
	slat1 = math.sin(lat1)
	clat1 = math.cos(lat1)
	slat2 = math.sin(lat2)
 	clat2 = math.cos(lat2)
	delta = (clat1 * slat2) - (slat1 * clat2 * cdlong)
	delta = delta * delta
	delta += (clat2 * sdlong) * (clat2 * sdlong)
	delta = math.sqrt(delta)
	denom = (slat1 * slat2) + (clat1 * clat2 * cdlong)
	delta = math.atan2(delta, denom)
	distance_to_target =  delta * 6372795
	return distance_to_target


# returns course in degrees (North=0, West=270) from position 1 to position 2,
# both specified as signed decimal-degrees latitude and longitude.
# Because Earth is no exact sphere, calculated course may be off by a tiny fraction.
def course_to_waypoint(current_lat, current_long) :
	dlon = math.radians(get_gps_target_long() - current_long)
	cLat = math.radians(current_lat)
	tLat = math.radians(get_gps_target_lat())
	a1 = math.sin(dlon) * math.cos(tLat)
	a2 = math.sin(cLat) * math.cos(tLat) * math.cos(dlon)
	a2 = math.cos(cLat) * math.sin(tLat) - a2
	a2 = math.atan2(a1, a2)
	if (a2 < 0.0) :
		a2 += 6.283185
	target_heading = math.degrees(a2)
	return target_heading




while True:
	next_way_point()
	print(distance_to_waypoint(-26.351797, 153.007266))
	print(course_to_waypoint(-26.351797, 153.007266))
	print(" ")
	gps_found, gps_msg = check_gps()
	if(gps_found):
		print('Useful GPS data returned.')
		print(int(gps_msg.num_sats))
