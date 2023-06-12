
'''
   This program invokes vlc on the command line and let it play the list of files
   specified in the command line.

   Example:
   cvlc --fullscreen --loop --play-and-exit --no-video-title-show --sub-text-scale=120  videos/video3-1-of-4.mp4 videos/video3-2-of-4.mp4 videos/video3-3-of-4.mp4 videos/video3-4-of-4.mp4

   To create a virtual env:
     python3 -m venv venv
     source venv/bin/activate
'''

import threading
import subprocess
import os
import os.path
import re
from glob import glob
from subprocess import check_output, CalledProcessError
from os import listdir, path
from os.path import isfile, join
import shutil
from pathlib import Path
from PIL import Image
#import pyautogui
import argparse
from display import Display
import time

vlc_player = "/usr/bin/cvlc"
#cmd = [ "/usr/bin/cvlc", "--fullscreen", "--loop", "--no-video-title-show", "--sub-text-scale=120", "--sub-source=logo", "--logo-position=5", "--logo-x=10", "--logo-y=10", "--logo-opacity=100" ]

TIME_SPENT_FILE = "time.dat"
REGISTRATION_FILE = "registration.dat"
TIME_IN_MINUTES = 1
FREE_TIME_IN_MINUTES = 1200
CPUINFO_PATH = "/proc/cpuinfo"
OPTIONS_FILE_NAME = "options.txt"

def read_options_from_file(conf_folder):
    options = []
    file = open(conf_folder+"/"+OPTIONS_FILE_NAME, "r")
    while True:
        line = file.readline()
        line = line.replace('\n', '')
        line = line.lstrip().rstrip()
        if not line:
            break
        if not line.startswith('#'):
            options.append(line)
    return options

