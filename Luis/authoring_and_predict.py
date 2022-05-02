####################################################################
#                  Version 3 Removing API REST					   # 
#                    and without linking ML and prebuilt entities  # 
#               Adding new utterances that fit the required model  #
####################################################################

# To run this sample, install the following modules.
# pip install azure-cognitiveservices-language-luis



# <Dependencies>
#from logging.handlers import DatagramHandler
#from multiprocessing.connection import Client
from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials
from functools import reduce



import json, time, uuid
import requests
import http.client, urllib.request, urllib.parse, urllib.error, base64


# </Dependencies>

def quickstart(): 

	# <VariablesYouChange>
    #Créez des variables pour stocker votre clé de création et les noms de vos ressources.
#	authoringKey = 'a096ee399422437b8cfec5816d91f92e'
#	authoringEndpoint = 'https://westeurope.api.cognitive.microsoft.com/'
	authoringKey = '44680094d70f4b22bc6fb194086ee9f8'
	authoringEndpoint = 'https://p10luisresource-authoring.cognitiveservices.azure.com/'
	predictionKey = '5fc4ccbb7dc04aa094934613afb5f55f'
#	predictionEndpoint = 'https://westeurope.api.cognitiveservices.azure.com/'
	predictionEndpoint = 'https://p10luisresource.cognitiveservices.azure.com/'
	# </VariablesYouChange>

	# <VariablesYouDontNeedToChangeChange>
	# We use a UUID to avoid name collisions.
    #Créez des variables pour stocker vos points de terminaison, le nom de l'application, la version et le nom de l'intention.
	appName = " FlyMe 2" + str(uuid.uuid4())
	versionId = "0.1"
	intentNames = ["BookFlight", "Greetings", "Confirmation"]
	# </VariablesYouDontNeedToChangeChange>

	# <AuthoringCreateClient>
    #Authentifier le client: Créez un objet CognitiveServicesCredentials avec votre clé et utilisez-le avec votre point de terminaison pour créer un objet LUISAuthoringClient.
	client = LUISAuthoringClient(authoringEndpoint, CognitiveServicesCredentials(authoringKey))
	# </AuthoringCreateClient>

	# Create app
	# get app id - necessary for all other changes

	app_id = create_app(client, appName, versionId)

	# <AddIntent>
#	client.model.add_intent(app_id, versionId, intentNames)
	for intent in intentNames:
			client.model.add_intent(app_id, versionId, intent)
	# </AddIntent>
	
	# Add Entities
	add_entities(client, app_id, versionId)
	#add_entities2(client, app_id, versionId)
	
	
	# Add labeled examples
	add_labeled_examples(client,app_id, versionId, intentNames)  # From Luis Documentation Examples
