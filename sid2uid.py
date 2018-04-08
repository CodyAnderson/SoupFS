#!/usr/bin/python
#
# Convert windows sid to centrify express generated uid
#  http://community.centrify.com/t5/DirectControl-Express-for-UNIX/RE-Evaluating-Centrify-Express-Now-And-Have-Some-Questions/td-p/3174
import argparse
import re

def sid(value):
    sidrx = re.compile('^S-1-5-\d{2}-\d+-(\d{4,10})-\d+-(\d+)$')
    m = sidrx.match(value)
    if (m):
        # uid is the last 9 bits of the sid combined with 22, 0 padded from rid
        (sid,rid) = m.group(1,2)
        sidbits = ('{0:b}'.format(int(sid)))[-9:]
        uidbits = '{0:022b}'.format(int(rid))
        return int(sidbits+uidbits,2)
    else:
        msg = "'%r' is not a valid sid" % value
        raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser(description='Convert Windows SID to unix ID for centrify')
parser.add_argument('sid',metavar='S',type=sid,nargs="+",help="list of account sid's")
args = parser.parse_args()
for uid in args.sid:
    print uid