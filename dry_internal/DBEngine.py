import sqlite3

class DBEngine:
	StorageSqlite = "sqlite"
	StoragePG = "pg"

	def open(self, path: str):
		pass
	def checkDb(self):
		pass
	def makeDb(self):
		pass
	def notUniqueHashes(self):
		pass
	def filesByHash(self, hash: str):
		pass
	def writeFileInfo(self, path: str, hash: str, size: int):
		pass
	def writeGroupRecord(self, hash: str, fname: str, size: int):
		pass

class PgPath:
	def __init__(self) -> None:
		self.host = ""
		self.user = ""
		self.password = ""
		self.dbname = ""
	def filled(self)->bool:
		return bool(self.host) and bool(self.user) and bool(self.dbname)

class PGEngine(DBEngine):
	def open(self, path: PgPath):
		pass
	def checkDb(self):
		pass
	def makeDb(self):
		pass
	def notUniqueHashes(self):
		pass
	def filesByHash(self, hash: str):
		pass
	def writeFileInfo(self, path: str, hash: str, size: int):
		pass
	def writeGroupRecord(self, hash: str, fname: str, size: int):
		pass

class SqliteEngine(DBEngine):
	def __init__(self):
		self.connection = None
		self.cursor = None
		self.path = ""

	def open(self, path:str):
		self.path = path
		self.connection = sqlite3.connect(path)
		self.cursor = self.connection.cursor()
		self.makeDb()

	def checkDb(self):
		if not self.cursor or not self.connection:
			raise Exception('dbEngine', 'not opened')

	def makeDb(self):
		self.checkDb()
		self.cursor.execute("""
			CREATE TABLE 'files' (
				'path' TEXT NOT NULL UNIQUE,
				'hash'  TEXT NOT NULL,
				'size' INTEGER NOT NULL);
		""")
		self.cursor.execute("""
			CREATE TABLE 'result' (
			'groupId' TEXT NOT NULL,
			'path'  TEXT NOT NULL,
			'size'  INTEGER NOT NULL);
		""")

		self.cursor.execute("""CREATE INDEX 'hash_i' ON 'files' ('hash');""")
		self.connection.commit()

	def close(self):
		self.cursor = None
		if self.connection:
			self.connection.close()
		self.connection = None

	def notUniqueHashes(self):
		self.checkDb()
		rc = []
		for row in self.cursor.execute("SELECT DISTINCT hash FROM files GROUP BY hash HAVING COUNT(*) > 1"):
			rc.append(row[0])
		return rc

	def filesByHash(self, hash: str):
		self.checkDb()
		rc = []
		for row in self.cursor.execute("SELECT path, size FROM files  WHERE hash='" + hash + "';"):
			rc.append((row[0], row[1]))
		return rc

	def writeFileInfo(self, path: str, hash: str, size: int):
		self.checkDb()
		self.cursor.execute("INSERT INTO files VALUES (?,?,?)", (path, hash, size))
		self.connection.commit()

	def writeGroupRecord(self, hash: str, fname: str, size: int):
		self.checkDb()
		self.cursor.execute("INSERT INTO result VALUES (?,?,?)", (hash, fname, size))
		self.connection.commit()

def makeEngine(type: str) -> DBEngine:
	if type.lower() == DBEngine.StoragePG:
		return PGEngine()
	elif type.lower() == DBEngine.StorageSqlite:
		return SqliteEngine()
	raise ValueError("no %s storage" % type)