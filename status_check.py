#!/usr/bin/python3
import os
import random
import string
import requests
from threading import Thread, Lock
from config import PROXIES, HEADERS
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


subs_dot_txt = 'assets/subs.txt'
subs_dot_tmp = f'/tmp/automan_{"".join([random.choice(string.hexdigits) for i in range(16)]).lower()}.tmp'

lock = Lock()
def touch(platform, program, subdomain):
    try:
        r1 = requests.get(f'http://{subdomain}', proxies=PROXIES, headers=HEADERS, timeout=5, allow_redirects=False, verify=False)
        c1 = r1.status_code
    except requests.exceptions.RequestException as e:
        c1 = 0
    try:
        r2 = requests.get(f'https://{subdomain}', proxies=PROXIES, headers=HEADERS, timeout=5, allow_redirects=False, verify=False)
        c2 = r2.status_code
    except requests.exceptions.RequestException as e:
        c2 = 0
    lock.acquire()
    with open(subs_dot_tmp, 'a') as f:
        f.write(f'{platform} {program} {subdomain} [{c1}|{c2}]\n')
    lock.release()

def check():
    ts = []
    with open(subs_dot_txt, 'r') as f:
        for line in f.readlines():
            platform, program, subdomain = line.strip('\r').strip('\n').split()
            ts.append(Thread(target=touch, args=(platform, program, subdomain)))
    print(f'[*] Threading')
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    print(f'[*] Move {subs_dot_tmp} to {subs_dot_txt}')
    os.system(f'mv {subs_dot_tmp} {subs_dot_txt}')


if __name__ == '__main__':
    check()