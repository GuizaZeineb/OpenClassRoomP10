import argparse
import time
import os
import json
import re
import numpy as np
import pytest




from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from functools import reduce

import numpy as np
import json, time, uuid
import requests
import http.client, urllib.request, urllib.parse, urllib.error, base64


def load_file(file_name):
    '''Lecture d'un fichier json'''
    with open(file_name) as json_file:
        file = json.load(json_file)
    return file

@pytest.fixture
def test_luis_REST_APIs(query):
	#
	# This quickstart shows how to add utterances to a LUIS model using the REST APIs.
	#
	try:
		appId = "fe2ea595-12f7-494c-8737-bc881341be54" #"af053a5d-6c77-4755-90a2-590d1044c0e6"
		predictionKey = "5fc4ccbb7dc04aa094934613afb5f55f"
		predictionEndpoint = "https://p10luisresource.cognitiveservices.azure.com/"
		headers = {'Ocp-Apim-Subscription-Key':predictionKey }#predictionKey
		app_version = "v3.0"
		# The URL parameters to use in this REST call.
		params ={
			#'timezoneOffset': '0',
			'verbose': 'true',
			'show-all-intents': 'true',
			#'spellCheck': 'false',
			#'staging': 'false'
		}
#		predictionRequest = { "query" : " Book a flight from Paris to New-York on March 18, 2022" }
		predictionRequest = { "query" : query }

		# Make the REST call to initiate a training session.

		predictionResponse = requests.post(f'{predictionEndpoint}luis/prediction/v3.0/apps/{appId}/slots/production/predict', 
headers=headers, params=params, data= json.dumps(predictionRequest))	

		# Display the results on the console.
		#print('Request testing status:')
		return (predictionResponse.json())
	except Exception as e:
		    # Display the error string.
			print(f'{e}')




