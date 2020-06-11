#!/usr/bin/python3

import platform
import random
import imghdr
import argparse
import configparser
import subprocess
from pathlib import Path
from datetime import date

def parse_args():
    parser = argparse.ArgumentParser(description="Wallpaper Changer")
    parser.add_argument("-d", "--dryrun", action='store_true',
            help="Don't change wallpaper, just print out what would happen")
    parser.add_argument("imgdir", metavar="IMAGE_DIRECTORY",
            help="The directory where wallpaper images are stored")
    
    args = parser.parse_args()
    return args

def get_image_file_list(path):
    res = path.glob('*.*')
    return [p for p in res if imghdr.what(p) is not None]

def set_wallpaper(filename):
    if platform.system() == 'Linux':
        subprocess.run(['gsettings', 'set', 'org.cinnamon.desktop.background',
            'picture-uri', 'file://{}'.format(filename)])
        subprocess.run(['gsettings', 'set', 'org.cinnamon.desktop.background',
            'picture-options', 'scaled'])
    
if __name__ == '__main__':
    args = parse_args()

    today = date.today()

    # will hold the path to the wallpaper
    wallpaper_path = None

    # set the image path
    # if it does not exist, then run now!
    image_path = Path(args.imgdir)
    if not image_path.exists() or not image_path.is_dir():
        print('ERROR: "{}" does not exist or is not a directory!'.format(args.imgdir))
        exit(1)

    # set the working directory to the one specified on the command line 
    # os.chdir(args.imgdir)

    # if a config file exists, let's read it to see what file to change
    # if no file exists, then create one with all the images in the dir
    config_path = image_path.joinpath(image_path.name + '.ini')
    config = configparser.ConfigParser()

    if config_path.exists():
        config.read_file(config_path.open('r'))
        if config.has_section('files'):
            # look for the first file in the configuration that does not have 
            # a date assigned. Use that one.
            # If all the files have a date, then we are going to regenerate
            #   the list
            for filename, dateused in config.items('files'):
                try:
                    use_file = date.fromisoformat(dateused) == today
                except ValueError:
                    use_file = True

                if use_file:
                    p = image_path.joinpath(filename)
                    if imghdr.what(p) is not None:
                        wallpaper_path = p
                        break

    # if there is no wallpaper specified, then we either could not read the 
    # config file, it doesn't exist, or all of the wallpapers in the directory
    # have been in used. In all cases, we will just regenerate the file list
    if wallpaper_path is None:
        # remove all of the files from the config (just remove the section)
        config.remove_section('files')

        # now add it back in
        config.add_section('files')

        # regenerate the file list 
        file_list = get_image_file_list(image_path)
        if len(file_list) > 0:
            # randomize the list
            random.seed()
            random.shuffle(file_list)

            # add each file to the config
            for p in file_list:
                config.set('files', p.name, '')

            # the wallpaper is the first file in the list
            wallpaper_path = file_list[0]

    # now, we should have a wallpaper file (or none were found in the directory)
    if wallpaper_path is not None:
        config.set('files', wallpaper_path.name, today.isoformat())
        print('Setting wallpaper to ' + str(wallpaper_path.resolve()))
        set_wallpaper(str(wallpaper_path.resolve()))

    # write the config file
    config.write(config_path.open('w'))

