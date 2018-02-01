#!/usr/bin/env python
#
# Create rrd file with:
# rrdtool create temperatures.rrd --start N  DS:temps1:GAUGE:120:-40:200  DS:temps2:GAUGE:120:-40:200  DS:temps3:GAUGE:120:-40:200  DS:temps4:GAUGE:120:-40:200  DS:hums1:GAUGE:120:0:100  DS:hums2:GAUGE:120:0:100  DS:hums3:GAUGE:120:0:100  DS:hums4:GAUGE:120:0:100  RRA:AVERAGE:0.5:1:2880  RRA:AVERAGE:0.5:6:700  RRA:AVERAGE:0.5:6:700  RRA:AVERAGE:0.5:24:775  RRA:AVERAGE:0.5:144:1500  RRA:AVERAGE:0.5:288:2000  RRA:MIN:0.5:1:600  RRA:MIN:0.5:6:700  RRA:MIN:0.5:24:775  RRA:MIN:0.5:144:1500  RRA:MIN:0.5:288:2000  RRA:MAX:0.5:6:700  RRA:MAX:0.5:24:775  RRA:MAX:0.5:144:1500  RRA:MAX:0.5:288:2000
#
#

import time
import os
import sys
import datetime
import subprocess
import shlex
import yaml

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../library/Adafruit_Python_DHT/')
import Adafruit_DHT

stream = open(os.path.dirname(os.path.abspath(__file__)) + '/../config/config.yaml', "r")
config = yaml.load(stream)


RETRY = 3
Valid=False
sensor1 = Adafruit_DHT.DHT22
pin1 = config['sensor1pin']
sensor2 = Adafruit_DHT.DHT22
pin2 = config['sensor2pin']
sensor3 = Adafruit_DHT.DHT22
pin3 = config['sensor3pin']
sensor4 = Adafruit_DHT.DHT22
pin4 = config['sensor4pin']


def readDHT_sensor(sensor, pin):
  if pin is not None:
    #retry at least RETRY times if something wrong
    for loop in range(RETRY):
      #put a minimum of interval stabilization
      if loop!=0:
        time.sleep(2)
      humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

      time.sleep(0.2)
      if temperature == (-999):
        continue
      if humidity == (-999):
        continue
      fahrenheit = 9.0/5.0 * temperature + 32
      return [fahrenheit, humidity]
  return [None , None]

##### MAIN #######

def main():
  sensor1Data = readDHT_sensor(sensor1, pin1)
  sensor2Data = readDHT_sensor(sensor2, pin2)
  sensor3Data = readDHT_sensor(sensor3, pin3)
  sensor4Data = readDHT_sensor(sensor4, pin4)

  now = datetime.datetime.now()
  webdata = os.path.dirname(os.path.abspath(__file__)) + "/../public/data/"

  #put current value into a file, useful for zabbix/nagios/etc... monitoring

  def TempS(value):
    if value == None :
      return "---"
    return value
  try:
    file = open(webdata+"Sensor1.txt","w")
    file.write("{0}\t{1:.2f}\t{2:.2f}\n".format(now,TempS(sensor1Data[0]),TempS(sensor1Data[1])))
    file.close()
  except:
    pass
  try:
    file = open(webdata+"Sensor2.txt","w")
    file.write("{0}\t{1:.2f}\t{2:.2f}\n".format(now,TempS(sensor2Data[0]),TempS(sensor2Data[1])))
    file.close()
  except:
    pass
  try:
    file = open(webdata+"Sensor3.txt","w")
    file.write("{0}\t{1:.2f}\t{2:.2f}\n".format(now,TempS(sensor3Data[0]),TempS(sensor3Data[1])))
    file.close()
  except:
    pass
  try:
    file = open(webdata+"Sensor4.txt","w")
    file.write("{0}\t{1:.2f}\t{2:.2f}\n".format(now,TempS(sensor4Data[0]),TempS(sensor4Data[1])))
    file.close()
  except:
    pass

  ########rddtool

  def Validate(value):
    if value == None:
      return ":U"
    else:
      return ":{0:.2f}".format(value)

  #create text string to insert data
  rdata = "N" + Validate(sensor1Data[0]) + Validate(sensor2Data[0]) + Validate(sensor3Data[0]) + Validate(sensor4Data[0]) + Validate(sensor1Data[1]) + Validate(sensor2Data[1]) + Validate(sensor3Data[1]) + Validate(sensor4Data[1])
  #now lets insert it into the rddtool data
  fileRrdtool = os.path.dirname(os.path.abspath(__file__)) + "/../rrd/temperatures.rrd"
  proc = subprocess.Popen(["rrdtool","update",fileRrdtool,rdata])
  proc.wait()
  #and now let's extract data to create data file for the web page
  def rrdExport(start , step , sortieXML):
    #temperature
    texte = "rrdtool xport -s {0} -e now --step {1} ".format(start, step)
    texte += "DEF:a={0}:temps1:AVERAGE ".format(fileRrdtool)
    texte += "DEF:c={0}:temps2:AVERAGE ".format(fileRrdtool)
    texte += "DEF:e={0}:temps3:AVERAGE ".format(fileRrdtool)
    texte += "DEF:g={0}:temps4:AVERAGE ".format(fileRrdtool)
    texte += "XPORT:a:""Sensor1Temperature"" "
    texte += "XPORT:c:""Sensor2Temperature"" "
    texte += "XPORT:e:""Sensor3Temperature"" "
    texte += "XPORT:g:""Sensor4Temperature"" "
    fileout = open(webdata+"temperature"+sortieXML,"w")
    args = shlex.split(texte)
    proc = subprocess.Popen(args, stdout=fileout)
    proc.wait()
    fileout.close()
    #humidity
    texte = "rrdtool xport -s {0} -e now --step {1} ".format(start, step)
    texte += "DEF:b={0}:hums1:AVERAGE ".format(fileRrdtool)
    texte += "DEF:d={0}:hums2:AVERAGE ".format(fileRrdtool)
    texte += "DEF:f={0}:hums3:AVERAGE ".format(fileRrdtool)
    texte += "DEF:h={0}:hums4:AVERAGE ".format(fileRrdtool)
    texte += "XPORT:b:""Sensor1Humidity"" "
    texte += "XPORT:d:""Sensor2Humidity"" "
    texte += "XPORT:f:""Sensor3Humidity"" "
    texte += "XPORT:h:""Sensor4Humidity"" "
    fileout = open(webdata+"humidity"+sortieXML,"w")
    args = shlex.split(texte)
    proc = subprocess.Popen(args, stdout=fileout)
    proc.wait()
    fileout.close()
  #ok extact 3 hours data
  rrdExport("now-3h",300, "3h.xml")
  #ok 24 hours
  rrdExport("now-24h",900, "24h.xml")
  #ok 48 hours
  rrdExport("now-48h",1800, "48h.xml")
  #ok 1 week
  rrdExport("now-8d",3600, "1w.xml")
  #ok 1 month
  rrdExport("now-1month",14400, "1m.xml")
  #ok 3 month
  rrdExport("now-3month",28800, "3m.xml")
  #ok 1 year
  rrdExport("now-1y",43200, "1y.xml")

main()
