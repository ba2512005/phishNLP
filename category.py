# -*- coding: cp1252 -*-
import xlrd
import re
import tldextract
import esm
import json
import bs4
import BeautifulSoup


def extractUrl(text, match):
	pretld, posttld = None, None
	url = ""

	tld = match[1]
	startpt, endpt = match[0][0], match[0][1]

	# check the next character is valid
	if len(text) > endpt:
		nextcharacter = text[endpt]
		if re.match("[a-z0-9-.]", nextcharacter):
			return None

		posttld = re.match(':?[0-9]*[/[!#$&-;=?a-z]+]?', text[endpt:])
	pretld = re.search('[a-z0-9-.]+?$', text[:startpt])

	if pretld:
		url = pretld.group(0)
		startpt -= len(pretld.group(0))
	url += tld
	if posttld:
		url += posttld.group(0)		
		endpt += len(posttld.group(0))

	# if it ends with a . or , strip it because it's probably unintentional
	url = url.rstrip(",.") 

	return (startpt, endpt), url

def getUrls(text):
	results = []
	tlds = (tldextract.TLDExtract()._get_tld_extractor().tlds)
	tldindex = esm.Index()
	for tld in tlds:
		tldindex.enter("." + tld.encode("idna"))
	tldindex.fix()
	tldsfound = tldindex.query(text)
	results = [extractUrl(text, tld) for tld in tldsfound]
	results = [x for x in results if x] # remove nulls
	return results
    
def arrayCountNlpKeywords(sentence): #wtf is this
    data = {}
    data["javascript"] = sentence.lower().count('javascript')
    data["numPeriods"] = sentence.count('.')
    data["label"] = sentence.lower().count('label')
    data["invoice"] = sentence.lower().count('invoice')
    data["post"] = sentence.lower().count('post')
    data["document"] = sentence.lower().count('document')
    data["postal"] = sentence.lower().count('postal')
    data["calculations"] = sentence.lower().count('calculations')
    data["copy"] = sentence.lower().count('copy')
    data["fedex"] = sentence.lower().count('fedex')
    data["statement"] = sentence.lower().count('statement')
    data["financial"] = sentence.lower().count('financial')
    data["dhl"] = sentence.lower().count('dhl')
    data["usps"] = sentence.lower().count('usps')
    data["8"] = sentence.lower().count('8')
    data["notification"] = sentence.lower().count('notification')
    data["n"] = sentence.lower().count('n')
    data["irs"] = sentence.lower().count('irs')
    data["ups"] = sentence.lower().count('ups')
    data["no"] = sentence.lower().count('no')
    data["delivery"] = sentence.lower().count('delivery')
    data["ticket"] = sentence.lower().count('ticket')
    return data

# categories = ['Commerce', 'Personal', 'Employment', 'Financial - General', 'Financial - Business' , 'Financial - Personal' , 'General' , 'Greetings' , 'Marketing' , 'Medical' , 'Numbers' , 'Offers' , 'Calls-to-Action' , 'Free' , 'Descriptions/Adjectives' , 'Sense of Urgency' , 'Nouns']

def importExcelSheetIndicators(filename):
    book = xlrd.open_workbook(
        filename)  # open our xls file, there's lots of extra default options in this call, for logging etc. take a look at the docs

    sheet = book.sheet_by_index(0)  # or by the index it has in excel's sheet collection

    r = sheet.row_values(0)

    data = []  # make a data store
    for i in range(1, sheet.nrows):
        row = sheet.row_slice(i)
        data.append([row[0].value.strip().lower(), row[1].value.strip().lower(), row[2].value])

    # print json.dumps(data, indent=1)

    return data

def appendCalculatedWordPoints(sentence, data):
    for i in range(len(data)):
        category = data[i][0]
        word = data[i][1]
        weight = data[i][2]
        data[i].append(sentence.count(word) * weight) # count of word * weight = points
        # print data[i]
    return data

def arrayOfCategories(data):
    categories = []
    for i in range(len(data)):
        if data[i][0] not in categories:
            categories.append(data[i][0])
    return categories

def tallyTotalPerCategory(categories, data):
    categoryTotal = []
    for i in range(len(categories)):
        total = 0;
        for j in range(len(data)):
            category = data[j][0]
            points = data[j][3]
            if (category == categories[i]):
                total += points
        categoryTotal.append([categories[i], total])
    return categoryTotal

def returnHighestCategory(categoryTotals):
    highestCategory = ['None', -1]
    for i in range(len(categoryTotals)):
        category = categoryTotals[i][0]
        points = categoryTotals[i][1]
        if (points > highestCategory[1]):
            highestCategory = categoryTotals[i]
    return highestCategory

def countNumberOfPeriods(body):
    return body.lower().count('.')

