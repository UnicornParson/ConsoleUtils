#!/usr/bin/env python3
import tempfile
import argparse
import sys
import enum 
import time
import os
import sqlite3
import hashlib
import json

mstime = lambda: int(round(time.time() * 1000))

class dbEngine:
  connection = None
  cursor = None

  @staticmethod
  def open(path):
    dbEngine.connection = sqlite3.connect(dbPath)
    dbEngine.cursor = dbEngine.connection.cursor()
    dbEngine.makeDb()

  def checkDb():
    if not dbEngine.cursor or not dbEngine.connection:
      raise Exception('dbEngine', 'not opened')

  @staticmethod
  def makeDb():
    dbEngine.checkDb()
    dbEngine.cursor.execute("""
      CREATE TABLE 'files' (
        'path' TEXT NOT NULL UNIQUE,
        'hash'  TEXT NOT NULL,
        'size' INTEGER NOT NULL);
    """)
    dbEngine.cursor.execute("""
      CREATE TABLE 'result' (
      'groupId' TEXT NOT NULL,
      'path'  TEXT NOT NULL,
      'size'  INTEGER NOT NULL);
    """)

    dbEngine.cursor.execute("""CREATE INDEX 'hash_i' ON 'files' ('hash');""")
    dbEngine.connection.commit()

  @staticmethod
  def close():
    dbEngine.cursor = None
    if dbEngine.connection:
      dbEngine.connection.close()
    dbEngine.connection = None

  def notUniqueHashes():
    dbEngine.checkDb()
    rc = []
    for row in dbEngine.cursor.execute("SELECT DISTINCT hash FROM files GROUP BY hash HAVING COUNT(*) > 1"):
      rc.append(row[0])
    return rc

  def filesByHash(hash):
    dbEngine.checkDb()
    rc = []
    for row in dbEngine.cursor.execute("SELECT path, size FROM files  WHERE hash='" + hash + "';"):
      rc.append((row[0], row[1]))
    return rc

  @staticmethod
  def writeFileInfo(path, hash, size):
    dbEngine.checkDb()
    dbEngine.cursor.execute("INSERT INTO files VALUES (?,?,?)", (path, hash, size))
    dbEngine.connection.commit()

  def writeGroupRecord(hash, fname, size):
    dbEngine.checkDb()
    dbEngine.cursor.execute("INSERT INTO result VALUES (?,?,?)", (hash, fname, size))
    dbEngine.connection.commit()


class Logger:
  verbose = False
  quiet = False

  @staticmethod
  def verboseLog(msg):
    if Logger.verbose:
      print(msg)

  @staticmethod
  def log(msg):
    if not Logger.quiet:
      print(msg)

class Formats(enum.Enum):
  json = 0
  stdout = 1
  ##html = 1
  sqlite = 2
  invalid = 3

  @staticmethod
  def parce(value) -> enum.Enum:
      if value == None:
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
##        Formats.html: ".htm",
        Formats.sqlite: ".sqlite"
      }
      if val != Formats.invalid:
        return extentions[val]
      print("invalid format" + val.name)
      return ""
    

def calc(fname):
  md5_object = hashlib.md5()
  block_size = 128 * md5_object.block_size
  a_file = open(fname, 'rb')
  chunk = a_file.read(block_size)
  while chunk:
  	md5_object.update(chunk)
  	chunk = a_file.read(block_size)
  a_file.close()
  return md5_object.hexdigest()

def compareFiles(path1, path2) -> bool:
  Logger.log("compare " + path1 + " -> " + path2)
  if not os.path.isfile(path1) or not os.path.isfile(path2):
    raise Exception('compareFiles', 'not a file')
  if path1 == path2:
    return True
  if os.path.getsize(path1) != os.path.getsize(path2):
    Logger.log("different sizes")
    return False
  f1 = open(path1, 'rb')
  f2 = open(path2, 'rb')
  block_size = 1024
  chunkIndex = 0
  chunk1 = f1.read(block_size)
  chunk2 = f2.read(block_size)
  while chunk1 and chunk2:
    if chunk1 != chunk2:
      Logger.log("different chunk[" + str(chunkIndex) + "]")
      f1.close
      f2.close
      return False
    chunkIndex += 1
    chunk1 = f1.read(block_size)
    chunk2 = f2.read(block_size)
  return True

def readFile(path):
  Logger.verboseLog("read file " + path)
  md5str = calc(path)
  fileSize = os.path.getsize(path)
  Logger.verboseLog("hash: " + md5str + " size: " + str(fileSize))
  dbEngine.writeFileInfo(path, md5str, fileSize)

def readDir(path):
  if os.path.islink(path): 
    Logger.verboseLog("ignore link " + path)
    return
  if os.path.isfile(path):
    readFile(path)
    return
  Logger.verboseLog("read folder " + path)
  for entry in os.listdir(path):
    readDir(path + "/" + entry)

def groupRecords():
  groups = {}
  for hash in dbEngine.notUniqueHashes():
    Logger.verboseLog(hash + " :: " + str(dbEngine.filesByHash(hash)))
    files = dbEngine.filesByHash(hash)
    if len(files) <= 1:
      continue
    groups[hash] = {}
    originalFile = files[0]
    groups[hash]["path"] = originalFile[0]
    groups[hash]["size"] = originalFile[1]
    dbEngine.writeGroupRecord(hash, originalFile[0], originalFile[1])
    for secondFile in files[1:]:
      if compareFiles(originalFile[0], secondFile[0]):
        groups[hash]["path"] = secondFile[0]
        groups[hash]["size"] = secondFile[1]
        dbEngine.writeGroupRecord(hash, secondFile[0], secondFile[1])
  return groups

parser = argparse.ArgumentParser(add_help=True, description="Duplicates detector [Don't repeat yourself!]")
parser.add_argument("-o", "--target", "--out", action="store", default=".", help="output target (default .)")
parser.add_argument("-f", "--format", "--fmt", action="store", default=Formats.sqlite.name, help="output format <json|stdout|sqlite(default)")
parser.add_argument("-v", "--verbose", action="store_true", help="print all messages")
parser.add_argument("-q", "--quiet", action="store_true", help="no output")
parser.add_argument("path", help="folder to scan")
args = parser.parse_args()
dbPath = ":memory:"
fmt = Formats.parce(args.format)
if fmt == Formats.invalid:
    print("invalid format " + args.format)
    parser.print_help(sys.stderr)
    sys.exit(1)

inPath = args.path
if not os.path.isdir(inPath):
    print("input must be a folder")
    parser.print_help(sys.stderr)
    sys.exit(1)

Logger.quiet = args.quiet
Logger.verbose = args.verbose and not Logger.quiet
target = args.target
if not target:
  target = "."
if os.path.isdir(target):
  target += "/duplicatesReport." + str(mstime()) + Formats.ext(fmt)
if fmt == Formats.sqlite and target:
  dbPath = target


Logger.verboseLog("in: " + inPath + " out[" + args.format + "]: " + target)

dbEngine.open(dbPath)
Logger.log("---- indexing stage ----")
readDir(args.path)
Logger.log("---- comparation stage ----")
groups = groupRecords()
groups_json = json.dumps(groups, sort_keys = True, indent = 2, separators = (',', ': '))
if fmt == Formats.json:
  outFile = open(target, 'w')
  outFile.write(groups_json)
  outFile.close()
elif fmt == Formats.stdout:
  print(groups_json)
else:
  print("database saved to " + dbPath)
Logger.log("---- done ----")
dbEngine.close()