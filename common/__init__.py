from . import TimingUtil
from . import StrUtils
import time
import os
import hashlib
import datetime
import sys

def timing(f):
  return TimingUtil.CTimingUtil.timing_impl(f)

class ParamsError(Exception):
  pass

def mstime() -> int:
  return round(time.time() * 1000)

def microtime():
    unixtime = datetime.datetime.now() - datetime.datetime(1970, 1, 1)
    return unixtime.days*24*60*60 + unixtime.seconds + unixtime.microseconds/1000000.0

def fssync():
  os.system("sync")

def mprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs, flush = True)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs, flush = True)

def mpSeed() -> str:
  return "p%d_%d" % (os.getpid(), mstime())

class HasherFactory:
  @staticmethod
  def createHasher():
    return hashlib.sha512()