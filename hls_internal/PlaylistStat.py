import asyncio

class PlaylistStat:
	def __init__(self) -> None:
		self.variant = False
		self.url = ""
		self.bandwidth = 0
		self.invalid = False
		self.invalidReason = ""
		self.seq = 0
		self.duration = 0
	
	def toDict(self) -> dict:
		d = {}
		d["variant"] = self.variant
		d["url"] = self.url
		d["bandwidth"] = self.bandwidth
		d["invalid"] = self.invalid
		d["invalidReason"] = self.invalidReason
		d["seq"] = self.seq
		d["duration"] = self.duration
		return d
	
	def toTuple(self) -> tuple:
		return 	(
			self.url,
			self.variant,
			self.bandwidth,
			self.invalid,
			self.invalidReason,
			self.seq,
			self.duration )

class StatWriter:
	def __init__(self) -> None:
		pass
	
	async def write(self, stat: PlaylistStat) -> bool:
		return True

	async def close(self):
		pass

class StatPrinter(StatWriter):
	async def write(self, stat: PlaylistStat) -> bool:
		print(stat.toDict())
		return True