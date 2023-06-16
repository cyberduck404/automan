#! /usr/bin/python3
# Description:
#       iterate specified attack script on subs.txt
#  Usage:
import os


subs_file = 'assets/subs.txt'
script_dir = 'attacks'


def list_scripts():
    return os.listdir(script_dir)

def attack(srt):
    srt_path = f'{script_dir}.{srt}'
    __import__(srt_path).run(subs_file)


def attacks():
    for fn in list_scripts():
        srt = fn.split('.')[0]
        if srt == '__pycache__':
            continue
        __import__(f'{script_dir}.{srt}')


if __name__ == '__main__':
    _data = get_subs()
    attack('bypass_403')
