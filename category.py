import xlrd
import re
import json

def retArrayOfDomains(str):
    myregex = r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}'
    return (re.findall(myregex, str))

def arrayCountNlpKeywords(sentence):
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

def jsonCountNlpKeywords(sentence):
    print json.dumps(arrayCountNlpKeywords(sentence), ensure_ascii=False)

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


def main():
    sentence = ('hello there... JAvASCripT - Stainless steel..stainless steel as seen on')
    sentence = sentence.strip().lower()

    print sentence
    jsonCountNlpKeywords(sentence)

    print(retArrayOfDomains("this is just an example https://subdomain.google.co.uk"))
    print(len(retArrayOfDomains("this is just an example https://subdomain.google.co.uk")))

    data = importExcelSheetIndicators("example.xlsx")
    data = appendCalculatedWordPoints(sentence, data)

    print data
    categories = arrayOfCategories(data)

    categoryTotals = tallyTotalPerCategory(categories, data)
    print categoryTotals



main()
