import serial
import pynmea2
import sys
import math
import time
from ultimate_gps import get_gps
from HMC5883L import get_heading

NUM_SATS_NEEDED = 8
GPS_WAYPOINT_ARRAY = [[-27.8552175, 153.1511374], [-27.8554650, 153.1516188], [-26.351858, 153.007521], [-26.351983, 153.007560]]
GPS_WAYPOINT_TOLERANCE = 10
GPS_WAYPOINT_INDEX = 0
GPS_WAYPOINT_TOLERANCE = 1




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

def get_heading_error(current_lat, current_long):
	#print("heading: ", get_heading())
	#print("Course to waypoint: ", course_to_waypoint(current_lat, current_long))
	heading_error = course_to_waypoint(current_lat, current_long) - get_heading()
	if(heading_error > -180):
		if(heading_error > 180):
			heading_error = heading_error -360
	else:
		heading_error = heading_error + 360
	return heading_error


def init():
	next_way_point()





while True:	
	gps_found, gps_msg = get_gps(NUM_SATS_NEEDED)
	millis = int(round(time.time() * 1000))
	if(gps_found):
		#print("current lat: " + str(gps_msg.latitude))
		#print("current long: " + str(gps_msg.longitude))
		#print("heading: ", get_heading_error(gps_msg.latitude, gps_msg.longitude))
		try:
			direction_string = str(millis) + ",1," + str(int(distance_to_waypoint(gps_msg.latitude, gps_msg.longitude))) + "," + str(int(get_heading_error(gps_msg.latitude, gps_msg.longitude))) + ";"
			if(distance_to_waypoint(gps_msg.latitude, gps_msg.longitude) < GPS_WAYPOINT_TOLERANCE):
				next_way_point()
		except:
			direction_string = str(millis) + ",0,,;"
	else:
		direction_string = str(millis) + ",0,,;"
	print(direction_string)
		
		


