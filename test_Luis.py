import argparse
import time
import os
import json
import re
import pytest


from Data.performance import test_luis_REST_APIs 


@pytest.fixture
def my_query():
    return "travel on 30/03/2022 and return on 30/04/2022 from Paris to Maldives with 5000£ "

#def test_luis_prediction_bookflight():
def test_luis_prediction_bookflight(my_query):

    #query ="travel on 30/03/2022 and return on 30/04/2022 from Paris to Maldives with 5000£ "
    reply = test_luis_REST_APIs(my_query)
    assert reply["prediction"]["topIntent"] == "BookFlight"
    assert reply["prediction"]["entities"]["Departure"] [0] == "Paris"
    assert reply["prediction"]["entities"]["Destination"] [0]== "Maldives"
    assert reply["prediction"]["entities"]["DepartureDate"] [0]== "30/03/2022"
    assert reply["prediction"]["entities"]["ArrivalDate"] [0]== "30/04/2022"
    assert reply["prediction"]["entities"]["$instance"]["money"][0]['text'] == "5000£"
