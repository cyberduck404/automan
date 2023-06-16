#
#
#
import requests
from threading import Thread


def run(filename):
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip('\r').strip('\n')
            platform, program, subdomain = line.split()