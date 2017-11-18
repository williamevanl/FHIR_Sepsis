import sys
from fhirclient import client
import fhirclient.models.patient as p
import fhirclient.models.observation as o
from datetime import datetime
#myfile = open(sys.argv[1], 'r')


def postObservation(measurement, value, patient, time):
    print measurement, value
    obs = o.Observation({'code': {'coding': [ {'system': 'http://hl7.org/fhir/observation-category' , 'code' : 'fakecode', 'display': measurement }]}, 'status': 'activeYo', "subject":{ "reference": "Patient/" + patient}, "effectiveDateTime": time, "valueQuantity": {"value": value} })#  "effectiveDateTime": time })
    result = o.Observation.create(obs, smart.server)
def postPatient(name):
    pat = p.Patient({"name" :[{"use":name}]})
    result = p.Patient.create(pat, smart.server)['issue'][0]['diagnostics'].split('/')[1] 
    return result

settings = {
                    'app_id': 'my_web_app',
                               # 'api_base': 'http://23.236.62.134:8080/baseDstu2/'
                     'api_base': 'http://localhost:8080/baseDstu2/'
                                                           }
smart = client.FHIRClient(settings=settings)


patDict = {}
for i in range(1,48):
    myfile = open("out." + str(i), 'r')

    lineCount = 0
    obsArray = []
    for line in myfile:
        lineCount += 1
       
        lineSplit = line.split("|")
    
        if lineCount == 1:
            for header in lineSplit:
                obsArray.append(header)
    
    ##For every column
        if len(lineSplit) > 2 and lineCount > 1:
            if lineSplit[1] not in patDict:
                patDict[lineSplit[1]] = postPatient(lineSplit[1].strip())

            
            for col in range (2, len(lineSplit)): 
                if lineSplit[col].strip() != '' and lineSplit[col].strip() != "NULL":
                #print len(lineSplit[col])
                    dTime = lineSplit[0].strip()+":00"
                    rdTime = dTime.replace(" ", "T")
                #print obsArray[col], lineSplit[col], patDict[lineSplit[1]], rdTime
                #print lineSplit[1]
                    postObservation(obsArray[col], float(lineSplit[col]), patDict[lineSplit[1]], rdTime)
#print str(patDict)



