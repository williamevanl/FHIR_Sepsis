from flask import Flask
from flask import render_template
import fhirclient.models.observation as o
import fhirclient.models.patient as p
import fhirclient.models.bundle as b
from fhirclient import client
import requests
import json
from flask import request
from pat_dat3 import get_patient_sepsis_scores

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
    window = request.args.get('window')
    patient  = request.args.get('patient')

    print(window)
    settings = {
                    'app_id': 'my_web_app',
                    'api_base': "http://35.192.2.85:8080/baseDstu2/",
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
    jsonArray.append(lastObject)
# Print it out - 
    while 1 == 1:
        nex =  lastObject
        try:
            lastUrl = nex['link'][1]['url'] 
        except:
            break
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
    #print str(nameArray)
    timeList=['time1', 'time2', 'time3', 'time4', 'time5', 'time6']
    sepScore = [.1,.2,.3,.4,.5,.6]
    patDict = {'4d46bc59629604b671e43c51385490c0': '1', '89034dfb56c4c5a8c6953beaaec4a26f': '41', '9007636124fa4a42caa84fc025236386' : '120', 'bac33e5db1d0f9ffe2091044e58a9394' :'212' } 
    
    wind = 12
    if window != None:
        wind = int(window.split(' ')[0])
        print str(wind)

    #print type(tar)
    if patient !=  None:
        res = get_patient_sepsis_scores(patient_id = patDict[patient] , window_secs = 60*60, interval_secs = 60*60, calc_cnt = wind)    
        timeList = []
        sepScore = []
        for timeL in res['dt']:
            timeList.append(str(timeL.time()))
   
        for value in res['value']:
            sepScore.append(float(value))
    return render_template('bootstrap/startbootstrap-sb-admin-gh-pages/index.html', option_list=nameArray, newList=sepScore, dateList=timeList)


if (__name__ == "__main__"): 
    app.run(host='0.0.0.0')
