import os
import hashlib

def hashFile(fname: str, onProgressStr = None):
    hasher = hashlib.sha512()
    block_size = 128 * hasher.block_size
    with open(fname, 'rb') as a_file:
        chunk = a_file.read(block_size)
        processedSize = block_size
        fSize = os.path.getsize(fname)
        if fSize <= 0:
            return hasher.hexdigest()
        while chunk:
            prc = (processedSize / fSize) * 100.0
            if onProgressStr:
                onProgressStr("process file %s %0.3f%%" % (fname, prc))
            hasher.update(chunk)
            del chunk
            chunk = a_file.read(block_size)
            processedSize += block_size

    return hasher.hexdigest()

class VideoHasher:
    def __init__(self, fname:str):
        self.fname = fname
