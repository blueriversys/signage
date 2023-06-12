import os
import os.path
import re
from glob import glob
from subprocess import check_output, CalledProcessError
from os import listdir, path
from os.path import isfile, join
from usb import USB

def get_files(folder, ext):
    only_files = [os.path.join(folder, f) for f in os.listdir(folder) if
    os.path.isfile(os.path.join(folder, f))]
    files = []
    for file in only_files:
        if file.endswith(ext):
            files.append(file)
    if len(files) > 0:
        files.sort()
    return files

def mount_pen_drive():
#    os.system('sudo umount /mnt')
    if os.path.exists('/dev/sda1'):
        os.system('sudo mount /dev/sda1 /mnt')
        return "/mnt"
    elif os.path.exists('/dev/sdb1'):
        os.system('sudo mount /dev/sdb1 /mnt')
        return "/mnt"
    else:
        return None

def get_pen_folder():
    folder = mount_pen_drive()
    print(f"folder {folder}")
    return folder

def have_pen_drive_files(file_type):
    pen_folder = get_pen_folder()
    if pen_folder is None:
       return False
    media_files = get_files(pen_folder, file_type)
    if len(media_files) > 0:
        return True
    return False

def process_pen_drive_files():
    if have_pen_drive_files('registration.dat'):
        pen_folder = get_pen_folder()
        print(f"found {pen_folder}/registration.dat")
    else:
        print("not found registration.dat")

def test_usb_class():
    usb = USB(True)

    if usb.is_pen_drive_present():
        print(f"usb is present")
        pen_folder = usb.get_pen_folder()
        print(f"usb pen folder: {pen_folder}")
    else:
        print("pen drive not present")


if __name__ == '__main__':
    #process_pen_drive_files()
    test_usb_class()