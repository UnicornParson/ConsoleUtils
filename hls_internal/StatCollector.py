import m3u8
import asyncio
import traceback
from urllib.parse import urlparse
from .PlaylistStat import *

def isAbsoluteUrl(url) -> bool:
	return bool(urlparse(url).netloc)

def urlBase(u) -> str:
	return (u[:u.rfind('/')] + "/")

def urlTail(u)->str:
	return u[u.rfind('/'):]

class StatCollector:
	def __init__(self) -> None:
		self.statWriter = None

	def setup(self, statWriter) -> bool:
		if not statWriter:
			raise ValueError("invalid writer")
		self.statWriter = statWriter
		return True

	async def processUrl(self, url: str) -> bool:
		if not self.statWriter:
			raise ValueError("run before setup")
		ret  = True
		stats = await self.getPlaylistStat(url)
		for s in stats:
			ret &= not s.invalid
			writeRc = await self.statWriter.write(s)
			if not writeRc:
				print("cannot write to writer")
		return ret


	async def getPlaylistStat(self, url: str):
		if not self.statWriter:
			raise ValueError("run before setup")
		print("getPlaylistStat ", url)
		stat = PlaylistStat()
		stat.url = url
		stat.bandwidth = 0
		try:
			playlist = m3u8.load(url)
		except Exception as e:
			stat.invalid = True
			stat.invalidReason = str(e)
			return [stat]
		rc = []
		stat.variant = playlist.is_variant
		if playlist.is_variant:
			for sub in playlist.playlists:
				print("download ", sub.uri, " with bandwidth ", sub.stream_info.bandwidth)
				newuri = sub.uri
				if not isAbsoluteUrl(sub.uri):
					base = urlBase(url)
					newuri = base + sub.uri
				l = await self.getPlaylistStat(newuri)
				if l == None:
					raise ValueError("unexpected stat list")
				for item in l:
					if item == None:
						raise ValueError("unexpected stat item")
					item.bandwidth = sub.stream_info.bandwidth
					rc.append(item)
					stat.duration += item.duration
			rc.append(stat)
		else:
			stat.duration = playlist.target_duration
			stat.seq = playlist.media_sequence
			rc.append(stat)
		return rc