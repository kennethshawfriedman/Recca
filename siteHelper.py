import os
import subprocess
import string

COLOR = "rgb(252, 102, 33)"

#The most fundamental call
#OUTPUT: "<tag>content</tag>"
def tag(tag, content):
	result = "<"+str(tag)+">"
	for x in content.splitlines():
		result += "\n\t"+x
	result += "\n</"+str(tag)+">\n"
	return result

#general value tags
#OUTPUT: "<tag values[0]='values[1]'>content</tag>"
def tagWithValues(tag, content, *values):
	fullTag = "<" + tag
	for i in xrange(0,len(values)):
		if i%2==0:
			fullTag += " " + param(values[i], values[i+1])
	fullTag += ">"
	if content:
		for x in content.splitlines():
			fullTag += "\n\t"+x
	return fullTag + "\n</" + tag + ">"

#OUTPUT: "<tag v[0]='v[1]'/>"
def singleTagWithValues(tag, *values):
	fullTag = "<" + tag
	for i in xrange(0,len(values)):
		if i%2==0:
			fullTag += " " + param(values[i], values[i+1])
	fullTag += ">\n"
	return fullTag

#OUTPUT: "<link rel='stylesheet' href='PATH'/>"
def cssAt(path):
	return singleTagWithValues("link", "rel", "stylesheet", "type", "text/css", "href", path)

#OUTPUT: "<meta name='name' content='content'/>""
def metadata(name, content):
	return singleTagWithValues("meta", "name", name, "content", content)

def param(p, value):
	return p + "=\"" + value + "\""

def divWithID(id, inner):
	return tagWithValues("div", inner, "id", id)

def divWithClass(className, inner):
	return tagWithValues("div", inner, "class", className)

def addLink(link, content):
	return "<a href='"+link+"'>"+content+"</a>"

def createHeader(title, description, cssPathArray, depthLevel):
	header = singleTagWithValues("meta", "charset", "utf-8") + \
		metadata("viewport", "width=device-width, initial-scale=1.0") +\
		metadata("author","Kenneth Friedman") +\
		metadata("description", description) +\
		tag("title", "KF: "+title) +\
		"<!-- CSS -->\n"
	prefix = ""
	if depthLevel==0:
		prefix +=''
	else:
		for x in xrange(0,depthLevel):
			prefix += "../"
	for path in cssPathArray:
		header += cssAt(prefix+path)
	return tag("header", header)

def createMain(title, subtitle, innerHTML):
	main = tagWithValues("div", title, "id", "name")
	main += "\n" + tagWithValues("div", subtitle, "id", "subname")
	main += "\n" + innerHTML
	return divWithID("main", main)

def createBody(title, subtitle, innerHTML, depth, navSection):
	body = createNav(navSection, depth)
	body += "\n" + createMain(title, subtitle, innerHTML)
	return tag("body", body) + addGoogleScripts()

def createNav(navSection, depthLevel):
	prefix = ""
	if depthLevel==0:
		prefix +=''
	else:
		for x in xrange(0,depthLevel):
			prefix += "../"
	nName = addLink(prefix, "kenneth<br id='br-on-full'/>friedman")

	nList = ""
	home = "thoughts"
	sections = ["questions", "projects", "more", "archive", "about"]

	if (navSection == home):
		nList += tag("li", tagWithValues("a", home, "href", prefix, "style", "color: "+COLOR))
	else:
		nList += tag("li", addLink(prefix, home))

	for i in xrange(len(sections)):
		s = sections[i]
		brInt = ""
		if (i==1):
			brInt = "<br id='br-on-mobile'/>"
		if (navSection == s):
			nList += tag("li", tagWithValues("a", s, "href", prefix+s, "style", "color: "+COLOR)+brInt)
		else:
			nList += tag("li", addLink(prefix+s, s)+brInt)

	navList = tagWithValues("ul", nList, "id", "navList")

	innerNav = divWithID("nav-name", nName) + navList
	return divWithID("nav", innerNav)

