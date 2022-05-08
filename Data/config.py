import os

class DefaultConfig:
    """ App Configuration """

 #   AUTHORING_KEY = os.environ.get("authoringKey", "")
 #   AUTHORING_ENDPOINT = os.environ.get("authoringEndpoint", "https:")
    PREDICTION_KEY = os.environ.get("predictionKey", "5fc4ccbb7dc04aa094934613afb5f55f")
    PREDICTION_ENDPOINT = os.environ.get("predictionEndpoint", "https://p10luisresource.cognitiveservices.azure.com/")
    LUIS_APP_ID = os.environ.get("LuisAppId", "fe2ea595-12f7-494c-8737-bc881341be54")                                        