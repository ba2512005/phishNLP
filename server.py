# -*- coding: cp1252 -*-
# server.py
import falcon
import os
import json
from waitress import serve
import enronspamfilter
import category as getCategory
import detectLang
import targetsBuilder
import dnstwist.dnstwist as dns

class NLPcaller:
    def on_get(self, req, resp):
        """Handles GET requests"""
        msg2 = ''' Usage: 
        POST to /nlp with the format:
        {
        "fromHeader" : "<goodemail@ge.com>"
        "toHeader"" : "<uncle.jeff@ge.com>"
        "replyToHeader" : "<badspammer@gg.com>"
        "emailBody" : "<message content you want to test>"
        
        }

        response looks like this:
        {
            "category": "financial - general",
            "headerFraud": 1,
            "confidence": 1,
            "language": "english",
            "categoryWeight": "2.0",
            "targetType": "Employee",
            "spamDetected": "1",
            "htmlInBody": 0,
            "mismatchedHref": [],
            "domains": [
                {
                    "url": "g00gle.com",
                    "spoofedAs": "google.com"
                },
                {
                    "url": "turdlogger.com",
                    "spoofedAs": 0
                },
                {
                    "url": "www.letthestoriesliveon.com",
                    "spoofedAs": 0
                }
            ],
            "spoofedUrlCount": 1,
            "risk": 0.6666666666666666,
            "contentRisk": 0.6666666666666666
        }
        '''
        resp.body = (msg2)
        
    def on_post(self,req,resp):
        try:
            raw_json = req.stream.read()
            print raw_json
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error',ex.message)
        try:
            inputs = json.loads(raw_json, encoding='cp1252')
            body = inputs['emailBody']
            fromHeader = inputs['fromHeader']
            toHeader = inputs['toHeader']
            replyToHeader = inputs['replyToHeader']
            target, targetWeight = targetsBuilder.getTarget(toHeader)
            
            language = detectLang.detectLang(body)  
            detector = enronspamfilter.predicter(body)
            assessment = getCategory.assess(body, fromHeader, replyToHeader)

            category = assessment['category']
            spoofCount = assessment['spoofedUrlCount']
            headerFraud = assessment['headerFraud']
            mismatchedHref = len(assessment['mismatchedHref'])

            confidence = 0 #get confidence level of things based on indicators
            det = str(detector)[2]
            if spoofCount>=1 and det == '1':
                category = "phish - " + category
                confidence = 1
            elif spoofCount == 0 and det == '1':
                category = "spam - " + category
                confidence = .75
            elif spoofCount>=1 and det == '0':
                category = "phish -" + category
                confidence = .5
            elif spoofCount == 0 and det == '0':
                confidence = .75
            else:
                confidence = .66

            print spoofCount
            print confidence
            print mismatchedHref
            

            contentRisk = float(spoofCount + headerFraud + mismatchedHref)/3
            risk = contentRisk * targetWeight * confidence
            
            assessment['spamDetected'] = det
            assessment['language'] = language
            assessment['targetType'] = target
            assessment['confidence'] = confidence
            assessment['contentRisk'] = contentRisk
            assessment['risk'] = risk 
            
            
            #print assessment
    
            resp.body = json.dumps(assessment)
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'Invalid JSON','Could not decode the request body. The ''JSON was incorrect. Call a GET on this URL for usage info.')

 
class ThingsResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.body = ('try /nlp')
    
    def on_post(self, req, resp):
         
         """Handles POST requests"""
         try:
             raw_json = req.stream.read()
             print raw_json
         except Exception as ex:
             raise falcon.HTTPError(falcon.HTTP_400,'Error',ex.message)

         try:
             result = json.loads(raw_json, encoding='utf-8')
             #sid =  r.db(PROJECT_DB).table(PROJECT_TABLE).insert({'title':result['title'],'body':result['body']}).run(db_connection)
             #resp.body = 'Successfully inserted %s'%sid
             resp.body = 'read things like this: Title: %s, Body: %s'% (result['title'], result['body'])
         except ValueError:
             raise falcon.HTTPError(falcon.HTTP_400,'Invalid JSON','Could not decode the request body. The ''JSON was incorrect.')

api = falcon.API()
things = ThingsResource()
NLP = NLPcaller()
api.add_route('/', things)
api.add_route('/nlp', NLP)




#dev on localhost
serve(api, host='0.0.0.0', port=80)
