import os
from glob import glob
from subprocess import check_output, CalledProcessError
import sys
import subprocess
from os import listdir
from os.path import isfile, join


def get_usb_devices():
    sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))
    usb_devices = (dev for dev in sdb_devices
                   if any(['usb' in dev.split('/')[5],
                           'usb' in dev.split('/')[6]]))
    return dict((os.path.basename(dev), dev) for dev in usb_devices)

def get_mount_points():
    devices = get_usb_devices()
    fullInfo = []
    output = []
    for dev in devices:
        output = subprocess.check_output(['lsblk', '-lnpo', 'NAME,MOUNTPOINT', '/dev/' + dev]).splitlines()
    return output
        
def is_pen_drive_present():
    pendrives = get_mount_points()
    if len(pendrives) > 0:
        return True
    return False
             
def get_files(folder, ext):
    onlyfiles = [os.path.join(folder, f) for f in os.listdir(folder) if 
    os.path.isfile(os.path.join(folder, f))]
    files = []
    for file in onlyfiles:
        if file.endswith(ext):
            files.append(file)
    return files 
                
if __name__ == '__main__':
    if is_pen_drive_present():
        drive_info = get_mount_points()
        print(drive_info[1])
        info = drive_info[1].split()
        print(f'drive mnt point {info[0]},  drive location {info[1]}')
        media_files = get_files(info[1].decode('ascii'), '.mp4')
        for file in media_files:
            print(file)
    else:
        print('no pen drive inserted')
        
