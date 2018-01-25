import serial
import pynmea2
import sys
import math
from ultimate_gps import get_gps
from HMC5883L import get_heading

NUM_SATS_NEEDED = 8
GPS_WAYPOINT_ARRAY = [[-26.351797, 153.007266], [-26.351816, 153.007397], [-26.351858, 153.007521], [-26.351983, 153.007560]]
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

def get_heading_error():
	heading_error = course_to_waypoint(-26.351797, 153.007266) - get_heading()
	if(heading_error > -180):
		if(heading_error > 180):
			heading_error = heading_error -360
		else:
			heading_error = heading_error + 360
	return heading_error


def init():
	next_way_point()




while True:
	init()
	gps_found, gps_msg = get_gps(NUM_SATS_NEEDED)
	direction_string = "TRUE," + str(int(distance_to_waypoint(-26.351797, 153.007266))) + "," + str(int(get_heading_error())) + ";"
	print(direction_string)
	if(distance_to_waypoint(-26.351797, 153.007266) < GPS_WAYPOINT_TOLERANCE):
		next_way_point()



#	if(gps_found):
#		direction_string = "TRUE," + distance_to_waypoint(-26.351797, 153.007266) + "," + get_heading_error() + ";"
#		print(direction_string)
#		if(distance_to_waypoint(-26.351797, 153.007266) < GPS_WAYPOINT_TOLERANCE):
#			next_way_point()
	else:
		direction_string = "FALSE,,;"
	print(direction_string)
		
		

