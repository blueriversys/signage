
import subprocess
import os
import os.path
import re
import pyudev
import psutil
import json

from glob import glob
from subprocess import check_output, CalledProcessError
from os import listdir, path
from os.path import isfile, join
import shutil
from pathlib import Path

class USB:
    def __init__(self, is_raspberry_pi=True):
        self.is_raspberry_pi = is_raspberry_pi

    def mount_pen_drive(self):
        os.system('sudo umount /mnt')
        if os.path.exists('/dev/sda1'):
            os.system('sudo mount /dev/sda1 /mnt')
            return "/mnt"
        elif os.path.exists('/dev/sdb1'):
            os.system('sudo mount /dev/sdb1 /mnt')
            return "/mnt"
        else:
            return None

    def get_usb_devices(self):
        sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))
        usb_devices = (dev for dev in sdb_devices
                       if any(['usb' in dev.split('/')[5], 'usb' in dev.split('/')[6]]))
        return dict((os.path.basename(dev), dev) for dev in usb_devices)

    def get_mount_points(self):
        devices = self.get_usb_devices()
        fullInfo = []
        output = []
        for dev in devices:
            output = subprocess.check_output(['lsblk', '-lnpo', 'NAME,MOUNTPOINT', '/dev/' + dev]).splitlines()
        return output

    def get_mount_points1(self):
        cmd = ['lsblk', '-lnpo', 'NAME,MOUNTPOINT', '/dev/sdb']
        output = subprocess.check_output(cmd)
        print(output)
        return output

    def get_mount_points2(self):
        p_handler = subprocess.run(['lsblk', '-J', '-o', 'PATH,SERIAL,MOUNTPOINT'], check=True, capture_output=True)
        json_output = json.loads(p_handler.stdout.decode("utf-8"))
        # (serial, device_path, mount_point)
        drives = [(dev['path'], dev['mountpoint']) for dev in json_output['blockdevices']]
        mounts = []
        for path, mountpoint in drives:
            if not path.startswith('/dev/sd'):
                continue
            if path.startswith('/dev/sda'):
                continue
            if mountpoint == None:
                continue
            #print(path, mountpoint)
            mounts.append({'path':path, 'mountpoint':mountpoint})
        return mounts

    def is_pen_drive_present(self):
        pendrives = self.get_mount_points2()
        if len(pendrives) > 0:
            return True
        return False

    def get_pen_folder(self):
        if self.is_raspberry_pi:
            folder = self.mount_pen_drive()
        else:
            drive_info = self.get_mount_points1()
            info = drive_info[1].split()
            # print(f'drive mnt point {info[0]},  drive location {info[1]}')
            folder = info[1].decode('ascii')
        return folder

    def list_removable_devices(self):
        context = pyudev.Context()
#        removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') if
#                     device.attributes.asstring('removable') == "1"]
        removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') ]
        print(removable)
        print("---------------------------------------")
        for device in removable:
            partitions = [device.device_node for device in
                          context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
            print("All removable partitions: {}".format(", ".join(partitions)))
            print("Mounted removable partitions:")
            for p in psutil.disk_partitions():
                if p.device in partitions:
                    print("  {}: {}".format(p.device, p.mountpoint))

    def get_files(self, folder, ext):
        onlyfiles = [os.path.join(folder, f) for f in os.listdir(folder) if
        os.path.isfile(os.path.join(folder, f))]
        files = []
        for file in onlyfiles:
            if file.endswith(ext):
                files.append(file)
        if len(files) > 0:
            files.sort()
        return files

