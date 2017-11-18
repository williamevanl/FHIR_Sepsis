from flask import Flask
from flask import render_template
import fhirclient.models.observation as o
import fhirclient.models.patient as p
import fhirclient.models.bundle as b
from fhirclient import client
import requests
import json

app = Flask(__name__)

@app.route("/") 


def hello(): 
        return "Hello World!"

@app.route("/fhir-app/")
def launch():
    return render_template('launch.html')



@app.route("/fhir-app/graph")
def graph():
    return render_template('graph.html')

@app.route("/fhir-app/launch")
def index():
    return render_template('index.html')

@app.route("/fhir-app/bootstrap")
def bootstrap():
    settings = {
                    'app_id': 'my_web_app',
                    'api_base': "http://35.184.247.92:8080/baseDstu2/",
                    'count':'500'
                    }
    smart = client.FHIRClient(settings=settings)
    # this will run a query that returns all observations
    search = p.Patient.where  (  struct=None)
    # This will put a bundle into the variable obs with the first 10 results as entries 
    obs = search.perform(smart.server)
    lastUrl = ""
    jsonArray = []
    lastObject = obs.as_json()
# Print it out - 
    while 1 == 1:
        nex =  lastObject
        lastUrl = nex['link'][1]['url'] 
        r = requests.get(lastUrl)
        if nex['link'][1]['relation'] == 'previous':
            break
        jsonArray.append(r.json()) 
    
        lastObject = r.json()
    #print lastUrl

    nameArray = []
    for record in jsonArray:
        for rec2 in (record['entry']):
            try:
                nameArray.append(str(rec2['resource']['name'][0]['use']))
            except:
                pass
    print str(nameArray) 
    return render_template('bootstrap/startbootstrap-sb-admin-gh-pages/index.html', option_list=nameArray)

if (__name__ == "__main__"): 
    app.run(host='0.0.0.0')