def loadDomains():
    df = open('fuzzydomains.csv', 'r')
    domainDict = {}
    original = ''
    for line in df:
        row = line.split(',')
        if row[0] in 'Original*':
            original = row[1]
            domainDict[row[1]] = 0
        elif row[0] not in 'fuzzer':
            domainDict[row[1]] = original
    df.close()
    return domainDict

def fromReplyToComparison(emailFrom, emailReplyTo):
    if (emailFrom == emailReplyTo):
        return 0
    return 1

def isHtmlInBody(body):
    return bool(bs4.BeautifulSoup(body, "html.parser").find())

def returnHrefs(body):
    hRefs = []
    soup = BeautifulSoup.BeautifulSoup(body)
    for link in soup.findAll("a"):
        hRefs.append([link, link.get("href"), link.string])
    return hRefs

def returnDifferentHrefs(hrefArray):
    differentHrefValues = []
    for href in hrefArray:
        if (href[1].strip().lower()) != (href[2].strip().lower()):
            differentHrefValues.append(href)
    return differentHrefValues

domains = loadDomains()
            
def assess(sentence, emailFrom, emailReplyTo):
    sentence = sentence.strip().lower()

    #print sentence
    #jsonCountNlpKeywords(sentence)

    #print(retArrayOfDomains("this is just an example https://subdomain.google.co.uk"))
    #print(len(retArrayOfDomains("this is just an example https://subdomain.google.co.uk")))

    data = importExcelSheetIndicators("example.xlsx") #should implement n-gram, normalization, lemmetizer
    data = appendCalculatedWordPoints(sentence, data)

    #print data
    categories = arrayOfCategories(data)

    categoryTotals = tallyTotalPerCategory(categories, data)
    #print categoryTotals

    highestCategory = returnHighestCategory(categoryTotals)
    #print "\nHighest Category: \n", highestCategory[0], "\nPoints: \n", highestCategory[1]
    allDomains = []
    urls = {}
    spoofCount = 0
    nonSpoofCount = 0
    for url in getUrls(sentence):
        print url
        domainObject = {}
        if url[1] not in urls: 
            if url[1] in domains:
                #domainObject.append(json.dumps({'url':url[1] ,'spoofedAs':domains[url[1]]}))
                domainObject['url'] = url[1]
                domainObject['spoofedAs'] = domains[url[1]]
                urls[url[1]] = domains[url[1]]
                spoofCount+=1
                
            else:
                urls[url[1]] = "no spoof found"
                domainObject['url'] = url[1]
                domainObject['spoofedAs'] = 0
                nonSpoofCount +=1
        allDomains.append(domainObject)
                #domainObject.append(json.dumps({'url':url[1] ,'spoofedAs':0}))
    category= highestCategory[0].encode('ascii','ignore')
    weight = str(highestCategory[1]).encode('ascii','ignore')
    
    
    
    ####################################return json.dumps({'category': category, 'categoryWeight' : weight , 'domains': [domain for domain in allDomains] })
    #counts number of periods in the body
    #emailFrom = "mohammed.kassem@ge.com"
    #emailReplyTo = "mohammed.kassem@ge.com"

    emailFrom = emailFrom.strip().lower()
    emailReplyTo = emailReplyTo.strip().lower()
    
    #print countNumberOfPeriods(sentence)

    #counts number of periods in the url

    fromReplyToCheck = fromReplyToComparison(emailFrom, emailReplyTo)
    
    
    #print "ReplyTo and From Header Comparison: ", fromReplyToCheck

    #sentence2 = "<html><a href='test.com'>sfdfs</a><a href='test.com'>test.com</a></html>"
    #print "HTML in body: ", isHtmlInBody(sentence2)
    #hRefs = returnHrefs(sentence2)

    #print "hrefs: ", hRefs

    #differenthRefs = returnDifferentHrefs(hRefs)
    #print "Different hRefs: ", differenthRefs
    
    catObject = {}
    catObject['category']=category
    catObject['categoryWeight']= weight 
    catObject['domains']=[domain for domain in allDomains]
    catObject['headerFraud']= fromReplyToCheck
    catObject['htmlInBody']= int(isHtmlInBody(sentence))
    catObject['mismatchedHref']= returnDifferentHrefs(returnHrefs(sentence))
    catObject['spoofedUrlCount']=spoofCount
    
    return catObject
#sentence = ("As one of our top customers we are providing 10% OFF the total of your next used book purchase g00gle.com from www.letthestoriesliveon.com . Please use the promotional code, TOPTENOFF at checkout. Limited to 1 use per customer. All books have free shipping within the contiguous 48 United States and there is no minimum purchase.We have millions of used books in stock that are up to 90% off MRSP and add tens of thousands of new items every day. Don't forget to check back frequently for new arrivals.")
#emailFrom = 'sofyan.saputra@ge.com'
#emailReplyTo = 'sofyan.s4putra@ge.com'
#print assess(sentence, emailFrom, emailReplyTo)

