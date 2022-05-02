import argparse
#from this import d
import time
import os
import json
import re


def load_file(file_name):
    '''Lecture d'un fichier json'''
    with open(file_name) as json_file:
        file = json.load(json_file)
    return file



def is_float_digit(n: str) -> bool:
    ''' Vérifier s'il est convertible à un float '''
    try:
        float(n)
        return True
    except ValueError:
         return False


def extract_json_utterances(data):

    labeledExampleUtteranceWithMLEntity = []

    for index in range(len(data)):

        utterance = {}
        text = data[index]['turns'][0]['text']
        intentName = "BookFlight"
        if text :
            utterance['text'] = text
            utterance['intentName'] = intentName
            utterance["entityLabels"] = []

            ##  Rajouter les paramètres d'entity labels à savoir startCharIndex, endCharIndex et entityName  ##

            # Travail concernant l'entité Départ
            if 'or_city' in data[index]['turns'][0]["labels"]["frames"][0]["info"].keys() :
                word = data[index]['turns'][0]["labels"]["frames"][0]["info"]['or_city'][0]['val']
                if text.lower().find(word.lower()) !=-1 :
                    word_startCharIndex = text.lower().find(word.lower())
                    word_endCharIndex = word_startCharIndex+len(word)-1
                    utterance['entityLabels'].append({"startCharIndex": word_startCharIndex,
                                                                    "endCharIndex": word_endCharIndex,
                                                                    "entityName": "Departure"})
        
             # Travail concernant l'entité Destination
            if 'dst_city' in data[index]['turns'][0]["labels"]["frames"][0]["info"].keys() :
                word = data[index]['turns'][0]["labels"]["frames"][0]["info"]['dst_city'][0]['val']
                if text.lower().find(word.lower()) !=-1 :
                    word_startCharIndex = text.lower().find(word.lower())
                    word_endCharIndex = word_startCharIndex+len(word)-1
                    utterance['entityLabels'].append({"startCharIndex": word_startCharIndex,
                                                                        "endCharIndex": word_endCharIndex,
                                                                        "entityName": "Destination"})    

        
            # Travail concernant l'entité Date de départ
            if 'str_date' in data[index]['turns'][0]["labels"]["frames"][0]["info"].keys() :
                word = data[index]['turns'][0]["labels"]["frames"][0]["info"]['str_date'][0]['val']
                if text.lower().find(word.lower()) !=-1 :
                    word_startCharIndex = text.lower().find(word.lower())
                    word_endCharIndex = word_startCharIndex+len(word)-1
                    utterance['entityLabels'].append({"startCharIndex": word_startCharIndex,
                                                                        "endCharIndex": word_endCharIndex,
                                                                        "entityName": "DepartureDate"})     
            # Travail concernant l'entité Date d'arrivée
            if 'end_date' in data[index]['turns'][0]["labels"]["frames"][0]["info"].keys() :
                word = data[index]['turns'][0]["labels"]["frames"][0]["info"]['end_date'][0]['val']
                if text.lower().find(word.lower()) !=-1 :
                    word_startCharIndex = text.lower().find(word.lower())
                    word_endCharIndex = word_startCharIndex+len(word)-1
                    utterance['entityLabels'].append({"startCharIndex": word_startCharIndex,
                                                                        "endCharIndex": word_endCharIndex,
                                                                        "entityName": "ArrivalDate"})             
        
            # Travail concernant l'entité Budget
            if 'budget' in data[index]['turns'][0]["labels"]["frames"][0]["info"].keys() :
                word = data[index]['turns'][0]["labels"]["frames"][0]["info"]['budget'][0]['val']
                #Done to check if the budget in the json is different from text because of float type
    #             if text.find(word) ==-1 :
    #                 if text.find(word.replace('.', ',')) !=-1 :
    #                     word = word.replace('.', ',')
    #                 elif (is_float_digit(word) ):
    # #                    z = [float(s) for s in re.findall(r'-?\d+\.\d*', text)]
    # #                    if len(z) != 0 :
    # #                        word =[int(x) for i,x in enumerate(z) if x == float(word)][0]
    # #                        word = str(word)
    #                     if (text.find(str(int(float(word)))) !=-1 ):
    #                         word = str(int(float(word)))                
#                if text.find(word) !=-1 :
                if text.lower().find(word.lower()) !=-1 :
                    word_startCharIndex = text.lower().find(word.lower())
                    word_endCharIndex = word_startCharIndex+len(word)-1
                    utterance['entityLabels'].append({"startCharIndex": word_startCharIndex,
                                                                    "endCharIndex": word_endCharIndex,
                                                                    "entityName": "Budget"})   
        
        labeledExampleUtteranceWithMLEntity.append(utterance)

    return labeledExampleUtteranceWithMLEntity



def main():

    # Load the Frames Dataset
    print("##############\nLoad data")
    
    data = load_file("frames.json")

    # Generate relevant json data for Luis application
    print("##############\nGenerate relevant json data")
    labeledExampleUtteranceWithMLEntity = extract_json_utterances(data)
    print (len (labeledExampleUtteranceWithMLEntity))


    # Create necessary json files for the train and test as well a small dataset for rapid use and Luis requests limit
    train_test_split_ratio = 0.7
    train_labeledExampleUtteranceWithMLEntity = labeledExampleUtteranceWithMLEntity[: int( len(labeledExampleUtteranceWithMLEntity) * train_test_split_ratio ) ]
    test_labeledExampleUtteranceWithMLEntity = labeledExampleUtteranceWithMLEntity[int( len(labeledExampleUtteranceWithMLEntity) * train_test_split_ratio ) :]
    print("taille train", len (train_labeledExampleUtteranceWithMLEntity))
    print("taille test", len (test_labeledExampleUtteranceWithMLEntity))

    with open("./train.json", "w") as handle:
        json.dump(train_labeledExampleUtteranceWithMLEntity, handle)
    with open("./test.json", "w") as handle:
        json.dump(test_labeledExampleUtteranceWithMLEntity, handle)
    with open("./small_train.json", "w") as handle:
        json.dump(train_labeledExampleUtteranceWithMLEntity[:50], handle)
    print("##############\nTrain and test files are created")


if __name__ == "__main__":
    main()