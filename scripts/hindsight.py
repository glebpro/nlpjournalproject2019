
#
#   Use `hindsight.` to record your notes through a journalling conversation.
#
#   Run ./step_ibm_enviornment.sh first and add credentials at the bottom.
#
#   Usage: python hindsight.py
#
#   Authors: Gleb Promokhov @glebpro
#            Joseph Agnelli @LambStack
#

import os
import re
import json
import sys
import pickle


from watson_developer_cloud import DiscoveryV1 # https://cloud.ibm.com/apidocs/discovery?language=python
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions
from watson_developer_cloud import AssistantV2
from watson_developer_cloud.watson_service import WatsonApiException

class Hindsight(object):

    def __init__(self, API_KEY, URL, enviornment_id, collection_id, NLU_API_KEY, NLU_URL, ASSISTANT_API_KEY, ASSISTANT_URL, ASSISSTANT_ID):
        '''
        Initialize a hindsight chatbot

        :param API_KEY: IBM Watson Discovery API Key
        :param URL: IBM Watson Discovery base url
        :param enviornment_id: IBM Enviornment id
        :param collection_id: IBM document collection id
        :return:
        '''
        self.chat_states = {
            'add_mode': 1,
            'ask_mode': 2
        }

        self.intents = {
            'show_notes'     : 1,
            'summarize_notes': 2,
            'sentiment_notes': 3
        }

        self.state = self.chat_states['add_mode']
        self.prompt = '>>> '
        self.chatprompt = '\t~~~ '
        self.state_prompt = 'Add a note: '

        self.discovery = DiscoveryV1(
            version = '2018-12-03',
            iam_apikey = API_KEY,
            url = URL
        )

        self.nlu = NaturalLanguageUnderstandingV1(
            version='2018-11-16',
            iam_apikey=NLU_API_KEY,
            url= NLU_URL
        )


        self.assistant = AssistantV2(
            version='2018-11-08',
            iam_apikey = ASSISTANT_API_KEY,
            url= ASSISTANT_URL
        )

        self.session_id = self.assistant.create_session(
            assistant_id = ASSISSTANT_ID
        ).get_result()['session_id']

        self.enviornment_id = enviornment_id
        self.collection_id = collection_id
        self.assistant_id = ASSISSTANT_ID

        self.ROOT_PATH = sys.path[0]

        self.METADATA_PATH = self.ROOT_PATH+'/notes_metadata'
        if not os.path.exists(self.METADATA_PATH):
            os.makedirs(self.METADATA_PATH)

        self.GLOBAL_ENTITIES = self.ROOT_PATH+'/notes_metadata/global_entities.p'
        if not os.path.exists(self.GLOBAL_ENTITIES):
            t = { 'NULL': 0 }
            pickle.dump(t, open(self.GLOBAL_ENTITIES, "wb"))

        self.GLOBAL_DOC_IDS = self.ROOT_PATH+'/notes_metadata/global_doc_ids.p'
        if not os.path.exists(self.GLOBAL_DOC_IDS):
            t = { 'NULL': '/' }
            pickle.dump(t, open(self.GLOBAL_DOC_IDS, "wb"))

        self.NOTES_PATH = self.ROOT_PATH+'/notes.html'
        if not os.path.exists(self.NOTES_PATH):
            os.makedirs(self.NOTES_PATH)

        self.INTENT_LINES = []
        if not os.path.exists(self.ROOT_PATH+'/intent_training_data.csv'):
            print('!!! ERROR: ./scripts/intent_training_data.csv required')
            quit()
        lines = open(self.ROOT_PATH+'/intent_training_data.csv').readlines()
        self.INTENT_LINES = [l.strip().split(',')[0] for l in lines]

    def hello(self):
        '''
        Introductory Message
        '''
        print('\n')
        print('~~~~~~~~~~~~~~~~~~~~~')
        print('`hindsight`. A journalling application.')
        print("commands: \n\t/add to enter 'add note' mode, \n\t/ask to enter 'query notes' mode, \n\t/quit to quit")
        print('~~~~~~~~~~~~~~~~~~~~~')
        print('\n')

    def chat(self):
        '''
        Start chat loop.
        '''

        # preprocess text for API input
        # crudely remove training data phrases to get 'non-intent' part of input
        def _scrubHindsightIntentQueryText(raw_input):
            pattern = re.compile("\\b("+'|'.join(self.INTENT_LINES)+")\\W", re.I)
            result = raw_input.strip().lower()
            result = pattern.sub("", result)
            return result

        def _summarizeNotesRoutine(query_text):
            response = self.discovery.query(self.enviornment_id, self.collection_id,
                                            natural_language_query = query_text,
                                            count=1000)

            results = [result_doc["html"] for result_doc in response.result["results"]]

            # SUMMARIZE_HERE

            return results

        def _showNotesRoutine(query_text):
            response = self.discovery.query(self.enviornment_id, self.collection_id,
                                    natural_language_query = query_text,
                                    count=5 )

            results = [result_doc["text"] for result_doc in response.result["results"]]
            return results

        def _sentimentNotesRoutine(query_text):
            response = self.discovery.query(self.enviornment_id, self.collection_id,
                        natural_language_query = query_text,
                        count=5 )

            sentiments = [result_doc["enriched_text"]["sentiment"]["document"]["score"] for result_doc in response.result["results"]]
            avg_sentiment = sum(sentiments)/len(sentiments)
            result = []

            if -0.75 > avg_sentiment:
                result.append("Your notes show that you feel terrible about that!")
            if -0.50 < avg_sentiment and avg_sentiment < -0.25:
                result.append("Your notes show that you feel pretty bad about that!")
            if -0.25 < avg_sentiment and avg_sentiment < 0:
                result.append("Your notes show that you don't feel to bad about that.")
            if 0 < avg_sentiment and avg_sentiment < .25:
                result.append("Your notes show that you feel pretty OK about that.")
            if .25 < avg_sentiment and avg_sentiment < .5:
                result.append("Your notes show that you feel well and good about that.")
            if .5 < avg_sentiment and avg_sentiment < .75:
                result.append("Your notes show that you feel really happy about that!")
            if .75 < avg_sentiment:
                result.append("Your notes show that you feel really fantastic about that!")

            return result

        raw_input = str(input(self.prompt + self.state_prompt))

        if raw_input == '/quit':
            return 1

        elif raw_input == '/add':
            self.state = self.chat_states['add_mode']
            self.state_prompt = 'Add a note: '

        elif raw_input == '/ask':
            self.state = self.chat_states['ask_mode']
            self.state_prompt = 'Ask your notes: '

        else:

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ COLLECTION status block
            # THIS CALL is very slow
            # document_processing_percent = self.get_collection_status()
            # if document_processing_percent < 100.0:
            #     print(self.chatprompt+"Not done processing notes, please wait...")
            #     print(self.chatprompt+"Only "+document_processing_percent+" % done...")
            #     self.chat()

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ADD mode
            if self.state == self.chat_states['add_mode']:

                # CATCH and RESPOND to 'to little text error' here
                result = self.add_note(raw_input)

                if result != 1:
                    print(self.chatprompt+"Something went wrong...")

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ASK mode
            elif self.state == self.chat_states['ask_mode']:

                # what is the user intented to do?
                intent = self.parse_ask_intent(raw_input)

                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ hindsight intents
                # if a hindsight intent
                if intent in list(self.intents.keys()):

                    query_text = _scrubHindsightIntentQueryText(raw_input)

                    if intent == "summarize_notes":
                        results = _summarizeNotesRoutine(query_text)
                    if intent == "show_notes":
                        results = _showNotesRoutine(query_text)
                    if intent == "sentiment_notes":
                        results = _sentimentNotesRoutine(query_text)

                    print(self.chatprompt+"Here are some results...")

                    for idx, r in enumerate(results):
                        print("%s: %s" % (idx, r))

                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ IBM + catchall intents

                # goodbye/ending intent
                elif intent == "General_Ending":
                    print(self.chatprompt+'All right then, goodbye!')
                    return 1

                # else use default response
                else:
                    print(self.chatprompt+'I am note sure what you mean...')

        self.chat()

    def parse_ask_intent(self, raw_input):

        input = raw_input.strip()

        # TODO hard match on training data

        response = self.assistant.message(
            assistant_id=self.assistant_id,
            session_id=self.session_id,
            input={
                'message_type': 'text',
                'text': input
            }
        ).get_result()

        # print(json.dumps(response, indent=2))

        return response["output"]["intents"][0]["intent"]

    def add_note(self, note_text):

        '''
        Add `note_text` to given local document by `title`.
        If `title` document not present, create LOCAL file.
        '''

        sentences = re.split("[.?!]", note_text.strip(".?!"))
        global_entities = pickle.load( open( self.GLOBAL_ENTITIES, "rb" ) )
        best_entity = 'NULL'

        # consider new entities
        # match note with highest occuring entity
        for sentence in sentences:
            entities = self.find_entities(sentence)
            if entities == -1:
                return -1

            for entity in entities:

                if entity not in list(global_entities.keys()):
                    global_entities[entity] = 0
                global_entities[entity] += 1

                if global_entities[entity] >= global_entities[best_entity]:
                    best_entity = entity

        # keep track of entities locally
        pickle.dump(global_entities, open( self.GLOBAL_ENTITIES, "wb" ) )
        print((note_text[:100]+'...') if len(note_text) > 100 else note_text)
        print("\t%s %s\n" % (best_entity, global_entities[best_entity]))

        # save note to local path
        best_entity = re.sub(' ', '_', best_entity)
        note_path = self.METADATA_PATH + '/' + best_entity + '.html'
        with open(note_path, 'a') as note:
            note.write(note_text + '\n\n')

        # send note to the cloud
        # print(best_entity, global_entities[best_entity])
        self.add_note_file(best_entity, note_path)

        return 1

    def find_entities(self, text):
        '''
        Find all the entites in a given string
        :param text: the string to find the entities
        :return string array: an array of all the entities as
        '''
        try:
            response = self.nlu.analyze(
                text=text,
                features=Features(
                    entities=EntitiesOptions(emotion=False, sentiment=False),
                    keywords=KeywordsOptions(emotion=False, sentiment=False)))

        except WatsonApiException as e:
            print("!!! WARNING: ", e)
            return -1

        list_of_keywords = [];
        for item in response.result["keywords"]:
            list_of_keywords.append(item["text"])

        return list_of_keywords

    def add_note_file(self, title, file_path):
        '''
        Add note to collection from file.

        :param file_path: absolute filepath to document file
        :return boolean: document_id if succeded upload, -1 otherwise
        '''

        # if previous 'title' already in collection, update to more recent local file
        # otherwise create new document in collection
        # use global_doc_ids.p to keep track of IBM doc_ids, since API  doesn't allow search by doc name...
        global_doc_ids = pickle.load( open( self.GLOBAL_DOC_IDS, "rb" ) )

        source = open(file_path)

        if title in global_doc_ids.keys():
            result = self.discovery.update_document(self.enviornment_id, self.collection_id, global_doc_ids[title],
                                                    file=source )
        else:
            result = self.discovery.add_document(self.enviornment_id, self.collection_id,
                                        file=source,
                                        filename=title+'.html',
                                        metadata="{ \"Title\": \""+title+"\" }" )
            global_doc_ids[title] = result.result['document_id']
            pickle.dump(global_doc_ids, open( self.GLOBAL_DOC_IDS, "wb" ) )

        if result.status_code != 202:
            print(result)
            print("!!! ERROR: Failed to upload document: %s" % file_path)
            return -1

        return result.result['document_id']

    def get_collection_status(self):
        response = self.discovery.get_collection(self.enviornment_id, self.collection_id).get_result()
        # print(json.dumps(response, indent=2))
        return round( (response["document_counts"]["available"] / (response["document_counts"]["processing"] + response["document_counts"]["available"])) * 100 , 2 )

