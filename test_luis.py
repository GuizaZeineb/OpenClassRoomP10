import argparse
import time
import os
import json
import re


#from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
#from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
#from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
#from msrest.authentication import CognitiveServicesCredentials
#from functools import reduce



#import json, time, uuid
#import requests
#import http.client, urllib.request, urllib.parse, urllib.error, base64


#from Data.performance import test_luis_REST_APIs 
from performance import test_luis_REST_APIs 

def test_luis_prediction_bookflight():
    query ="travel on 30/03/2022 and return on 30/04/2022 from Paris to Maldives with 5000£ "
    reply = test_luis_REST_APIs(query)
    assert reply["prediction"]["topIntent"] == "BookFlight"
    assert reply["prediction"]["entities"]["Departure"] == "Paris"
    assert reply["prediction"]["entities"]["Destination"] == "Maldives"
    assert reply["prediction"]["entities"]["DepartureDate"] == "30/03/2022"
    assert reply["prediction"]["entities"]["ArrivalDate"] == "30/04/2022"
    assert reply["prediction"]["entities"]["$instance"]["money"][0]['text'] == "5000£"
