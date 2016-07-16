import csv
import siteHelper
import math

class Book:

	title = ""
	author = ""
	description = ""
	availability = []
	recommenders = []

	def __init__(self, title, author, description):
		self.title = title
		self.author = author
		self.description = description

class Recommender:
	name = ""
	category = ""
	bio = ""
	category = ""
	books = []

#Parser that returns an arry of books, parsed from the reccaTab.txt TSV
def getArrayOfBooks():
	with open('reccaTab.txt','rU') as tsvin:
		tsvin = csv.reader(tsvin, delimiter='\t')
		books = []
		for row in tsvin:
			tempBook = Book(row[0], row[1], row[2])
			tempBook.availability = [x.strip() for x in row[3].split(',')]
			tempBook.recommenders = [x.strip() for x in row[4].split(',')]
			books.append(tempBook)
		books.pop(0)
		return books

def getArrayOfDistinctRecommenders(booksList):
	authors = []
	for book in booksList:
		authors += book.recommenders
	return list(set(authors))

def getArrayOfBooksFromRecommender(recca, booksList):
	bookFromReccer = []
	for book in booksList:
		if recca.name in book.recommenders:
			bookFromReccer.append(book)
	return bookFromReccer

def getArrayOfRecommenders():
	with open('reccaReccers.txt','rU') as tsvin:
		tsvin = csv.reader(tsvin, delimiter='\t')
		reccers = []
		for row in tsvin:
			tempReccer = Recommender()
			tempReccer.name = row[0]
			tempReccer.category = row[1]
			tempReccer.bio = row[2]
			tempReccer.wikiLink = row[3]
			reccers.append(tempReccer)
		reccers.pop(0)
		return reccers

#These are the parsers that only run once per build
ALL_BOOK_LIST = getArrayOfBooks()
ALL_RECCER_LIST = getArrayOfRecommenders()

def getFullRecommenderObjectFromReccerName(incomingName):
	for tempRec in ALL_RECCER_LIST:
		if tempRec.name == incomingName:
			return tempRec
	raise Exception(incomingName, ' referenced, but missing from official recommenders list.')

def convertStringToPath(incoming):
	return incoming.replace(' ', '-').replace('.', '-').replace('--', '-').lower()

def createHeader(recommender, cssPathArray):
	header = siteHelper.singleTagWithValues("meta", "charset", "utf-8")
	header += siteHelper.metadata("viewport", "width=device-width, initial-scale=1.0")
	header += siteHelper.metadata("description", "A simple and clean book list of books recommended by "+recommender.name+".")
	header += siteHelper.tag("title", "Recca: "+recommender.name+"'s Book List") + "<!-- CSS -->\n"
	for path in cssPathArray:
		header += siteHelper.cssAt(path)
	return siteHelper.tag("header", header)

def createBody(reccer):
	article = createPersonBlock(reccer)
	article += createContentBlock(reccer)
	body = siteHelper.addLink("http://recca.org", "<img src=\"../../reccaLogo.png\"/>")
	body += siteHelper.divWithClass("article", article)
	return siteHelper.tag("body", body)

def createPersonBlock(reccer):
	personBlock = siteHelper.tag("person", reccer.name)
	personBlock += siteHelper.tag("bio", reccer.bio)
	personBlock += siteHelper.addLink(reccer.wikiLink, "Read More")
	return siteHelper.divWithClass("personBlock", personBlock)

def createContentBlock(reccer):
	innerBlock = ""
	for book in getArrayOfBooksFromRecommender(reccer, ALL_BOOK_LIST):
		tempBookItem = getBasicInfo(book)
		tempBookItem += getAdditionalInfo(book, reccer)
		innerBlock += siteHelper.tag("bookItem", tempBookItem)
	contentBlock = siteHelper.tag("div", innerBlock)
	return siteHelper.divWithClass("contentBlock", contentBlock)

