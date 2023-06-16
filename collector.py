#! /usr/bin/python3
# Description:
#       assets collector, accept parameter
#  Usage:
#       python3 collector.py -d domain.com
#       python3 collector.py -f wildcards.tmp
import os
import re
import string
import sys
import time
import argparse
import subprocess
import random


config_amass = 'configs/amass.config.ini'  # todo
config_resolver = 'configs/resolvers.txt'
output_dir = f"assets"
os.environ['PATH'] += f":{os.path.expanduser('~')}/go/bin"
output = f'/tmp/automan_{"".join([random.choice(string.hexdigits) for i in range(16)]).lower()}.tmp'


def init():
    os.system(f'rm -f {output_dir}/*.tmp')

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('-d', '--domain', type=str, help='Specify domain(s), split by comma, Ex: att.com,google.com')
    p.add_argument('-pf', '--platform', type=str, default='hackerone', help='Specify platform which program belong to')  # todo://group
    p.add_argument('-pg', '--program',  type=str, help='Specify program name')
    p.add_argument('-oos', '--out_of_scope', type=str, help='Specify out-of-scope, Ex: a1.com,a2.com')
    p.add_argument('-f', '--domainFile', type=str, help='Specify domain file which formatted with <platform> <handle> <wildcard> [<out-of-scope1>,<o2>,<o3>]')
    args = p.parse_args()
    ctx = {}
    if args.domain:  # Single program mode
        in_scopes = args.domain.split(',')
        out_of_scopes = args.ouf_of_scope.split(',')
        platform, program = args.platform, args.program
        ctx = {
            platform: {
                program: {
                    'in-scope': in_scopes,
                    'out-of-scope': out_of_scopes
                }
            }
        }
    else:
        df = args.domainFile
        if os.path.exists(df):
            with open(df, 'r') as f:
                for line in f.readlines():
                    if line.startswith('#'):
                        continue
                    line = line.strip('\r').strip('\n')
                    # hackerone khealth khealth.com [oos1,oos2,oos3]
                    data = line.split(' ')
                    if len(data) == 3:
                        platform, program, domain = data
                        ooss = []
                    elif len(data) == 4:
                        platform, program, domain, out_of_scopes = data
                        ooss = out_of_scopes.strip('[').strip(']').split(',')
                    if not ctx.get(platform):
                        ctx[platform] = {}
                    if not ctx[platform].get(program):
                        ctx[platform][program] = {
                            'in-scope': [],
                            'out-of-scope': []
                        }
                    ctx[platform][program]['in-scope'].append(domain)
                    for i in ooss:
                        if i:
                            ctx[platform][program]['out-of-scope'].append(i)
                    ctx[platform][program]['out-of-scope'] = list(set(ctx[platform][program]['out-of-scope']))
        else:
            print(f"[!] No exist domain file, exit.")
            sys.exit(0)
    return ctx

def execute(cmd, platform, program, domain):
    start = time.time()
    print(f"[{platform} - {program} - {domain}] {cmd}")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    lines = []
    for line in iter(p.stdout.readline, b''):
        line = line.strip().decode('GB2312')
        print(line)
        lines.append(line)
    print(f"[{platform} - {program} - {domain}] Cost {int(time.time() - start)}s")

def collect(platform, program, domain, out_of_scopes):
    output_tmp = f'/tmp/automan_{"".join([random.choice(string.hexdigits) for i in range(16)]).lower()}.tmp'
    cmds = []
    cmds.append(f"amass enum -d {domain} -passive -norecursive | sed 's/^/{platform} {program} /g' >> {output_tmp}")
    if os.path.exists(config_resolver):
        cmds.append(f"subfinder -silent -d {domain} | shuffledns -silent -d {domain} -r {config_resolver} | sed 's/^/{platform} {program} /g' >> {output_tmp}")
    # todo://add more cmds
    for cmd in cmds:
        execute(cmd, platform, program, domain)
    # out-of-scope
    lst = []
    with open(output_tmp, 'r') as f:
        for line in f.readlines():
            found = False
            line = line.strip('\r').strip('\n')
            for out_of_scope in out_of_scopes:
                if out_of_scope in line:
                    found = True
                    break
            if found:
                continue
            lst.append(line)
    with open(output, 'w') as f:
        for line in lst:
            f.write(line+'\n')
    # sort & merge
    os.system(f'cat {output_dir}/subs.txt {output} 2>/dev/null | sort -u > {output_dir}/subs.tmp; mv {output_dir}/subs.tmp {output_dir}/subs.txt')

if __name__ == '__main__':
    data = parse_args()
    for _platform, values in data.items():
        for _program in values.keys():
            detail = data[_platform][_program]
            _in_scope = detail['in-scope']
            _out_of_scopes = detail['out-of-scope']
            for _domain in _in_scope:
                collect(_platform, _program, _domain, _out_of_scopes)