if __name__ == "__main__":

    API_KEY= ""
    URL= "https://gateway.watsonplatform.net/discovery/api"
    enviornment_id = ""
    collection_id = ""


    NLU_API_KEY = ""
    NLU_URL = "https://gateway.watsonplatform.net/natural-language-understanding/api"

    ASSISTANT_KEY = ""
    ASSISTANT_URL = ""
    ASSISSTANT_ID = ""
    
    bot = Hindsight(API_KEY, URL, enviornment_id, collection_id, NLU_API_KEY, NLU_URL, ASSISTANT_KEY, ASSISTANT_URL, ASSISSTANT_ID)
    bot.hello()

    bot.chat()

    # print(pickle.load( open( bot.GLOBAL_ENTITIES, "rb" ) ))


    # def add_mode_file_input(path, bot):
    #     '''
    #     Add every line from file as 'add note' conversation input.
    #
    #     :param path: filepath to document file or folder
    #     '''
    #     lines = []
    #     if os.path.isfile(path):
    #         lines += open(path).readlines()
    #     else:
    #         for f in [entry for entry in os.listdir(path) if os.path.isfile(os.path.join(path,entry))]:
    #             print("reading: %s" % f)
    #             lines += open(path+f).readlines()
    #     for l in lines:
    #         bot.add_note(l.strip())
    #
    # add_mode_file_input(bot.ROOT_PATH+"/../data/tcse_data/", bot)
