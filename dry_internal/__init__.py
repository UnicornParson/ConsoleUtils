import enum
import sys
import os

#import common utils
internalbindir = os.path.dirname(os.path.abspath(__file__))
patoolPath = internalbindir + "/../common"
sys.path.append(patoolPath)
import common

#########################################################################################################
class Stats:
	def __init__(self):
		self.totalCount = 0
		self.totalSize = 0
		self.startTime = common.mstime()
		self.filesCount = 0
		self.filesSize = 0
#########################################################################################################
class Formats(enum.Enum):
	json = 0
	stdout = 1
	html = 2
	sqlite = 3
	invalid = 4

	@staticmethod
	def parse(value) -> enum.Enum:
			if not value:
				return Formats.invalid
			for m, mm in Formats.__members__.items():
				if m == value.lower():
					return mm
			return Formats.invalid

	@staticmethod
	def ext(val) -> str:
			extentions = {
				Formats.json: ".json",
				Formats.stdout: ".txt",
				Formats.html: ".htm",
				Formats.sqlite: ".sqlite"
			}
			if val != Formats.invalid:
				return extentions[val]
			print(f"invalid format {val.name}")
			return ""
#########################################################################################################
