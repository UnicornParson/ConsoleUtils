# ConsoleUtils
useful console scripts

## dry
search for a duplicate files (content based comparation)
required python 3.5 or newer
### Features:
- hash-based comparation
- archives scan (no recursive)
- html/json/sqlite/plain reports

```
usage: dry [-h] [-o TARGET] [-f FORMAT] [-v] [-q] [-c] [--tmp TMP]
           [--archlimit ARCHLIMIT] [--noarchive] [--progress] [--noprescan]
           path

Duplicates detector [Don't repeat yourself!]

positional arguments:
  path                  folder to scan

optional arguments:
  -h, --help            show this help message and exit
  -o TARGET, --target TARGET, --out TARGET
                        output target (default .)
  -f FORMAT, --format FORMAT, --fmt FORMAT
                        output format <json|stdout|html|sqlite(default)
  -v, --verbose         print all messages
  -q, --quiet           no output
  -c, --compare         content based comparation (hash based is default)
  --tmp TMP             tmp folder. default: current. WARNING! script will
                        extract archives to this folder
  --archlimit ARCHLIMIT
                        don't open archives that large than this limit (in
                        Mb). 0 - no limit (default)
  --noarchive           don't open archives, process as usual files
  --progress            print progress line
  --noprescan           skip prescan step (calculate summary counts for
                        progress displayed.) it can take a long time on large
                        folders
```
### required python3 packages:
 - BeautifulSoup
 - reprint

### 3rd-party:
patool from https://wummel.github.io/patool/

### Brokern windows / Todo:
- multiprocessing version in progress. 
  temporary results in dryMP file


## csvmerger
merge some scv files into one
required python 3.5 or newer

```
usage: csvmerger [-h] [-H] file [file ...]

Merge some csv file into one

positional arguments:
  file           list of input files

optional arguments:
  -h, --help     show this help message and exit
  -H, --headers  files has headers
```

## ScreenshotUtil
Console util to make a screenshot

## HLS
HLS utils

## FROZEN
frozen frames detector
* hignlights changed pixels in video
* prints sibling frames difference coefficient

## kafkaSnatch
dumps kafka topic to txt file
requirements can be found in **kafkaSnatch_req.txt**
```
usage: kafkaSnatch broker_addr topic_name
example: kafkaSnatch 127.0.0.1:12345 my_topic
```