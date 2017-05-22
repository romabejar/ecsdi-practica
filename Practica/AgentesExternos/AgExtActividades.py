"""
API KEY GOOGLE PLACES = AIzaSyCyjudYWWbnReJa3LdTgfnQXgLxIyXvLSk
"""
__author__ = 'bejar'

from flask import Flask, request, Response
from flask.json import jsonify
import json
import argparse
import requests
from requests import ConnectionError
from multiprocessing import Process
from googleplaces import GooglePlaces, types, lang
import string

# Definimos los parametros de la linea de comandos
parser = argparse.ArgumentParser()
parser.add_argument('--host', default='localhost', help="Host del agente")
parser.add_argument('--port', type=int, help="Puerto de comunicacion del agente")
parser.add_argument('--acomm', help='Direccion del agente con el que comunicarse')
parser.add_argument('--aport', type=int, help='Puerto del agente con el que comunicarse')
parser.add_argument('--messages', nargs='+', default=[], help="mensajes a enviar")

app = Flask(__name__)

@app.route("/")
def isAlive():
    text = 'Hi i\'m AgExtActividades o/, if you wanna party go to <a href= /place?location=Barcelona,%20Spain&keyword=Discoteca&type=night_club>here</a>'
    return text


@app.route("/place")
def getPlaces():
    """
    /place?location=loc&keyword=key&type=type
    :return:
    """
    YOUR_API_KEY = 'AIzaSyCyjudYWWbnReJa3LdTgfnQXgLxIyXvLSk'
    google_places = GooglePlaces(YOUR_API_KEY)

    location = request.args["location"]
    keyword = request.args["keyword"]
    type = request.args["type"]

    # You may prefer to use the text_search API, instead.
    query_result = google_places.nearby_search(
        location=location, keyword=keyword,
        radius=20000, types=type)
    # placestring = "Name: %s, GeoLoc: %s, Reference: %s, Phone: %s \n"(places[0].name, places[0].geo_location, places[0].reference, places[0].local_phone_number)

    resultado = {}
    i = 0
    for place in query_result.places:
        place_json = {}
        # Returned places from a query are place summaries.
        # print place.name
        # print place.geo_location
        # print place.reference
        place.get_details()
        place_json['name'] = place.name
        place_json['lat'] = float(place.geo_location['lat'])
        place_json['lng'] = float(place.geo_location['lng'])
        # place_json['reference'] = place.reference
        # place_json['details'] = place.details
        # The following method has to make a further API call.
        # Referencing any of the attributes below, prior to making a call to
        # get_details() will raise a googleplaces.GooglePlacesAttributeError.
        # print place.details # A dict matching the JSON response from Google.
        # print place.local_phone_number
        # print place.international_phone_number
        # print place.website
        # print place.url
        resultado[i] = place_json
        print i
        print resultado[i]
        i = i+1

    # HAY QUE INTENTAR DEVOLVER UN JSON CON LA INFO

    json_data = json.dumps(resultado)
    print json_data
    return json_data

if __name__ == '__main__':

    # parsing de los parametros de la linea de comandos
    args = parser.parse_args()

    # Ponemos en marcha el servidor
    app.run(host=args.host, port=args.port)

    print 'The End'