def extract_performance(data):

    performance = []
    accuracy =[]
    nb0,nb1,nb2,nb3,nb4,nb5=0,0,0,0,0,0

    for utterance in data:       
        #_________________Intent & Entities Extraction for Test
        query = utterance["text"]
        test_intent = None
        test_Departure = None
        test_Destination = None
        test_Departure_date = None
        test_Arrival_date = None
        test_Budget = None
        if utterance['intent'] == "BookFlight":
            test_intent = "BookFlight"
            nb0 +=1
        for entity in utterance['entities']:
            if entity['entity'] == "Departure":
                test_Departure = query[entity["startPos"]:(entity["endPos"]+1)] 
                nb1 +=1
            if entity['entity'] == "Destination":
                test_Destination = query[entity["startPos"]:(entity["endPos"]+1)]
                nb2 +=1
            if entity['entity'] == "DepartureDate":
                test_Departure_date = query[entity["startPos"]:(entity["endPos"]+1)]
                nb3 +=1
            if entity['entity'] == "ArrivalDate":
                test_Arrival_date = query[entity["startPos"]:(entity["endPos"]+1)]
                nb4 +=1
            if entity['entity'] == "Budget":
                test_Budget = query[entity["startPos"]:(entity["endPos"]+1)]
                nb5 +=1
                

        #_________________Intent & Entities Extraction after Prediction
        reply = test_luis_REST_APIs(query)
        try :
            #prediction_topIntent = reply["prediction"]["topIntent"]
            prediction_entities = reply["prediction"]["entities"]
            prediction_intent = None
            prediction_Departure = None
            prediction_Destination = None
            prediction_Departure_date = None
            prediction_Arrival_date = None
            prediction_Budget = None
            if len(prediction_entities)!=0:
                prediction_intent = reply["prediction"]['topIntent']
                if "Departure" in prediction_entities:
                    prediction_Departure = prediction_entities["Departure"][0]
                if "Destination" in prediction_entities:
                    prediction_Destination = prediction_entities["Destination"][0] 
                if "DepartureDate" in prediction_entities:
                    prediction_Departure_date= prediction_entities["DepartureDate"][0]
                if "ArrivalDate" in prediction_entities:
                    prediction_Arrival_date = prediction_entities["ArrivalDate"][0]
    #            if "Budget" in prediction_entities:
    #                prediction_Budget = prediction_entities["Budget"][0]
    #            if "money" in prediction_entities:

    #            if "builtin.currency" in prediction_entities:
    #                prediction_Budget = prediction_entities["money"][0]
    
                if "money" in prediction_entities["$instance"]:
                    prediction_Budget = prediction_entities["$instance"]["money"][0]['text'] 
            #--------Calcul d'accuracy à chaque utterance_____#
            # Top Intent| Departure| Destination \ Departure Date \ Arrival Date \ Budget
            Intent, Departure, Destination, Departure_Date, Arrival_Date , Budget = 0,0,0,0,0,0
            if prediction_intent == test_intent and prediction_intent!=None:
                Intent=1
            if prediction_Departure == test_Departure and prediction_Departure!=None:
                Departure=1
            if prediction_Destination == test_Destination and prediction_Destination!=None:
                Destination=1
            if prediction_Departure_date == test_Departure_date and prediction_Departure_date!=None:
                Departure_Date=1
            if prediction_Arrival_date == test_Arrival_date and prediction_Arrival_date!=None:
                Arrival_Date=1
    #        if prediction_Budget == test_Budget and prediction_Budget!=None:
            if prediction_Budget!=None and prediction_Budget.find(test_Budget) !=-1 :
                Budget=1
            z = Intent, Departure, Destination, Departure_Date, Arrival_Date , Budget
            accuracy.append(z)
        except Exception as e:
            print(e)


    #print("accuracy : ", accuracy)    
    values = np.sum(accuracy, axis=0)*100
    nb =[nb0, nb1, nb2, nb3, nb4, nb5]
    #performance = [[m/n for m, n in zip(values, nb)]]
    performance =[values[0]/nb0, values[1]/nb1, values[2]/nb2, values[3]/nb3, values[4]/nb4, values[5]/nb5]
    #print("\nAccuracy Top Intent ", performance[0], "%","\nAccuracy Departure ", performance[1], "%","\nAccuracy Destination ", performance[2], "%", 
    #     "\nAccuracy Departure_Date ", performance[3], "%","\nAccuracy Arrival_Date ", performance[4], "%","\nAccuracy Budget ", performance[5], "%")

    return performance

def save_performance(performance):
    performance_array = np.array(performance)

    # Displaying the array

    file = open("performance.txt", "w+")

    # Saving the array in a text file
    content = str(performance_array)
    file.write(content)
    file.close()

    # Displaying the contents of the text file
    file = open("performance.txt", "r")
    content = file.read()

    print("Array contents in performance.txt: ", content)
    file.close()


def main():

    # Load the Frames Dataset
    print("##############\nLoad data")
    data = load_file("test_final_20.json")

    # Config : Luis Credentials
    #CONFIG = DefaultConfig()

    # appId = "fe2ea595-12f7-494c-8737-bc881341be54" #"af053a5d-6c77-4755-90a2-590d1044c0e6"
    # predictionKey = "5fc4ccbb7dc04aa094934613afb5f55f"
    # predictionEndpoint = "https://p10luisresource.cognitiveservices.azure.com/"

    # Calculate the accuracy performance
    print("##############\nCalculate Luis Performance")
    performance = extract_performance(data)

    # Print the accurace Performance
    print("\nAccuracy Top Intent ", performance[0], "%","\nAccuracy Departure ", performance[1], "%",
    "\nAccuracy Destination ", performance[2], "%", "\nAccuracy Departure_Date ", performance[3], "%",
    "\nAccuracy Arrival_Date ", performance[4], "%","\nAccuracy Budget ", performance[5], "%")

    # save the accuracy performance
    save_performance(performance)

if __name__ == "__main__":
    main()
