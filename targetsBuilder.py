import json
import requests

def getToken():
        
        url = "https://fssfed.stage.ge.com/fss/as/token.oauth2"

        querystring = {"grant_type":"client_credentials","client_id":"GECorporate-6GjaUdE6cO56CCR6iqeaX3tj","client_secret":"4addec84c12f031fd969ff573c2161e60537fe30","scope":"api"}

        headers = {
            'cache-control': "no-cache"
            }

        response = requests.request("POST", url, headers=headers, params=querystring)

        #print(response.text)
        return response

def getEmployees(token, email):
        url = "https://stage.api.ge.com:443/digital/hrapi/v1/search/people"

        #querystring = {"q":"emailAddress:"+email}
        querystring = {"q":"emailAddress:\""+email+"\""}

        headers = {
            'authorization': "bearer "+token,
            'content-type': "application/x-www-form-urlencoded",
            'cache-control': "no-cache"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        
        #print response.text
        return response

def getTarget(email):
        tokenResp = json.loads(getToken().text)
        token = str(tokenResp['access_token'])
        empResp = json.loads(getEmployees(token,email).text)
        employeeType = empResp['data'][0]['personType'].encode('ascii','ignore')
        x = 1
        weight = {
          'Officer': lambda x: x * 2,
          'Employee': lambda x: x * 1,
          'Contractor': lambda x: x * 1
        }[employeeType](x)
        return employeeType, weight

#print getTarget('jri.immelt@ge.com')
