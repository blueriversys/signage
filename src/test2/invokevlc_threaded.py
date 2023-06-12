import logging
import threading
import time
import subprocess
import os
import re
import shutil
import argparse
from display import Display
from usb import USB
#from os import path

TIME_SPENT_FILE = "time.dat"
REGISTRATION_FILE = "registration.dat"
TIME_IN_MINUTES = 1
FREE_TIME_IN_MINUTES = 1200
CPUINFO_PATH = "/proc/cpuinfo"

# These are the thread functions
def video_player(name):
    cmd = ["cvlc", "--loop", "--no-video-title-show"]
    playlist_file = conf_folder + "/" + "playlist.m3u"
    cmd.append(playlist_file)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    #process.wait()

def time_counter(name):
    spent_file = conf_folder + "/" + TIME_SPENT_FILE
    if not os.path.exists(spent_file):
        file = open(spent_file, 'w')
        file.write("0")
        file.close()

    with open(spent_file) as f:
        minutes = f.read()

    print(f'initial time is {minutes}')

    while True:
        time.sleep(TIME_IN_MINUTES*60)
        with open(spent_file, 'w') as f:
            min_int = int(minutes)
            min_int += 1
            minutes = str(min_int)
            f.write(minutes)
            print(f'one more minute written to file')


def get_time_left_in_minutes():
    spent_file = conf_folder + "/" + TIME_SPENT_FILE
    with open(spent_file) as f:
        minutes = f.read()
        minutes.strip(" ")
        minutes = int(minutes)

    if FREE_TIME_IN_MINUTES > minutes:
        return FREE_TIME_IN_MINUTES - minutes
    else:
        return 0

def is_raspberry_pi():
    if not os.path.exists(CPUINFO_PATH):
        return False
    with open(CPUINFO_PATH) as f:
        cpuinfo = f.read()
    return re.search(r"^Model\s*:\s*Raspberry Pi", cpuinfo, flags=re.M) is not None

def list_file_paths():
    """Search all the file reader paths for movie files with the provided extensions.
    """
    # Get list of paths to search from the file reader.
    reader = USBDriveReader()
    _extensions = ["bmp", "dat"]
    paths = reader.search_paths()

    # Enumerate all movie files inside those paths.
    if not len(paths):
        print("no file found in USB drive")
        return

    movies = []
    for apath in paths:
        # Skip paths that don't exist or are files.
        if not os.path.exists(apath) or not os.path.isdir(apath):
            continue

        for x in os.listdir(apath):
            # Ignore hidden files (useful when file loaded on usb key from an OSX computer
            if x[0] != '.' and re.search('\.({0})$'.format(_extensions), x, flags=re.IGNORECASE):
                repeatsetting = re.search('_repeat_([0-9]*)x', x, flags=re.IGNORECASE)
                if (repeatsetting is not None):
                    repeat = repeatsetting.group(1)
                else:
                    repeat = 1
                basename, extension = os.path.splitext(x)
                print(f"filename {basename}")

def list_pen_folder(usb):
    print(f"This is a raspberry PI: {is_raspberry_pi()}")

    if usb.is_pen_drive_present():
        devices = usb.get_mount_points2()
        print("pen drive is present...here is a list of devices:")
        for device in devices:
            print(f"device: {device['path']}   mountpoint: {device['mountpoint']}")
            print(f"files in folder {device['mountpoint']}:")
            files = usb.get_files(device['mountpoint'], 'mp4')
            for file in files:
                print(file)
        return

    print(f"no pen drive attached")

def search_and_copy_registration(usb):
        devices = usb.get_mount_points2()
        print("pen drive is present...here is a list of devices:")
        dst_folder = conf_folder
        for device in devices:
            files = usb.get_files(device['mountpoint'], 'dat')
            for file in files:
                if file.endswith(REGISTRATION_FILE):
                    shutil.copy(file, f'{dst_folder}')
                    print(f"file name {file} copied to {dst_folder}")
        return

def main():
    usb = USB(is_raspberry_pi())

    if usb.is_pen_drive_present():
        search_and_copy_registration(usb)

    local_registration = conf_folder + "/" + REGISTRATION_FILE
    if not os.path.exists(local_registration):
        minutes_left = get_time_left_in_minutes()
        display = Display()
        display.print_line(180, "This is an unregistered version of the software.", 80)
        display.print_line(240, f"Minutes left to use in unregistered mode:", 80)
        display.print_line(300, f"{minutes_left}", 80)
        display.print_countdown("Videos will start playing in a moment...", 100, 10)
        display.quit()

    # list files on the usb drive, if drive is present
    list_pen_folder(usb)

    # start video playing thread
    video_player_thread = threading.Thread(target=video_player, args=(1,))
    video_player_thread.start()

    # start time counting thread
    time_counter_thread = threading.Thread(target=time_counter, args=(1,))
    time_counter_thread.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Invoker of the VLC player')
    parser.add_argument("-c", "--conf",
                      required=True,
                      dest="conf_folder",
                      help="Folder where the config files will be placed",
                      type=str,
                      action="store"
                      )

    parser.add_argument("-v", "--videos",
                      required=True,
                      dest="videos_folder",
                      help="Folder where the video files will be placed",
                      type=str,
                      action="store"
                      )

    parser.add_argument("-l", "--logo",
                      required=True,
                      dest="logo_folder",
                      help="Folder where the logo file will be placed",
                      type=str,
                      action="store"
                      )

    args = parser.parse_args()

    conf_folder = args.conf_folder
    videos_folder = args.videos_folder
    logo_folder = args.logo_folder

    # invoke main()
    main()
