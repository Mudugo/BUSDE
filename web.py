import json

import flask
from flask import Flask, request

from data import *

app = Flask(__name__)


# TODO:
# Corrigir "a" e "o" para º e ª                     #data linha 95
# Corrigir quebra de linha desnecessária            atrelado ao item acima
# Tirar () das datas                                #data linha 75
# Corrigir UNICODE                                  #web linha 26
# Remover "literatura disponível em www.nanda.org"  #data linha 93

@app.get('/diagnoses')
def list_diagnoses():
    return "Hello, World!"


@app.route('/diagnose/<code>')
def find_by_code(code):
    data = json.dumps(find_diagnose_by_code(diagnoses, code).__dict__, indent=2)
    formated = data.encode().decode('unicode-escape')
    return make_json_response(formated)


@app.get('/diagnose')
def find_by_characteristic():
    characteristics = request.args.getlist("c")
    list = find_diagnose_by_defining_characteristic(diagnoses, characteristics)
    data = json.dumps([ob.__dict__ for ob in list], indent=2)
    return make_json_response(data)


def make_json_response(data):
    resp = flask.make_response(data)
    resp.headers['Content-Type'] = 'application/json'
    return resp


if __name__ == '__main__':
    print("Loading diagnoses...")
    diagnoses = load_diagnoses()

    print("Starting web server...")
    app.run(port=8080, debug=True)
