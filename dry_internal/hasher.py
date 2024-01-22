from PIL import Image
import imagehash
from videohash import VideoHash
import os
import glob
import sys
import subprocess
import time
import hashlib
import datetime

class VideoHasher:
	def __init__(self, fname:str):
		self.fname = fname