############       Working one but with no more than 100 http request from API REST###############
#	add_labeled_example_REST_APIs(app_id, authoringKey, versionId , authoringEndpoint) # New one to put a jsonfile but no more than 100 requests


	# <TrainAppVersion>
	client.train.train_version(app_id, versionId)
	waiting = True
	while waiting:
		info = client.train.get_status(app_id, versionId)

		# get_status returns a list of training statuses, one for each model. Loop through them and make sure all are done.
		waiting = any(map(lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
		if waiting:
			print ("Waiting 10 seconds for training to complete...")
			time.sleep(10)
		else: 
			print ("trained")
			waiting = False
	# </TrainAppVersion>

	
	# <PublishVersion>
	# Mark the app as public so we can query it using any prediction endpoint.
	# Note: For production scenarios, you should instead assign the app to your own LUIS prediction endpoint. See:
	# https://docs.microsoft.com/en-gb/azure/cognitive-services/luis/luis-how-to-azure-subscription#assign-a-resource-to-an-app
	client.apps.update_settings(app_id, is_public=True)
	print("Luis application is public")

	responseEndpointInfo = client.apps.publish(app_id, versionId, is_staging=False)
	print("Luis application is published ", responseEndpointInfo)
	# </PublishVersion>

############ Works but using REST_APIS and predictionEndpoint
#	test_luis_REST_APIs(app_id, predictionKey , predictionEndpoint)
#	print("Luis application test is done ")

######________________ Caution__________________________
#This quickstart uses the authoring key as as part of the runtime credentials. 
# The authoring key is allowed to query the runtime with a few queries. For staging and production-level code, 
# replace the authoring key with a prediction runtime key.

	# <PredictionCreateClient>
	runtimeCredentials = CognitiveServicesCredentials(authoringKey)
	clientRuntime = LUISRuntimeClient(endpoint=authoringEndpoint, credentials=runtimeCredentials)
	print("Prediction Client Created ")
	# </PredictionCreateClient>


    # <QueryPredictionEndpoint>
    # Production == slot name
	predictionRequest = { "query" : "Book a flight from Paris to New-York on March 18, 2022" }
	predictionResponse = clientRuntime.prediction.get_slot_prediction(app_id, "Production", predictionRequest)
	print("Top intent: {}".format(predictionResponse.prediction.top_intent))
	print("Sentiment: {}".format (predictionResponse.prediction.sentiment))
	print("Intents: ")

	for intent in predictionResponse.prediction.intents:
		print("\t{}".format (json.dumps (intent)))
	print("Entities: {}".format (predictionResponse.prediction.entities))
    # </QueryPredictionEndpoint>


	# Clean up resources.
#	print ("Deleting app...")
#	client.apps.delete(app_id)
#	print ("App deleted.")

def create_app(client, appName, versionId):

    # <AuthoringCreateApplication>
	# define app basics
    #description = "This is my first dummy LUIS application"
    #Une application LUIS stocke le modèle de traitement en langage naturel contenant les intentions, les entités et les exemples d'énoncés.
	appDefinition = ApplicationCreateObject (name=appName, initial_version_id=versionId, culture='en-us')
	# create app
    #Créez une méthode add pour l’objet AppsOperation afin de créer l’application. Le nom et la culture de la langue sont des propriétés obligatoires.
	app_id = client.apps.add(appDefinition)
	# get app id - necessary for all other changes
	print("Created LUIS app with ID {}".format(app_id))
	# </AuthoringCreateApplication>
	
	return app_id


def add_entities(client, app_id, versionId):

	# <AuthoringAddEntities>

	# define machine-learned entity
	# Add information into the model

	departure_name = "Departure"
	departure_id = client.model.add_entity(app_id, versionId, name=departure_name)
	print("{} simple entity created with id {}".format(departure_name, departure_id))
#	print(departure_name, " added")
#	departuremodelObject = client.model.get_entity(app_id, versionId, departure_id)

	destination_name = "Destination"
	destination_id = client.model.add_entity(app_id, versionId, name=destination_name)
	print("{} simple entity created with id {}".format(destination_name, destination_id))
#	print(destination_name, " added")
#	destinationmodelObject = client.model.get_entity(app_id, versionId, destination_id)


	departure_date_name ='DepartureDate' 
	departure_date_id = client.model.add_entity(app_id, versionId, name=departure_date_name)
	print("{} simple entity created with id {}".format(departure_date_name, departure_date_id))
#	print(departure_date_name, " added")
#	departure_datemodelObject = client.model.get_entity(app_id, versionId, departure_date_id)


	arrival_date_name ='ArrivalDate' 
	arrival_date_id = client.model.add_entity(app_id, versionId, name=arrival_date_name)
	print("{} simple entity created with id {}".format(arrival_date_name, arrival_date_id))
#	print(arrival_date_name, " added")
#	arrival_datemodelObject = client.model.get_entity(app_id, versionId, arrival_date_id)


	budget_name ='Budget' 
	budget_id = client.model.add_entity(app_id, versionId, name=budget_name)
	print("{} simple entity created with id {}".format(budget_name, budget_id))	
#	budgetmodelObject = client.model.get_entity(app_id, versionId, budget_id)


#######################################################################
#_______________________Prebuilt Entities______________________________
#######################################################################
	# Add Prebuilt entity
	prebuilt_extractor_names=["datetimeV2", "money", "geographyV2"]
	client.model.add_prebuilt(app_id, versionId, prebuilt_extractor_names)

	# add model as feature to subentity model

# #	prebuiltFeaturedDefinition = {"model_name": "money", "is_required": False}
# 	prebuiltFeatureRequiredDefinition = {"model_name": "money", "is_required": True}

	# client.features.add_entity_feature(app_id, versionId, budget_id, prebuiltFeatureRequiredDefinition)
	# print("{} prebuilt feature entity created with id {}".format(budget_name, budget_id))

	# Add model as feature to subentity model
	prebuiltFeaturedDefinition = {"model_name" : "geographyV2", "is_required": False}
	client.features.add_entity_feature(app_id, versionId, departure_id, prebuiltFeaturedDefinition)
	client.features.add_entity_feature(app_id, versionId, destination_id, prebuiltFeaturedDefinition)
	prebuiltFeaturedDefinition = {"model_name": "datetimeV2", "is_required": False}
	client.features.add_entity_feature(app_id, versionId, departure_date_id, prebuiltFeaturedDefinition)
	client.features.add_entity_feature(app_id, versionId, arrival_date_id, prebuiltFeaturedDefinition)
	prebuiltFeaturedDefinition = {"model_name": "money", "is_required": False}
	client.features.add_entity_feature(app_id, versionId, budget_id, prebuiltFeaturedDefinition)

#--------------> Part 1===Tryal1
	# prebuiltFeatureNotRequiredDefinition = { "model_name": "datetimeV2" }
	# client.features.add_entity_feature(app_id, versionId, departure_date_id, prebuiltFeatureNotRequiredDefinition)
	# print("{} prebuilt feature entity created with id {}".format(departure_date_name, departure_date_id))	
	# client.features.add_entity_feature(app_id, versionId, arrival_date_id, prebuiltFeatureNotRequiredDefinition)
	# print("{} prebuilt feature entity created with id {}".format(arrival_date_name, arrival_date_id))		



#--------------> Part 2 ====Trayal 2
	# prebuiltFeatureRequiredDefinition1  = { "model_name": "datetimeV2" , "is_required": True}
	# client.features.add_entity_feature(app_id, versionId, departure_date_id, prebuiltFeatureRequiredDefinition1)
	# print("{} prebuilt feature entity created with id {}".format(departure_date_name, departure_date_id))	
	# client.features.add_entity_feature(app_id, versionId, arrival_date_id, prebuiltFeatureRequiredDefinition1)
	# print("{} prebuilt feature entity created with id {}".format(arrival_date_name, arrival_date_id))	

	# prebuiltFeaturedDefinition = {"model_name": "geographyV2", "is_required": False}
	# client.features.add_entity_feature(app_id, versionId, departure_id, prebuiltFeaturedDefinition)
	# print("{} prebuilt feature entity created with id {}".format(departure_name, departure_id))	
	# client.features.add_entity_feature(app_id, versionId, destination_id, prebuiltFeaturedDefinition)
	# print("{} prebuilt feature entity created with id {}".format(destination_name, destination_id))	



#------> Comment: command K  puis command C
#------`> uncomment: command  K puis command U

#######################################################################
#__________________Phrase Lists (origin/destination)___________________
#######################################################################

	# define phraselist - add phrases as significant vocabulary to app
	# DestinationPhraseList = {
	# 	"enabledForAllModels": False,
	# 	"isExchangeable": True,
	# 	"name": "DestinationPhraseList",
	# 	"phrases": "to,arrive,land at,go,going,stay, heading"
	# }

	# # add phrase list to app
	# DestinationPhraseListId = client.features.add_phrase_list(app_id, versionId, DestinationPhraseList)


	# OriginPhraseList = {
	# 	"enabledForAllModels": False,
	# 	"isExchangeable": True,
	# 	"name": "OriginPhraseList",
	# 	"phrases": "start at, begin from, leave, on"
	# }

	# # add phrase list to app
	# OriginPhraseListId = client.features.add_phrase_list(app_id, versionId, OriginPhraseList)

	# # add phrase list as feature to subentity model
	# DestinationphraseListFeatureDefinition = { "feature_name": "DestinationPhraseList", "model_name": None }
	# client.features.add_entity_feature(app_id, versionId, destination_id, DestinationphraseListFeatureDefinition)
	# client.features.add_entity_feature(app_id, versionId, arrival_date_id, DestinationphraseListFeatureDefinition)

	# OriginphraseListFeatureDefinition = { "feature_name": "OriginPhraseList", "model_name": None }
	# client.features.add_entity_feature(app_id, versionId, departure_id, OriginphraseListFeatureDefinition)
	# client.features.add_entity_feature(app_id, versionId, departure_date_id, OriginphraseListFeatureDefinition)


def get_examples(json_file):
    with open(json_file, "r") as handle:
        file = json.load(handle)
    return file

def add_labeled_examples(client, app_id, versionId, intentNames):

	# <AuthoringAddLabeledExamples>
    # Define labeled example						
			
#	labeledExampleUtteranceWithMLEntity = get_examples("../data/train.json")
	labeledExampleUtteranceWithMLEntity = get_examples("../data/small_train.json")
	print("Labeled Example Utterance:   loaded")

    # Add an example for the entity.
    # Enable nested children to allow using multiple models with the same name.
	# The quantity subentity and the phraselist could have the same exact name if this is set to True
	for labeledExampleUtterance in labeledExampleUtteranceWithMLEntity:
		try:
#			print("\nutterance : ", labeledExampleUtterance)
			client.examples.add(app_id, versionId, labeledExampleUtterance, { "enableNestedChildren": False })
		except Exception as e:
#			print("\nutterance : ", labeledExampleUtterance)
			# Display the error string.
			print(f'{e}')
	print("client.examples = Labeled Example Utterance:   added")	

	greeting_utterances = [
        {
            "text": "Hello",
            "intentName": intentNames[1]
        },
        {
            "text": "Hi",
            "intentName": intentNames[1]
        },
		{
            "text": "Hey",
            "intentName": intentNames[1]
        },
		{
            "text": "G’day",
            "intentName": intentNames[1]
        },
        {
            "text": "Morning",
            "intentName": intentNames[1]
        },
        {
            "text": "Good morning",
            "intentName": intentNames[1]
        },
        {
            "text": "OK",
            "intentName": intentNames[1]
        },
		{
            "text": "good",
            "intentName": intentNames[1]
        }   
    ]
	for greeting_utterance in greeting_utterances:
		try:
#			print("\nutterance : ", greeting_utterance)
			client.examples.add(app_id, versionId, greeting_utterance, { "enableNestedChildren": False })
		except Exception as e:
#			print("\nutterance : ", greeting_utterance)
			# Display the error string.
			print(f'{e}')
	print("client.examples = Labeled Example greeting_utterance:   added")		

	confirmation_utterances = [
        {
            "text": "Yes",
            "intentName": intentNames[2]
        },
        {
            "text": "Ok",
            "intentName": intentNames[2]
        },
		{
            "text": "Right",
            "intentName": intentNames[2]
        },
		{
            "text": "Exact",
            "intentName": intentNames[2]
        },
		{
            "text": "Thanks",
            "intentName": intentNames[2]
        },
		{
            "text": "Good",
            "intentName": intentNames[2]
        }
	]
	for confirmation_utterance in confirmation_utterances:
		try:
#			print("\nutterance : ", confirmation_utterance)
			client.examples.add(app_id, versionId, confirmation_utterance, { "enableNestedChildren": False })
		except Exception as e:
#			print("\nutterance : ", confirmation_utterance)
			# Display the error string.
			print(f'{e}')
	print("client.examples = Labeled Example confirmation_utterance:   added")

# _____  Data corresponds to new occurences that need to be taken into account_______
	data = [
	{'text': "I want a trip budget of 5000 euros",
	'intentName': 'BookFlight',
	'entityLabels': [
	{'startCharIndex': 24,'endCharIndex': 34,'entityName': 'Budget'}]},

	{'text': "I have a two thousand dollars budget for this trip",
	'intentName': 'BookFlight',
	'entityLabels': [
	{'startCharIndex': 9,'endCharIndex': 29,'entityName': 'Budget'}]},

	{'text': 'I am looking to get away to greece on 21th of september and returning back on 15th of november',
	'intentName': 'BookFlight',
	'entityLabels': [
	{'startCharIndex': 28,'endCharIndex': 34,'entityName': 'Destination'},
	{'startCharIndex': 78,'endCharIndex': 94,'entityName': 'ArrivalDate'},
	{'startCharIndex': 38, 'endCharIndex': 55, 'entityName': 'DepartureDate'}]},

	{'text': 'Visit a country in Asia from 30-06-1999 to 01-01-2000',
	'intentName': 'BookFlight',
	'entityLabels': [
	{'startCharIndex': 19,'endCharIndex': 23,'entityName': 'Destination'},
	{'startCharIndex': 29, 'endCharIndex': 39, 'entityName': 'DepartureDate'},
	{'startCharIndex': 43,'endCharIndex': 53,'entityName': 'ArrivalDate'}
	]},

	{'text': 'Visit a country in Asia on 30/06/1999 and retrurning back on 01/01/2000',
	'intentName': 'BookFlight',
	'entityLabels': [
	{'startCharIndex': 19,'endCharIndex': 23,'entityName': 'Destination'},
	{'startCharIndex': 27, 'endCharIndex': 37, 'entityName': 'DepartureDate'},
	{'startCharIndex': 61,'endCharIndex': 71,'entityName': 'ArrivalDate'}
	]},

	{'text': 'Visit a country in Asia from 30/06/1999 to 01/01/2000',
	'intentName': 'BookFlight',
	'entityLabels': [
	{'startCharIndex': 19,'endCharIndex': 23,'entityName': 'Destination'},
	{'startCharIndex': 29, 'endCharIndex': 39, 'entityName': 'DepartureDate'},
	{'startCharIndex': 43,'endCharIndex': 53,'entityName': 'ArrivalDate'}
	]},

	{'text': 'I have a trip to Monaco leaving on 31/03/2022 and I return on 04/04/2022',
	'intentName': 'BookFlight',
	'entityLabels': [
	{'startCharIndex': 17,'endCharIndex': 23,'entityName': 'Destination'},
	{'startCharIndex': 35, 'endCharIndex': 45, 'entityName': 'DepartureDate'},
	{'startCharIndex': 62,'endCharIndex': 72,'entityName': 'ArrivalDate'}
	]},

	{'text': 'travel to Dubai on 20/03/2022 with 500€',
	'intentName': 'BookFlight',
	'entityLabels': [
	{'startCharIndex': 10,'endCharIndex': 15,'entityName': 'Destination'},
	{'startCharIndex': 19, 'endCharIndex': 29, 'entityName': 'DepartureDate'},
	{'startCharIndex': 35,'endCharIndex': 39,'entityName': 'Budget'}
	]},

	{'text': 'traveling to: Dubai from: Monaco on 30/03/2022 and returning on 15/04/2022 with a maximum budget of: 0€.',
	'intentName': 'BookFlight',
	'entityLabels': [
	{'startCharIndex': 12,'endCharIndex': 19,'entityName': 'Destination'},
	{'startCharIndex': 24,'endCharIndex': 32,'entityName': 'Departure'},
	{'startCharIndex': 36, 'endCharIndex': 46, 'entityName': 'DepartureDate'},
	{'startCharIndex': 64, 'endCharIndex': 74, 'entityName': 'ArrivalDate'},
	{'startCharIndex': 101,'endCharIndex': 103,'entityName': 'Budget'}
	]},	

	{'text': 'travel on 20/03/2022 and return back 30/03/2022 with 600$.',
	'intentName': 'BookFlight',
	'entityLabels': [
	{'startCharIndex': 10, 'endCharIndex': 20, 'entityName': 'DepartureDate'},
	{'startCharIndex': 37, 'endCharIndex': 47, 'entityName': 'ArrivalDate'},
	{'startCharIndex': 53,'endCharIndex': 57,'entityName': 'Budget'}
	]},	

	{'text': 'Travel between 27/03/2022 and 30-03-2022',
	'intentName': 'BookFlight',
	'entityLabels': [
	{'startCharIndex': 15, 'endCharIndex': 25, 'entityName': 'DepartureDate'},
	{'startCharIndex': 30,'endCharIndex': 40,'entityName': 'ArrivalDate'}
	]}
	]

	for my_utterance in data:
		try:
			client.examples.add(app_id, versionId, my_utterance, { "enableNestedChildren": False })
		except Exception as e:
				print(f'{e}')	
	print("client.examples = my own Labeled data :  added")




	# </AuthoringAddLabeledExamples>



def add_labeled_example_REST_APIs( appId, authoring_key, app_version, authoring_endpoint):
	#
	# This quickstart shows how to add utterances to a LUIS model using the REST APIs.
	#

	try:
		print("start adding utterances")

		data = get_examples("../data/small_train.json")	
		headers = {'Ocp-Apim-Subscription-Key': authoring_key}
		# The URL parameters to use in this REST call.
		params ={
			#'timezoneOffset': '0',
			#'verbose': 'true',
			#'show-all-intents': 'true',
			#'spellCheck': 'false',
			#'staging': 'false'
		}

		response = requests.post(f'{authoring_endpoint}luis/authoring/v3.0-preview/apps/{appId}/versions/{app_version}/examples', 
		headers=headers, params=params, data= json.dumps(data) )

		# Display the results on the console.
		print('Add the list of utterances:')
		print(response.json())

	except Exception as e:
		    # Display the error string.
			print(f'{e}')

def test_luis_REST_APIs( appId, predictionKey, predictionEndpoint):
	#
	# This quickstart shows how to add utterances to a LUIS model using the REST APIs.
	#

	try:
		print("start testing")		
		#data = get_examples("../data/train.json")	
		headers = {'Ocp-Apim-Subscription-Key': predictionKey}
		app_version = "v3.0"
		# The URL parameters to use in this REST call.
		params ={
			#'timezoneOffset': '0',
			'verbose': 'true',
			'show-all-intents': 'true',
			#'spellCheck': 'false',
			#'staging': 'false'
		}
		predictionRequest = { "query" : " Book a flight from Paris to New-York on March 18, 2022" }
		# Make the REST call to initiate a training session.

		predictionResponse = requests.post(f'{predictionEndpoint}luis/prediction/v3.0/apps/7cf18177-348e-4169-9758-f00f086bb603/slots/production/predict', 
		headers=headers, params=params, data= json.dumps(predictionRequest))	

		# Display the results on the console.
		print('Request testing status:')
		print(predictionResponse.json())


		print("\n\nQUERY: ",predictionResponse.json()['query'])
		print("\n\nTop intent: {}".format(predictionResponse.json()['prediction']['topIntent'] ))
		#print("Sentiment: {}".format (predictionResponse.json()['prediction']sentiment))
		print("\n\nIntents: \n", predictionResponse.json()['prediction']['intents'])

		#for intent in predictionResponse['prediction']['intents']:
		#	print("\t{}".format (json.dumps (intent)))
		for key, value in  predictionResponse.json()['prediction']['entities'].items(): 
			    print("\n", key,':', value)
	except Exception as e:
		    # Display the error string.
			print(f'{e}')


# <AuthoringSortModelObject>
def get_grandchild_id(model, childName, grandChildName):
	
	theseChildren = next(filter((lambda child: child.name == childName), model.children))
	theseGrandchildren = next(filter((lambda child: child.name == grandChildName), theseChildren.children))
	
	grandChildId = theseGrandchildren.id
	
	return grandChildId
# </AuthoringSortModelObject>




quickstart()