"""
API KEY GOOGLE PLACES = AIzaSyCyjudYWWbnReJa3LdTgfnQXgLxIyXvLSk
"""
__author__ = 'bejar'

from flask import Flask, request
import argparse
import requests
from requests import ConnectionError
from multiprocessing import Process
from googleplaces import GooglePlaces, types, lang

# Definimos los parametros de la linea de comandos
parser = argparse.ArgumentParser()
parser.add_argument('--host', default='localhost', help="Host del agente")
parser.add_argument('--port', type=int, help="Puerto de comunicacion del agente")
parser.add_argument('--acomm', help='Direccion del agente con el que comunicarse')
parser.add_argument('--aport', type=int, help='Puerto del agente con el que comunicarse')
parser.add_argument('--messages', nargs='+', default=[], help="mensajes a enviar")

app = Flask(__name__)


@app.route("/")
def isalive():
    """
    Entrada del servicio para saber si esta en funcionamiento
    :return:
    """
    YOUR_API_KEY = 'AIzaSyCyjudYWWbnReJa3LdTgfnQXgLxIyXvLSk'

    google_places = GooglePlaces(YOUR_API_KEY)

    # You may prefer to use the text_search API, instead.
    query_result = google_places.nearby_search(
        location='London, England', keyword='Fish and Chips',
        radius=20000, types=[types.TYPE_FOOD])

    # placestring = "Name: %s, GeoLoc: %s, Reference: %s, Phone: %s \n"(places[0].name, places[0].geo_location, places[0].reference, places[0].local_phone_number)
    return query_result.places[0].name
    # for place in query_result.places:
        # Returned places from a query are place summaries.
        # return place.name
        # return place.geo_location
        # return place.reference

        # The following method has to make a further API call.
        # place.get_details()
        # Referencing any of the attributes below, prior to making a call to
        # get_details() will raise a googleplaces.GooglePlacesAttributeError.
        # return place.details # A dict matching the JSON response from Google.
        # return place.local_phone_number
        # return place.international_phone_number
        # return place.website
        # return place.url

if __name__ == '__main__':

    # parsing de los parametros de la linea de comandos
    args = parser.parse_args()

    # Ponemos en marcha el comportamiento si se indica una direccion
    if args.acomm is not None:
        ab = Process(target=behavior, args=(args.messages, (args.acomm, args.aport)))
        ab.start()

    # Ponemos en marcha el servidor
    app.run(host=args.host, port=args.port)

    # Esperamos a que acaben los behaviors
    if args.acomm is not None:
        ab.join()

    print 'The End'