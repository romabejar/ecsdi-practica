# -*- coding: utf-8 -*-
"""
Agente que responde a peticiones
@author: javier
"""
__author__ = 'javier'
import json
import pprint
import argparse
from googleplaces import GooglePlaces
from flask import Flask, request
from AgentUtil.ACLMessages import build_message, send_message, get_message_properties
from AgentUtil.Agent import Agent
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.plugins.stores import sparqlstore
from flask import Flask, request
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import FOAF, RDF

from AgentUtil.OntoNamespaces import ACL, DSO, TIO
from AgentUtil.FlaskServer import shutdown_server
from AgentUtil.ACLMessages import build_message, send_message, get_message_properties
from AgentUtil.Agent import Agent
from AgentUtil.Logging import config_logger
from datetime import timedelta
import datetime

# Definimos los parametros de la linea de comandos
parser = argparse.ArgumentParser()
parser.add_argument('--open', help="Define si el servidor esta abierto al exterior o no", action='store_true',
                    default=False)
parser.add_argument('--port', type=int, help="Puerto de comunicacion del agente")
parser.add_argument('--dhost', default='localhost', help="Host del agente de directorio")
parser.add_argument('--dport', type=int, help="Puerto de comunicacion del agente de directorio")

# parsing de los parametros de la linea de comandos
args = parser.parse_args()

# Configuration stuff
if args.port is None:
    port = 9003
else:
    port = args.port

plan_port = 9002


#hostname = socket.gethostname()
hostname = 'localhost'

if args.dport is None:
    dport = 9000
else:
    dport = args.dport

#dhostname = socket.gethostname()
dhostname = 'localhost'

# Flask stuff
app = Flask(__name__)

agn = Namespace("http://www.agentes.org#")
myns = Namespace("http://my.namespace.org/")
myns_atr = Namespace("http://my.namespace.org/atributos/")
myns_act = Namespace("http://my.namespace.org/actividades/")
myns_lug = Namespace("http://my.namespace.org/lugares/")
myns_loc = Namespace("http://my.namespace.org/localizacion/")
myns_periodo = Namespace("http://my.namespace.org/periodo/")
myns_valoracion = Namespace("http://my.namespace.org/valoracion/")
myns_compania = Namespace("http://my.namespace.org/compania/")

# Contador de mensajes
mss_cnt = 0

# Datos del Agente Planificador
AgentePlanificador = Agent('AgentePlanificador',
                  agn.AgentePlanificador,
                  'http://%s:%d/comm' % (hostname, port),
                  'http://%s:%d/Stop' % (hostname, port))


@app.route("/comm")
def buscar_actividades_localmente():
    global mss_cnt

    message = request.args['content']
    print "INFO AgentBuscador => Mensaje extraído\n"
    # VERBOSE

    # Grafo en el que volcamos el contenido de la request
    gm = Graph()
    gm.parse(data=message)


    # Propiedades del mensaje
    msgdic = get_message_properties(gm)

    gr = Graph()

    ## Comprobar si lo que tenemos en la chache esta bien
    datos_en_cache = False


    if datos_en_cache == True:
        print "AgenteActividades => Recibo peticion de actividades."
        print "AgenteActividades => Si tenemos datos validos en cache"

        #location = "Barcelona"
        #tipo_actividad = "festiva"

    else:
        json_data = buscar_actividades_externamente("Barcelona","Spain",20000)
        # Grafo donde retornaremos el resultado
        # Hago bind de las ontologias que usaremos en el grafo

        gr.bind('myns_act', myns_act)
        gr.bind('myns_atr', myns_atr)
        gr.bind('myns_loc', myns_loc)
        gr.bind('myns_periodo', myns_periodo)
        gr.bind('myns_compania', myns_compania)

        for place in json_data.places:
            plc_obj = myns_act[place.place_id]
            loc_obj = myns_loc[place.place_id]
            periodo = myns_periodo[place.place_id]
            compania = myns_compania[place.place_id]

            # Localizacion
            gr.add((loc_obj, myns_atr.longitud, Literal("15.9")))  # Parsear de la llamada a la api
            gr.add((loc_obj, myns_atr.latitud, Literal("12.9")))  # Parsear de la llamada a la api

            # Periodo
            gr.add((periodo, myns_atr.inicio, Literal("11:00")))
            gr.add((periodo, myns_atr.fin, Literal("12:50")))

            # Compania
            gr.add((compania, myns_atr.nombre, Literal("Roman Airlines")))
            gr.add((compania, myns_atr.ofrece, plc_obj))

            # Actividad
            gr.add((plc_obj, myns_atr.esUn, myns.activiad))
            gr.add((plc_obj, myns_atr.coste, Literal("15")))
            gr.add((plc_obj, myns_atr.se_encuentra_en, loc_obj))
            gr.add((plc_obj, myns_atr.tipo_de_actividad, Literal("Fiesta")))
            gr.add((plc_obj, myns_atr.tiene_como_horario, periodo))
            gr.add((plc_obj, myns_atr.es_ofrecido_por, compania))

            gr = build_message(gr,
                               ACL['inform-'],
                               sender=AgentePlanificador.uri,
                               msgcnt=mss_cnt,
                               receiver=msgdic['sender'])

        mss_cnt += 1

        return true

def buscar_actividades_externamente(destinationCity="Barcelona", destinationCountry="Spain", radius=20000):

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
        i = i + 1

    json_data = json.dumps(resultado)
    print json_data
    return json_data


if __name__ == '__main__':
    app.run(host=hostname, port=port)

    # Esperamos a que acaben los behaviors
    # ab1.join()