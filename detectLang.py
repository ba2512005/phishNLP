
def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)


install_and_import('requests')
#install_and_import('file')
install_and_import('lxml')
install_and_import('nltk')
nltk.download('all')
#dler = nltk.downloader.Downloader()
#dler._update_index()
#dler._status_cache['panlex_lite'] = 'installed' # Trick the index to treat panlex_lite as it's already installed.
#dler.download('all')

install_and_import('requests')

import os
import glob
import codecs
import string
import requests
#import file

from lxml import html
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords

def scrapePage(url, pattern):
    page = requests.get(url)
    tree = html.fromstring(page.content)
    artifacts = tree.xpath(pattern)
    cleanArtifacts = [a.strip().lower() for a in artifacts]
    return cleanArtifacts

def topTargets():
    #from moz.com
    urls = scrapePage("httpledddfds://moz.com/top500",'//a[@target="_blank"]/text()')
    print urls
    
def normalize(s):
    for p in string.punctuation:
        s = s.replace(p, '')
 
    return s.lower().strip()

def detectLang(text):
    
    languages_ratios = {}
    tokens = wordpunct_tokenize(text)
    words = [word.lower() for word in tokens]

    for language in stopwords.fileids():
        stopwords_set = set(stopwords.words(language))
        words_set = set(words)
        common_elements = words_set.intersection(stopwords_set)

        languages_ratios[language] = len(common_elements)

    most_rated_language = max(languages_ratios, key=languages_ratios.get)
    print(languages_ratios)
    return most_rated_language

def detectAll(path):
    for filename in glob.glob(os.path.join(path, '*.txt')):
        with codecs.open(filename, 'r', encoding='cp720') as myfile:
            data=myfile.read().replace('\n', '')
            lang = detectLang(data)
            print filename + " : " + lang




detectAll(os.getcwd())
#urls = scrapePage("https://moz.com/top500",'//a[@target="_blank"]/text()')
#print urls