def play_files(conf_folder, videos_folder, logo_folder):
    if not ready_to_play(conf_folder, videos_folder):
        print('not ready to play')
        return
    cmd = [vlc_player]
    cmd = cmd + read_options_from_file(conf_folder)
    cmd.append(f"--logo-file={logo_folder}/logo.png")
    cmd.append(f"{conf_folder}/playlist.m3u")
    print(f"vlc command: {cmd}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    process.wait()

def ready_to_play(conf_folder, videos_folder):
    if not path.exists(conf_folder + "/" + "playlist.m3u"):
        return False
    dir = os.listdir(videos_folder)
    if len(dir) == 0:
        return False
    return True
        
def is_raspberry_pi():
    if not path.exists(CPUINFO_PATH):
        return False
    with open(CPUINFO_PATH) as f:
        cpuinfo = f.read()
    return re.search(r"^Model\s*:\s*Raspberry Pi", cpuinfo, flags=re.M) is not None

def mount_pen_drive():
    os.system('sudo umount /mnt')
    if os.path.exists('/dev/sda1'):
        os.system('sudo mount /dev/sda1 /mnt')
        return "/mnt"
    elif os.path.exists('/dev/sdb1'):
        os.system('sudo mount /dev/sdb1 /mnt')
        return "/mnt"
    else:
        return None

#def get_usb_devices():
#    sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))
#    usb_devices = (dev for dev in sdb_devices
#                   if any(['usb' in dev.split('/')[5],
#                           'usb' in dev.split('/')[6]]))
#    return dict((os.path.basename(dev), dev) for dev in usb_devices)

#def get_usb_devices():
#    sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))
#    usb_devices = (dev for dev in sdb_devices
#        if 'usb' in dev.split('/')[5])
#    return dict((os.path.basename(dev), dev) for dev in usb_devices)

def get_mount_points():
    devices = get_usb_devices()
    output = []
    for dev in devices:
        output = subprocess.check_output(['lsblk', '-lnpo', 'NAME,MOUNTPOINT', '/dev/' + dev]).splitlines()
    return output
        
def get_pi_mount_points(starts_with, devices=None):
    output = check_output(['mount']).splitlines()
    output = [tmp.decode('UTF-8') for tmp in output]
    devices = devices 

    def is_usb(path):
        return any(dev in path for dev in devices)
    usb_info = (line for line in output if is_usb(line.split()[0]))
    return [(info.split()[2], info.split()[0]) for info in usb_info if info.split()[2].startswith(starts_with)]

def is_pen_drive_present():
    return len(get_mount_points()) > 0

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

def get_video_length(filename):
    print(filename)
    output = subprocess.check_output(("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename)).strip()
    video_length = int(float(output))
    print("Video length in seconds: " + str(video_length))
    return video_length
        
def get_video_size(filename):
    output = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", filename], check=True, capture_output=True, text=True).stdout
    width, height = output.split('x')
    return int(width), int(height)
        
def reduce_size(filename, out_filename, width, height):
    print(f'Starting reduction process of file {filename}')
    output = subprocess.run(["ffmpeg", "-i", filename, "-vcodec", "libx264", "-acodec", "copy", "-y", "-vf", f"scale={width}:{height}", "-threads", "4", "-ss", "0", "-t", "200", out_filename], check=True, capture_output=True, text=True).stdout
    print(f'Finished reduction process. Created file {out_filename}')
            
def get_pen_folder():
    folder = None
    if is_raspberry_pi():
        folder = get_pi_pen_folder()
    else:
        if is_pen_drive_present():
            drive_info = get_mount_points()
            info = drive_info[1].split()
            folder = info[1].decode('ascii')
    return folder
                
def have_pen_drive_files(file_type):
    pen_folder = get_pen_folder()
    if pen_folder is None:
        return False
    media_files = get_files(pen_folder, file_type)
    if len(media_files) > 0:
        return True
    return False

def get_average_video_width(video_folder):
    media_files = get_files(video_folder, '.mp4')
    count=0
    total=0
    for file in media_files:
        width, height = get_video_size(file)
        total += width
        count += 1
    return total / count

def reduce_files(dst_folder):
    pen_folder = get_pen_folder()
    media_files = get_files(pen_folder, '.mp4')
    count=0
    for file in media_files:
        length = get_video_length(file)
        width, height = get_video_size(file)
        print(f'file {file}  length: {length}  width {width}  height {height}')
        fname = Path(file).name
        if width > 960:
            reduce_size(file, f'{dst_folder}/{fname}', 960, 540)
        else:
            shutil.copy(file, f'{dst_folder}')
        count += 1

def create_playlist(conf_folder, folder):
    files = get_files(folder, '.mp4')
    with open(conf_folder+"/playlist.m3u", "w") as file:
        # Writing data to a file
        for filename in files:
            #print(f'{file}')
            file.write(filename+'\n')

def create_subtitle_files(folder):
    pen_folder = get_pen_folder()
    srt_files = get_files(pen_folder, '.srt')
    if len(srt_files) > 0:
        for srt_file in srt_files:
            shutil.copy(srt_file, folder)
        return

    # if we get here is because there is no .srt files in the pen drive
    lines = [
        "1",
        "00:00:00,0 --> 00:00:05,000",
        f"This is video # in the list",
        "<font color='red'>When she was the queen of hearts.</font>"
    ]

    # get file names from the "videos" folder
    files = get_files(folder, '.mp4')
    count = 0
    for filename in files:
        srt_file = filename.replace(".mp4", ".srt")
        seq = 0
        with open(srt_file, "w") as file:
            for line in lines:
                if seq == 2:
                    file.write(f'This is video #{count} in the list\n')
                else:
                    file.write(f'{line}\n')
                seq += 1
            print(f"finished creating subtitle file {srt_file}")
            count += 1

def print_files(files):
    print('files to play')
    for file in files:
        print(f'{file}')

def calc_height_proportional(w, h, fixed_w):
    # if original width > fixed_w
    print(f"original img size {w, h, fixed_w}")
    if w > fixed_w:
        factor = 1 - (w - fixed_w) / w
    else:
        factor = fixed_w / w
    print(f"height factor: {factor}")
    return int(h * factor)

def reduce_image_size(filename, outfilename, video_w):
    print(f'Starting reduction process of file {filename}')
    image = Image.open(filename)
    w, h = image.size

    # find display resolution
    #res = pyautogui.size()

    width = video_w
    height = int(calc_height_proportional(w, h, width))

    if video_w > 960:
        divide_factor = int(video_w / 960)
    else:
        divide_factor = 4

    # now we just reduce the size of the logo
    width = int(width / divide_factor)
    height = int(height / divide_factor)
    print(f'resulting size: {width}x{height}')
    new_image = image.resize((width, height))
    new_image.save(outfilename)
    print(f'Finished logo reduction process - case1. Created file {outfilename}')

def process_logo_file(logo_folder, videos_folder):
    pen_folder = get_pen_folder()
    img_files = get_files(pen_folder, '.png')
    print(f"size of img files: {len(img_files)}")
    width = get_average_video_width(videos_folder)
    for file in img_files:
        if file.endswith("logo.png"):
            reduce_image_size(file, f"{logo_folder}/logo.png", width)

def process_pen_drive_files(videos_folder, logo_folder):
    if have_pen_drive_files('.mp4'):
        # delete current files in the conf and videos folder
        purge(videos_folder, ".srt")
        purge(videos_folder, ".mp4")
        reduce_files(videos_folder)
        create_subtitle_files(videos_folder)

    if have_pen_drive_files('logo.png'):
        purge(logo_folder, '.png')
        process_logo_file(logo_folder, videos_folder)

def purge(folder, pattern):
    print(f'in purge, folder {folder}  pattern {pattern}')
    files = get_files(folder, pattern)
    for f in files:
        print(f'removing {f}')
        os.remove(f)

def time_counter(conf_folder):
    print(f"here in time_counter, folder {conf_folder}")
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

def get_time_left_in_minutes(conf_folder):
    spent_file = conf_folder + "/" + TIME_SPENT_FILE
    if not os.path.exists(spent_file):
        file = open(spent_file, 'w')
        file.write("0")
        file.close()

    with open(spent_file) as f:
        minutes = f.read()
        minutes.strip(" ")
        minutes = int(minutes)

    if FREE_TIME_IN_MINUTES > minutes:
        return FREE_TIME_IN_MINUTES - minutes
    else:
        return 0

def get_usb_devices():
    sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))
    usb_devices = (dev for dev in sdb_devices
        if 'usb' in dev.split('/')[5])
    return dict((os.path.basename(dev), dev) for dev in usb_devices)

def get_pi_mount_points(starts_with, devices=None):
    output = check_output(['mount']).splitlines()
    output = [tmp.decode('UTF-8') for tmp in output]
    devices = devices 

    def is_usb(path):
        return any(dev in path for dev in devices)
    usb_info = (line for line in output if is_usb(line.split()[0]))
    return [(info.split()[2], info.split()[0]) for info in usb_info if info.split()[2].startswith(starts_with)]

def get_pi_pen_folder():
    mount_array = get_pi_mount_points("/media/pi", "/media/pi/*")
    if not mount_array:
        print("PI pen drive folder not found")
        return None
    else:
        mount_key, mount_path = mount_array[0]
        return mount_key

def search_and_copy_registration(conf_folder):
    pen_folder = get_pen_folder()
    if pen_folder is not None:
        reg_file = pen_folder + "/" + REGISTRATION_FILE
        if os.path.exists(reg_file):
            print(f"Registration.dat file found: {reg_file} to be copied to {conf_folder}")
            shutil.copy(reg_file, f'{conf_folder}')
        else:
            print(f"Registration.dat not found on the pen drive")

def time_thread():
    print("\here in time_thread")

def main():
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

    # if the folders don't exist, create them
    try:
        if not os.path.exists(conf_folder):
            os.mkdir(conf_folder)
        if not os.path.exists(videos_folder):
            os.mkdir(videos_folder)
        if not os.path.exists(logo_folder):
            os.mkdir(logo_folder)
    except OSError as error:
        print(f'Error {error} creating folders')
        exit(0)

    print(f'conf folder: {conf_folder},  videos folder: {videos_folder},  logo_folder: {logo_folder}')

    if get_pen_folder() is not None:
        if have_pen_drive_files('registration.dat'):
            print("found registration.dat in pen drive")
        else:
            print("no registration.dat found in pen drive")
    else:
        print("pen drive is not inserted.")

    if get_pen_folder() is None:
        if is_raspberry_pi():
            print("It's Raspberry Pi. No pen drive inserted")
        else:
            print("It's not Raspberry Pi. No pen drive inserted")
    else:
        print("here to call search_and_copy_registration()")
        search_and_copy_registration(conf_folder)
        process_pen_drive_files(videos_folder, logo_folder)

    # test presence of registration file
    local_registration = conf_folder + "/" + REGISTRATION_FILE
    if not os.path.exists(local_registration):
        minutes_left = get_time_left_in_minutes(conf_folder)
        display = Display()
        display.print_line(180, "This is an unregistered version of the software.", 80)
        display.print_line(240, f"Minutes left to use in unregistered mode:", 80)
        display.print_line(300, f"{minutes_left}", 80)
        display.print_countdown("Videos will start playing in a moment...", 100, 10)
        display.quit()

    # now create the playlist and play it
    files = get_files(videos_folder, '.mp4')
    print_files(files)
    create_playlist(conf_folder, videos_folder)

    # start video playing thread
    video_player_thread = threading.Thread(target=play_files, args=(conf_folder, videos_folder, logo_folder,))
    video_player_thread.start()

    # start time counting thread
    time_counter_thread = threading.Thread(target=time_counter, args=(conf_folder,))
    time_counter_thread.start()


if __name__ == '__main__':
    main()

