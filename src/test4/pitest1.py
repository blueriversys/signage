#!/usr/bin/env python

import os
import sys
from glob import glob
from subprocess import check_output, CalledProcessError

def get_files(folder, ext):
    only_files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    files = []
    for file in only_files:
        if file.endswith(ext):
            files.append(file)
    if len(files) > 0:
        files.sort()
    return files

def get_usb_devices():
    sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))
    usb_devices = (dev for dev in sdb_devices
        if 'usb' in dev.split('/')[5])
    return dict((os.path.basename(dev), dev) for dev in usb_devices)

def get_mount_points(starts_with, devices=None):
    devices = devices or get_usb_devices()  # if devices are None: get_usb_devices
    output = check_output(['mount']).splitlines()
    output = [tmp.decode('UTF-8') for tmp in output]

    def is_usb(path):
        return any(dev in path for dev in devices)
    usb_info = (line for line in output if is_usb(line.split()[0]))
    return [(info.split()[2], info.split()[0]) for info in usb_info if info.split()[2].startswith(starts_with)]

def get_media_name(devices, starts_with):
    usb_mounts = get_mount_points(devices)
    return [(info.split()[0], info.split()[2]) for info in usb_mounts if info.split()[0].startswith(starts_with)]

#def get_mount_points(devices=None):
#    devices = devices or get_usb_devices() # if devices are None: get_usb_devices
#    output = check_output(['mount']).splitlines()
#    is_usb = lambda path: any(dev in path for dev in devices)
#    usb_info = (line for line in output if is_usb(line.split()[0]))
#    return [(info.split()[0], info.split()[2]) for info in usb_info]

def get_pi_pen_folder():
    sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))
    usb_devices = (dev for dev in sdb_devices if 'usb' in dev.split('/')[5])
    devices = dict((os.path.basename(dev), dev) for dev in usb_devices)

    output = check_output(['mount']).splitlines()
    output = [tmp.decode('UTF-8') for tmp in output]

    def is_usb(path):
        return any(dev in path for dev in devices)

    usb_info = (line for line in output if is_usb(line.split()[0]))
    mount_array = [(info.split()[2], info.split()[0]) for info in usb_info if info.split()[2].startswith('/home/pi')]

    if not mount_array:
        return None
    else:
        mount_key, mount_path = mount_array[0]
        return mount_key

if __name__ == '__main__':
    pi_pen_folder = get_pi_pen_folder()
    print(pi_pen_folder)

if __name__ == '__main__':
    media_name = sys.argv[1]
    mount_array = get_mount_points(media_name, media_name+"/*")
    if not mount_array:
        print("nothing was returned")
    else:
        for mount in mount_array:
            mount_key, mount_path = mount
            print(f"{mount_key}  ->   {mount_path}")
            files = get_files(mount_key, '.py')
            for file in files:
                print(f"{file}")