def createHTML(title, subtitle, description, cssPaths, depth, navSection, innerHTML):
	print "NAV SECTION: " + navSection
	html = createHeader(title, description, cssPaths, depth)
	html += createBody(title, subtitle, innerHTML, depth, navSection)
	return tag("html", html)

def addGoogleScripts():
	return "FIX BEFORE RELEASING with proper UA from google"
	return "<script>(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)})(window,document,'script','//www.google-analytics.com/analytics.js','ga');ga('create', 'UA-35724589-1', 'auto');ga('send', 'pageview');</script>"


def makeDirAt(path):
	if not os.path.exists(path):
   		os.makedirs(path)

def writeToIndexHTML(content, path):
	makeDirAt(path)
	finalText = open(path+"/index.html", "w")
	finalText.write(content)
	finalText.close()

def markdownToHTML(mdContent):
	text_file = open("temp.txt", "w")
	text_file.write(mdContent)
	text_file.close()
	html = subprocess.check_output("perl Markdown.pl  'temp.txt'", shell=True)
	os.remove("temp.txt")
	return html

def archiveToHTML(archContent, depth):
	htmlArchive = ""
	for line in string.split(archContent, '\n'):
		if len(line)>0 and (line[0] == '-' or line[0] == '*'):
			prefix = ""
			for i in xrange(depth-1):
				prefix += "../"
			if line[0] == '-':
				imageT = singleTagWithValues("img", "class", "bullet", "src", prefix + "circle.png")
			else:
				imageT = singleTagWithValues("img", "class", "bullet", "src", prefix + "star.png")
			split = line.find("::")
			if split < 0:
				print "ERROR: No split in an archive item:" + line
			else:
				postTitle = line[1:split].strip()
				postLink = line[split+2:].strip()
				innerArch = addLink(postLink, postTitle)
				htmlArchive += tag("div", imageT+innerArch)
		else:
			if depth==1:
				htmlArchive += tag("h2", addLink(line+"/", line))
			else:
				htmlArchive += tag("h2", line.strip())
	return htmlArchive


def createFullPageAtMDPath(path, depth, cssList):
	fileName = path+"/index.md"
	with open(fileName, 'r') as myfile:
		data=myfile.read()
	byLine = data.split('\n')
	title = ""
	des = ""
	subtitle = ""
	navSection = ""
	convertToHTML = True
	isArchiveSystem = False
	for line in byLine:
		if line[0:6]=="TITLE:":
			title = line[6:].strip()
		elif line[0:12] == "SHORT-TITLE:":
			des = line[12:].strip()
		elif line[0:5] == "DATE:":
			subtitle = line[5:].strip()
		elif line[0:4] == "NAV:":
			navSection = line[4:].strip()
		elif line[0:3] == "MD:":
			mdYesOrNo = line[3:].strip()
			if mdYesOrNo.lower() == "no" or mdYesOrNo.lower() == "false":
				convertToHTML = False
		elif line[0:8] == "ARCHIVE:":
			archYesOrNo = line[8:].strip()
			if archYesOrNo.lower() == "yes" or archYesOrNo.lower() == "true":
				isArchiveSystem = True
	firstIndex = data.find("POST:")+7
	contentAsMD = data[firstIndex:]
	if isArchiveSystem:
		contentAsHTML = archiveToHTML(contentAsMD, depth)
	elif convertToHTML:
		contentAsHTML = markdownToHTML(contentAsMD)
	else:
		contentAsHTML = contentAsMD
	footer = "<footer style=\"font-family: 'c3'; text-align: center;\">Kenneth Friedman <script type=\"text/javascript\">document.write(new Date().getFullYear());</script></footer>"
	fullPageAsHTML = createHTML(title, des, "KF: "+title, cssList, depth, navSection, contentAsHTML+footer)
	writeToIndexHTML(fullPageAsHTML, path)



