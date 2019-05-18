#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, serial, argparse, time, csv, datetime

class vedirect:

    def __init__(self, serialport, timeout):
        self.serialport = serialport
        self.ser = serial.Serial(serialport, 19200, timeout=timeout)
        self.header1 = '\r'
        self.header2 = '\n'
        self.hexmarker = ':'
        self.delimiter = '\t'
        self.key = ''
        self.value = ''
        self.bytes_sum = 0
        self.state = self.WAIT_HEADER
        self.dict = {}


    (HEX, WAIT_HEADER, IN_KEY, IN_VALUE, IN_CHECKSUM) = range(5)

    def input(self, byte):
        if byte == self.hexmarker and self.state != self.IN_CHECKSUM:
            self.state = self.HEX


        if self.state == self.WAIT_HEADER:
            self.bytes_sum += ord(byte) # there is an error here, ord() expects a string of nonzero length
            if byte == self.header1:
                self.state = self.WAIT_HEADER
            elif byte == self.header2:
                self.state = self.IN_KEY

            return None
        elif self.state == self.IN_KEY:
            self.bytes_sum += ord(byte)
            if byte == self.delimiter:
                if (self.key == 'Checksum'):
                    self.state = self.IN_CHECKSUM
                else:
                    self.state = self.IN_VALUE
            else:
                self.key += byte
            return None
        elif self.state == self.IN_VALUE:
            self.bytes_sum += ord(byte)
            if byte == self.header1:
                self.dict[self.key] = self.value
                self.key = ''
                self.value = ''
            else:
                self.value += byte
            return None
        elif self.state == self.IN_CHECKSUM:
            self.bytes_sum += ord(byte)
            self.key = ''
            self.value = ''
            self.state = self.WAIT_HEADER
            if (self.bytes_sum % 256 == 0):
                self.bytes_sum = 0
                return self.dict
            else:
                print ('Malformed packet')
                self.bytes_sum = 0
        elif self.state == self.HEX:
            self.bytes_sum = 0
            if byte == self.header2:
                self.state = self.WAIT_HEADER
        else:
            raise AssertionError()

    def read_data(self):
        while True:
            byte = self.ser.read(1)
            packet = self.input(byte)

    def read_data_single(self):
        while True:
            byte = self.ser.read(1)
            packet = self.input(byte)
            if (packet != None):
                return packet


    def read_data_callback(self, callbackFunction):
        while True:
            byte = self.ser.read(1)
            if byte:
                packet = self.input(byte)
                if (packet != None):
                    callbackFunction(packet)
            else:
                break


def print_data_callback(data):
    print (data)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process VE.Direct protocol')
    parser.add_argument('--port', help='Serial port')
    parser.add_argument('--timeout', help='Serial port read timeout', type=int, default='60')
    args = parser.parse_args()
    ve = vedirect(args.port, args.timeout)
    #ve.read_data_callback(print_data_callback)
#make all the arrays associated with each variable
    datatimer = []
    volt =[] #key name is V
    i = []
    vpv = []
    ppv = []
    cs = []
    err = []
    h19 = [] #yield total
    h20 = [] #yield today
    h21 = [] #power max today
    h22 = [] #yield yesterday
    h23 = [] #power mas yesterday
#now start adding stuff into the arrays
# time the function
    start = time.time()
    while time.time()-start <= 600:
    #count = 0
        #while count<10:
        print(ve.read_data_single())
        datatimer.append(datetime.datetime.now())
        volt.append(ve.dict['V'])
        i.append(ve.dict['I'])
        vpv.append(ve.dict['VPV'])
        ppv.append(ve.dict['PPV'])
        cs.append(ve.dict['CS'])
        err.append(ve.dict['ERR'])
        h19.append(ve.dict['H19'])
        h20.append(ve.dict['H20'])
        h21.append(ve.dict['H21'])
        h22.append(ve.dict['H22'])
        h23.append(ve.dict['H23'])
    	#count +=1
        time.sleep(2)
    myData = [input('Trial Name')]
    myData.append(["time", "voltage", "current", "voltage panels", "PPV", "cs", "err", "h19", "h20", "h21", "h22", "h23"])
    p = 0 #appendcount
    while p<len(volt)-1:
    	myData.append([datatimer[p], volt[p], i[p], vpv[p], ppv[p], cs[p], err[p], h19[p], h20[p], h21[p], h22[p], h23[p]])
    	p+=1
    #print myData
    myFile = open('testdata.csv', 'a')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(myData)
    print ('Writing complete')
#make an array store that gets the data added into it