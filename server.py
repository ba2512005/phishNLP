# -*- coding: cp1252 -*-
# server.py
import falcon
import os
import json
from waitress import serve
import enronspamfilter

class NLPcaller:
    def on_get(self, req, resp):
        """Handles GET requests"""
        msg2 = ''' Usage: 
        POST to /nlp with the format: {"body" : "<message content you want to test>"}

        response looks like this:
        {
          "spamDetected": 1,
          "category": "finance",
          "riskWeight": ".6"
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
            result = enronspamfilter.predicter(inputs['body'])
            det = str(result)[2]
            resp.body = ('{"spam_detected" : '+det+', "category" : "finance" , "risk" : ".6"}')
            #insert categorizer here
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'Invalid JSON','Could not decode the request body. The ''JSON was incorrect.')

 
class ThingsResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.body = ('\nI\'ve always been more interested in\n'\
                     'the future than in the past.\n'\
                     '\n'\
                     '    ~ Grace Hopper\n\n')
    
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
serve(api, host='0.0.0.0', port=5555)
