from flask import Flask
from flask import render_template

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
    return render_template('bootstrap/startbootstrap-sb-admin-gh-pages/index.html')

if (__name__ == "__main__"): 
    app.run(host='0.0.0.0')
