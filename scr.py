#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" 
Create a KML file based on exif data

Requires exiftool to have been installed    
Usage: exif2kml.py *.jpg > output.kml
python scr.py *.JPG

"""

import os
import sys
import re
import time

def decimalat(DegString):
    # This function requires that the re module is loaded
    # Take a string in the format "34 56.78 N" and return decimal degrees
    SearchStr=r''' *(\d+) deg (\d+)' ([\d\.]+)" (\w)'''
    Result = re.search(SearchStr, DegString)

    # Get the (captured) character groups from the search
    Degrees = float(Result.group(1))
    Minutes = float(Result.group(2))
    Seconds = float(Result.group(3))
    Compass = Result.group(4).upper() # make sure it is capital too

    # Calculate the decimal degrees
    DecimalDegree = Degrees + Minutes/60 + Seconds/(60*60)
    if Compass == 'S' or Compass == 'W':
        DecimalDegree = -DecimalDegree  
    return DecimalDegree

def writePlace(filename,lon,lat,alt,date):
    PlacemarkString = '''
   <trkpt lat="{0}" lon="{1}">
    <ele>{2}</ele>
    <time>{3}</time>
   </trkpt>'''.format(lat,lon,alt,date)
   
    #print PlacemarkString

    PlacemarkString2 = '''   
    <Placemark>
     <name>{0}</name>
     <Point>
      <altitudeMode>absolute</altitudeMode>
      <coordinates>{1}, {2}</coordinates>
      <TimeStamp>
        <when>{3}</when>
      </TimeStamp>
     </Point>
    </Placemark>'''.format(filename,lat,lon,date)
    return PlacemarkString 

HeadString='''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
<Document>'''

if len(sys.argv)<2:
    print >> sys.stderr, __doc__

else:
    placestring = ''
    FList = sys.argv[1:]
    for F in FList:
        ExifData=os.popen('exiftool "'+ F +'" -DateTimeOriginal -GPSLatitude -GPSLongitude -gpsaltitude').read()
        if "Longitude" in ExifData:
            print >> sys.stderr, F,"\n",ExifData.rstrip()
            Fields = ExifData.split("\n")
            for Items in Fields:
                if len(Items)> 10:
                    K,V = Items.split(" : ")
                    if "Latitude" in K:
                        lat = decimalat(V)
                    elif "Longitude" in K:
                        lon = decimalat(V)
                    elif "Altitude" in K:
                        print K
                        alt=V.split(" m")[0]
                        #alt = decimalat(resAlt)
                    elif "Date" in K:
                        date = time.strptime(V.strip(),"%Y:%m:%d %H:%M:%S")  # time format
            if lat:
                TimeFmt = "%Y-%m-%dT%H:%M:%S"
                placestring += writePlace(F,lon,lat,alt,time.strftime(TimeFmt,date))
                lat = ''
                alt = ''
    # Generate the output file...
    # This just prints to screen -- use > to capture to file...
    print HeadString
    print placestring
    print """</Document>\n</kml>"""