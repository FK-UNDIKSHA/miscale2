import os
import sys
import time
import socket
import json
from datetime import datetime
from bluepy import btle
from bluepy.btle import Scanner, BTLEDisconnectError, BTLEManagementError, DefaultDelegate

BT_MAC = "50:FB:19:4B:88:43"
MINTA = ""
selesai = 0
hasil = ""
hasil_old = ""
noImpedande = 0
count = 0

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 6996        # Port to listen on (non-privileged ports are > 1023)

class MiScale2:
    """
    This Focused on Analyzing data Xiaomi Mi Scale 2 sended from ScanDelegate Class
    """
    def __init__(bt_data):
        self.BT_DATA = bt_data

def create_connection():
    """ create a database connection to a database that resides
        in the memory
    """
    conn = None;
    try:
        conn = sqlite3.connect('ukur.sqlite')
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

class ScanDelegate():
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        global MINTA, selesai, hasil, hasil_old, count
        if dev.addr == BT_MAC.lower() :
            #time.sleep(2)
            print("[DEBUG] Device Discovered Receiving Data...")
            for (sdid, desc, data) in dev.getScanData():
                #print(sdid, desc, data)
                if data.startswith('1b18') and sdid == 22:
                    data2 = bytes.fromhex(data[4:])
                    ctrlByte1 = data2[1]
                    isStabilized = ctrlByte1 & (1<<5)
                    hasImpedance = ctrlByte1 & (1<<1)

                    measunit = data[4:6]
                    measured = int((data[28:30] + data[26:28]), 16) * 0.01
                    unit = ''
                    if measunit == "03": unit = 'lbs'
                    if measunit == "02": unit = 'kg' ; measured = measured / 2
                    miimpedance = str(int((data[24:26] + data[22:24]), 16))
                    if unit and isStabilized:
                        print(count)

                        if count >= 0:
                            hasil = {"Berat": round(measured, 2), "Unit": "KG", "Impedance": miimpedance, "noImpedande" : noImpedande }
                            print(hasil)

                            if hasil_old == "":
                                hasil_old = hasil

                            if hasil_old == hasil:
                                count+= 1

                            if count > 10 or hasil_old != hasil:
                                if MINTA and hasil['Impedance'] < 10000:
                                    selesai = 1
                                elif not MINTA:
                                    selesai = 1

                            print(round(measured, 2), unit, str(datetime.now()), hasImpedance, miimpedance)

                            #if len(banding) <=5:
                            #    banding.append( round(measured, 2))

                        #count += 1

def mainV(status=0):
    global hasil, MINTA
    MINTA = status
    scanner = Scanner().withDelegate(ScanDelegate())
    while (selesai == 0):
        devices = scanner.scan(1, passive=True)
    temp = json.dumps(hasil).encode("utf-8")
    return hasil

def mainS():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', 6748))

    s.listen()
    while 1:
        conn, addr = s.accept()
        with conn:
            print('Connected by:', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                if data.decode('utf-8').lower().startswith('miscale2'):
                    noImpedande = 0
                    if 'noimpedance' in data.decode('utf-8').lower():
                        noImpedande = 1
                    time.sleep(5)
                    print("Silahkan Naik ke timbangan")
                    while (selesai == 0):
                        devices = scanner.scan(5)
                    temp = json.dumps(hasil).encode("utf-8")
                    conn.sendall(temp)
                    selesai = 0
                    count = 0
                    banding = []
                #conn.sendall(data)
if __name__ == '__main__':
    scanner = Scanner().withDelegate(ScanDelegate())
    while (selesai == 0):
        devices = scanner.scan(2, passive=True)
    print(hasil)
    """


    """

    #while (selesai == 0):
    #    devices = scanner.scan(1)
