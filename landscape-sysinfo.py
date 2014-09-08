#!/usr/bin/python
#
# landscape-sysinfo-mini.py -- a trivial re-implementation of the 
# sysinfo printout shown on debian at boot time. No twisted, no reactor, just /proc & utmp
#
# (C) 2014 jw@owncloud.com
#
# inspired by ubuntu 14.10 /etc/update-motd.d/50-landscape-sysinfo
# Requires: python-utmp 
# for counting users.
#
# 2014-09-07 V1.0 jw, 
#		ad hoc writeup, feature-complete. Probably buggy?
#

import sys,os,time,posix,glob,utmp

_version_ = '1.1'

def dev_addr(device):
  """ find the local ip address on the given device """
  for l in os.popen('ip route list dev '+device):
    seen=''
    for a in l.split():
      if seen == 'src': return a
      seen = a
  return None

def default_dev():
  """ find the device where our default route is """
  for l in open('/proc/net/route').readlines():
    a = l.split()
    if a[1] == '00000000':
      return a[0]
  return None

def utmp_count():
  u = utmp.UtmpRecord()
  users = 0
  for i in u:
    if i.ut_type == utmp.USER_PROCESS: users += 1
  return users

def proc_meminfo():
  items = {}
  for l in open('/proc/meminfo').readlines():
    a = l.split()
    items[a[0]] = int(a[1])
  print items['MemTotal:'], items['MemFree:'], items['SwapTotal:'], items['SwapFree:']
  return items

loadav = float(open("/proc/loadavg").read().split()[1])
processes = len(glob.glob('/proc/[0-9]*'))
statfs = os.statvfs('/')
rootperc = 100-100.*statfs.f_bavail/statfs.f_blocks
rootgb = statfs.f_bsize*statfs.f_blocks/1024./1024/1024
rootusage = "%.1f%% of %.2fGB" % (rootperc, rootgb)
defaultdev = default_dev()
ipaddr = dev_addr(defaultdev)
users = utmp_count()
meminfo = proc_meminfo()
memperc = "%d%%" % (100-100.*meminfo['MemFree:']/(meminfo['MemTotal:'] or 1))
swapperc = "%d%%" % (100-100.*meminfo['SwapFree:']/(meminfo['SwapTotal:'] or 1))

if meminfo['SwapTotal:'] == 0: swapperc = '---'

print "  System information as of %s\n" % time.asctime()
print "  System load:  %-5.2f                Processes:           %d" % (loadav, processes)
print "  Usage of /:   %-20s Users logged in:     %d"% (rootusage, users)
print "  Memory usage: %-4s                 IP address for %s: %s" % (memperc, defaultdev, ipaddr)
print "  Swap usage:   %s" % (swapperc)

sys.exit(0)
