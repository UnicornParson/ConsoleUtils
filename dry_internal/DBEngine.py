import sqlite3
import psycopg2

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
	def close(self):
		pass
	def cleanup(self):
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
	ProduccerId = None
	SessionId = None

	@staticmethod
	def makeNodeKeys(produccer: int, session: int):
		PGEngine.ProduccerId = produccer
		PGEngine.SessionId = session


	def __init__(self):
		self.connection = None
		self.cursor = None
		self.path = ""

	def open(self, path: PgPath):
		if not path.filled():
			raise ValueError("Invalig pgconfig")
		self.path = path
		self.connection = psycopg2.connect(dbname=path.dbname, user=path.user, password=path.password, host=path.host, port="5432")
		if not self.connection:
			raise ConnectionError("cannot connect to %s:%s" % (path.host, path.dbname))
		self.cursor = self.connection.cursor()
		self.makeDb()
	
	def close(self):
		self.cursor = None
		if self.connection:
			self.connection.close()
		self.connection = None

	def execOne(self, q, args):
		self.checkDb()
		try:
			self.cursor.execute(q, args)
		except Exception as e:
			print(e, " in ", q)
	

	def checkDb(self):
		if not self.cursor or not self.connection:
			raise Exception('dbEngine', 'not opened')
		if not PGEngine.ProduccerId:
			raise ValueError("Invalig ProduccerId")
		if not PGEngine.SessionId:
			raise ValueError("Invalig SessionId")

	def makeDb(self):
		try:
			print("use db user ",self.path.user)
			self.cursor.execute("""
				CREATE TABLE IF NOT EXISTS public.hashes
				(
					id bigserial NOT NULL,
					producer_id integer NOT NULL,
					session_id bigint NOT NULL,
					path character varying(512) COLLATE pg_catalog."default" NOT NULL,
					hash character varying(256) COLLATE pg_catalog."default" NOT NULL,
					size bigint NOT NULL,
					frags jsonb,
					CONSTRAINT hashes_pkey PRIMARY KEY (id)
				)
			""")
			self.cursor.execute("ALTER TABLE IF EXISTS public.hashes OWNER TO %s;" % self.path.user)
			self.cursor.execute("""
				CREATE TABLE IF NOT EXISTS public.results
				(
					id bigserial NOT NULL,
					session_id bigint NOT NULL,
					groupId character varying(256) NOT NULL,
					path character varying(512) NOT NULL,
					size bigint NOT NULL,
					PRIMARY KEY (id)
				);
			""")
			self.cursor.execute("ALTER TABLE IF EXISTS public.results OWNER TO %s;" % self.path.user)
			self.cursor.execute("CREATE OR REPLACE VIEW public.sessions AS SELECT DISTINCT session_id as sid FROM public.hashes order by session_id;")
			self.cursor.execute("ALTER TABLE public.sessions OWNER TO %s;" % self.path.user)

		except Exception as e:
			print(e, " in ",self.cursor.query)

		self.connection.commit()
		print("create db OK")

	def notUniqueHashes(self):
		self.checkDb()
		rc = []
		self.execOne("SELECT DISTINCT hash FROM public.hashes WHERE session_id=%s GROUP BY hash HAVING COUNT(*) > 1", (PGEngine.SessionId,))
		try:
			qrc = self.cursor.fetchall()
		except psycopg2.ProgrammingError:
			qrc = []
		for row in qrc:
			rc.append(row[0])
		return rc

	def filesByHash(self, hash: str):
		self.checkDb()
		rc = []
		self.execOne("SELECT path, size FROM public.hashes  WHERE hash=%s and session_id=%s", (hash,PGEngine.SessionId))
		try:
			qrc = self.cursor.fetchall()
		except psycopg2.ProgrammingError:
			qrc = []
		for row in qrc:
			rc.append((row[0], row[1]))
		return rc
	def writeFileInfo(self, path: str, hash: str, size: int):
		self.execOne("INSERT INTO public.hashes(producer_id, path, hash, size, session_id) VALUES (%s, %s, %s, %s, %s)", (PGEngine.ProduccerId, path, hash, size, PGEngine.SessionId))
		self.connection.commit()
		
	def writeGroupRecord(self, hash: str, fname: str, size: int):
		self.execOne("INSERT INTO public.results(session_id, groupId, path, size) VALUES (%s, %s, %s, %s)", (PGEngine.SessionId, hash, fname, size))
		self.connection.commit()

	def cleanup(self):
		self.execOne("DELETE FROM public.hashes WHERE session_id = %s", (PGEngine.SessionId,))
		self.connection.commit()

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
