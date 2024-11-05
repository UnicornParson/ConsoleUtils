import common
from bs4 import BeautifulSoup as bs
from operator import itemgetter

class HTMLGenerator:
	def __init__(self):
		self.footer = """
			</body>
			</html>
		"""
	def makeHeader(self, title) -> str:
		return """
			<!DOCTYPE html>
			<html>
			<head>
					<title>""" + title + """</title>
					<link href="data:image/x-icon;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACf0lEQVQ4jX2TXUjTYRTGf/+5zA+GOhM/lp+gWU5xhUQRwSRIoaCMwsSyEOqmm+qiJCJQociCLgJvwiAqoYgoCLwR6UJLM0tUTKjNKRPdnCun2NK9p4v/JlriAy/Py8t7Hp7nHI52v8MphWnxAIgIiCAiiCj9rgREEQqFGJvwNTacLrvFWrwb9MhiUEng9+Zn2uOTMdesXGjpqF5bbwRQAiGlP3Rl5bERdnR3kmVJ5dJx2+PA/CtHe9OJPl1A1n+0Tzg2FJhyTzI948ViToqpOljwuh0sAEYRXeHLkFPn4XEAbNYcbMW5tLV3ARAMBjlWYcO/8IflFZXh9issSQaMhAVsxbnrOILz1XZEwjEFojQwGGZWI2/qoNSqOxBABGpP2sEACfFbefa5MQcYN/BvE8KIFK3lkOijNqfP0+/tHim9k1ejve13i92avmqJSMEa20rpDMJMYJhHo3dJzkykr/fTihH1fwQRsBXnYLNm0/b8PUqBpsGhwyk8HGnCnGFidOyb8szM1hsiPVi1DWxLNpFqEVp7blNpLyQjLYmy/bE8GLxJXPIWnN9d/BhzXvx63fFEe/PRJeWlmayEwrYRvAsOno60kpKeiHdinqpdtdzrv4EpJRaPe5aEqX1cPdWslWyP0qcgAgNDTgRwTXrJL4jhjwSZw8uvJB8tg9eIM8XhnfRRnlFHQow1Mn0MhAUi3fb9XKS3z0eFuZ5p5xxLi0tEE43P7edA2hkqd57Vlywc26iUQtNgtzUXJVBSlItSIAgN2S00d17B75+jPL+GI0V1RBvDWxsRGHZ4UMsrCIIK6WssKnxEOJp2mRcTLzEH9tDzYQCUYnjUxbmqvQD8BfgNemkN6Z12AAAAAElFTkSuQmCC" rel="icon" type="image/x-icon" />
					<meta charset="UTF-8">
					<style>
							body {
								background-color: #fff;
								margin: 4px;
								padding: 0px;
								font-family: monospace;
							}
							.TitleBox {
								color:rgb(121, 121, 138);
								font-size: 24px;
								border: 0;
								border-left: 16px solid #ffbf00;
								border-bottom: 1px solid #ffbf00;
								padding: 8px;
								border-radius: 5px;
							}
							table {
								width: 100%
							}
							td {
								border: 1px solid rgb(174, 174, 177);
								border-radius: 5px;
								color: #330;
								margin-left: 16px;
							}
							.tableHeaderCell {
								color: #000;
								background-color: rgb(110 110 111 / 23%);
								text-align: center;
							}
							.tableHeader {
								width: 70%;
								border: 1px solid #ffbf00;
								border-left: 16px solid #ffbf00;
								margin-top: 6px; 
								margin-right: 15%;
								margin-bottom: 2px;
								margin-left: 15%;
								border-radius: 5px;
								margin-top: 16px;
								padding-left: 16px;
							}
							hr {
								margin-top: 6px;
								margin-left: 20%;
								margin-right: 20%;
								padding: 0;
								height: 10px;
								border: none;
								border-top: 1px solid #ffbf00;
								box-shadow: 0 10px 10px -10px #ffbf00 inset;
							}
							pre {
								background-color: #263238;
								color: #CCFF90;
								margin: 6px;
								padding: 16px;
								border-radius: 6px;
							}
							pre::selection {
								background-color: #CCFF90;
								color: #263238;
							}
							.nodupLine {
								font-size: 24px;
								color: white;
								text-decoration: none;
								padding: .8em 1em calc(.8em + 3px);
								border-radius: 3px;
								background: rgb(64,199,129);
								box-shadow: 0 -3px rgb(53 167 110) inset;
								transition: 0.2s;
							}
					</style>
			</head>
			<body>
			<div class='TitleBox'>""" + title + """</div>"""

	def makeSection(self, hash, size, files) -> str:
		count = len(files)
		text = "<div class='tableHeader'>%s. count: <b>%d</b>. total size: <b>%s</b></div>" % (hash, count, common.StrUtils.convert_bytes(size * count))
		text += "<table><tr><td class='tableHeaderCell'>Path</td><td class='tableHeaderCell'>Size</td></tr>"
		for path in files:
			text += "<tr><td>%s</td><td>%s</td></tr>" % (common.StrUtils.readablePath(path), common.StrUtils.convert_bytes(size))
		text += "</table>" + self.footer
		return text

	def makeRmSection(self, sectionslist) -> str:
		text = "<br><div class='tableHeader'>Remove duplicates shell command</span><pre>\n#!/bin/bash\n\n"
		for entry in sectionslist:
			for fname in entry["path"][1:]:
				text += "rm -v \"%s\"\n" % fname
		if not sectionslist:
			text += "# no duplicartes\n"
		text += "\necho \"done!\"\n</pre><br>"
		return text
			

	def generate(self, group, baseFolder) -> str:
		htmltext = self.makeHeader(f"Duplicates report in {baseFolder}")
		if group:
			for h in group.keys():
				group[h]["h"] = h
				group[h]["summ"] = len(group[h]["path"]) * group[h]["size"]
				
			sortedData = sorted(group.values(), key=itemgetter("summ"), reverse=True)
			for entry in sortedData:
				htmltext += self.makeSection(entry["h"], entry["size"], entry["path"])
			htmltext += self.makeRmSection(sortedData)
		else: # nodup
			htmltext += f"<div class='nodupLine'>No duplicates in {baseFolder}</div>"
		htmltext += self.footer
		soup = bs(htmltext, 'html.parser')
		return soup.prettify()

