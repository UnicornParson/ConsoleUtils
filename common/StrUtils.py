from pathlib import *

def convert_bytes(num) -> str:
    for x in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "0B"

def msToHours(num) -> str:
    ms = num % 1000
    s = (num // 1000) % 60
    m = (num // 60000)  % 60
    h = num // (60 * 60 * 1000)
    return f"{h}h {m}m {s}s {ms:03}ms"

def readablePath(path) -> str:
    return str(PurePath(path))

def secondsToHours(num) -> str:
    s = num % 60
    m = (num // 60)  % 60
    h = num // 3600
    return f"{h}h {m}m {s}s"