def getBasicInfo(book):
	basicInfo = siteHelper.divWithClass("bookTitle", book.title)
	tempBookInnerAuthor = siteHelper.tag("strong", book.author)
	basicInfo += siteHelper.divWithClass("bookAuthor", "by "+tempBookInnerAuthor)
	basicInfo += siteHelper.divWithClass("bookDescription", book.description)
	return siteHelper.divWithClass("basicInfo", basicInfo)

def getAdditionalInfo(book, reccer):
	additionalInfo = siteHelper.divWithClass("additionalTopic", "available in:")
	additionalInfo += siteHelper.divWithClass("topicContent", getAvailabilityBlock(book))
	additionalInfo += siteHelper.divWithClass("additionalTopic", "also recommended by:")
	additionalInfo += siteHelper.divWithClass("topicContent", getOtherReccers(book, reccer))
	return siteHelper.divWithClass("additionalInfo", additionalInfo)

def getAvailabilityBlock(book):
	avail = ""
	for a in book.availability:
		avail += a +  "<br/>"
	avail = avail[:-5].strip() #removes last break line
	return avail

def getOtherReccers(book, reccer):
	others = ""
	for r in book.recommenders:
		rObj = getFullRecommenderObjectFromReccerName(r)
		if rObj.name != reccer.name: #don't inclue the current page's reccer
			tempURL = "../../" + convertStringToPath(rObj.category + "/" + rObj.name)
			rLink = siteHelper.addLink(tempURL,rObj.name)
			others += rLink + "<br/>"
	others = others[:-5].strip() #removes last break line
	return others

def createPageForRecommender(reccer):	
	path = convertStringToPath(reccer.category + "/" + reccer.name)
	headerHTML = createHeader(reccer, ["../../css/styles.css","../../css/fonts.css"])
	bodyHTML = createBody(reccer)
	allHTML = headerHTML + bodyHTML
	content = siteHelper.tag("html", allHTML)
	siteHelper.writeToIndexHTML(content, path)

def makeHomePageWithReccers(reccers):
	categories = {}
	homePage = ""
	for r in reccers:
		if r.category not in categories.keys():
			categories[r.category] = []
		categories[r.category].append([r.name, convertStringToPath(r.category + "/" + r.name)])
	innerBody = ""
	for category in categories.keys():
		tempFieldSection = siteHelper.tag("h1", category.capitalize())
		categoryCount = len(categories[category])
		halfCount = int(math.ceil(categoryCount/2.0))
		firstCol = ""
		secondCol = ""
		for i in xrange(0, halfCount):
			tempName = categories[category][i][0]
			tempLink = categories[category][i][1]
			firstCol += siteHelper.addLink(tempLink, tempName) + "<br/>"
		for i in xrange(halfCount, categoryCount):
			tempName = categories[category][i][0]
			tempLink = categories[category][i][1]
			secondCol += siteHelper.addLink(tempLink, tempName) + "<br/>"
		tempFieldSection += siteHelper.divWithClass("firstCol", firstCol)
		tempFieldSection += siteHelper.divWithClass("secondCol", secondCol)
		innerBody += siteHelper.divWithClass("fieldSection", tempFieldSection)
	innerHead = siteHelper.cssAt("css/home.css")
	innerHead += siteHelper.cssAt("css/fonts.css")
	innerHead += siteHelper.tag("title", "Recca")
	innerHead += siteHelper.singleTagWithValues("meta", "charset", "utf-8")
	innerHead += siteHelper.metadata("viewport", "width=device-width, initial-scale=1.0")
	innerHead += siteHelper.metadata("description", "A simple and clean list of book recommendations from the greatest minds around.")
	header = siteHelper.tag("head", innerHead)
	insideBody = siteHelper.singleTagWithValues("img", "src", "reccaLogo.png", "width", "20%", "style", "position: absolute")
	insideBody += siteHelper.tag("innerBody", innerBody)
	body = siteHelper.tag("body", insideBody)
	allHTML = siteHelper.tag("html", header + body)
	siteHelper.writeToIndexHTML(allHTML, ".")

for r in ALL_RECCER_LIST:
	createPageForRecommender(r)

makeHomePageWithReccers(ALL_RECCER_LIST)