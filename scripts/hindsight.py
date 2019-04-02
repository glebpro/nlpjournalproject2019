
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


from watson_developer_cloud import DiscoveryV1 # https://cloud.ibm.com/apidocs/discovery?language=python
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 \
    import Features, EntitiesOptions, KeywordsOptions
from watson_developer_cloud import AssistantV2

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
            'ask_notes'      : 1,
            'summarize_notes': 2
        }

        self.state = self.chat_states['add_mode']
        self.prompt = '>>> '
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

        self.NOTES_PATH = self.ROOT_PATH+'/notes.html'
        if not os.path.exists(self.NOTES_PATH):
            os.makedirs(self.NOTES_PATH)

        self.INTENT_LINES = []
        if not os.path.exists(self.ROOT_PATH+'/intent_training_data.csv'):
            print('!!! ERROR: ./scripts/intent_training_data.csv required')
            quit()
        lines = open(self.ROOT_PATH+'/intent_training_data.csv').readlines()
        lines = [l.strip().split(',')[0] for l in lines]
        self.INTENT_LINES = lines

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

            response = ''

            # ADD mode
            if self.state == self.chat_states['add_mode']:
                self.add_note(raw_input)

            # ASK mode
            elif self.state == self.chat_states['ask_mode']:

                # what is the user intented to do?
                intent = self.parse_ask_intent(raw_input)

                # if a hindsight intent
                if intent in list(self.intents.keys()):

                    query_text = _scrubHindsightIntentQueryText(raw_input)

                    if intent == "summarize_notes":

                        response = self.discovery.query(self.enviornment_id, self.collection_id,
                                                        natural_language_query = query_text,
                                                        count=1000)

                        #SUMMARIZE

                        # print(response)


                    if intent == "ask_notes":
                        response = self.discovery.query(self.enviornment_id, self.collection_id,
                                                        natural_language_query = query_text,
                                                        passages_count = notes_count,
                                                        sort="-time",
                                                        highlight=True,
                                                        count=5)

                # goodbye/ending intent
                elif intent == "General_Ending":
                    print('All right then, goodbye!')
                    return 1

                # else use default response
                else:
                    print('I am note sure what you mean...')

        self.chat()

    def parse_ask_intent(self, raw_input):

        input = raw_input.strip()

        response = self.assistant.message(
            assistant_id=self.assistant_id,
            session_id=self.session_id,
            input={
                'message_type': 'text',
                'text': input
            }
        ).get_result()

        print(json.dumps(response, indent=2))

        return response["output"]["intents"][0]["intent"]

    def add_note(self, note_text):

        '''
        Add `note_text` to given document by `title`.
        If `title` document not present, create a new one.
        '''

        # TODO: way to force all notes into specific title, skip parsing

        files_to_upload = []
        sentences = re.split("[.?!]", note_text.strip(".?!"))

        for sentence in sentences:

            #write the note to the 'notes.html' file
            with open(self.NOTES_PATH, 'a') as note_file:
                note_file.write(sentence + "\n")

            line_num = len(open(self.NOTES_PATH).readlines())
            files_to_upload.append(self.NOTES_PATH)

            # print('S: '+ sentence)
            entities = self.find_entities(sentence)

            json_string = "{ lineNum : " + str(line_num) + "}"

            #write the metadata into their respective json files
            for entity in entities:
                file_name = self.METADATA_PATH + '/' + entity.replace(' ', '_') + '.json'
                with open(file_name, 'a') as meta_data:
                    num_lines = sum(1 for line in open(file_name))
                    if(num_lines >= 1):
                        meta_data.write(",\n")
                    meta_data.write(json_string)
                files_to_upload.append(file_name)

        # save
        results = [];
        for file in set(files_to_upload):
            results.append(self.add_note_file(file)) #comment this for testing

        return results

    def find_entities(self, text):
        '''
        Find all the entites in a given string
        :param text: the string to find the entities
        :return string array: an array of all the entities as
        '''
        response = self.nlu.analyze(
            text=text,
            features=Features(
                entities=EntitiesOptions(emotion=False, sentiment=False),
                keywords=KeywordsOptions(emotion=False, sentiment=False))).get_result()

        #json_obj = json.loads(response)

        #print(json.dumps(response, indent=2))
        list_of_keywords = [];
        for item in response["keywords"]:
            list_of_keywords.append(item["text"])

        return list_of_keywords

    def add_note_file(self, file_path):
        '''
        Add note to collection from file.

        :param file_path: absolute filepath to document file
        :return boolean: document_id if succeded upload, -1 otherwise
        '''

        source = open(file_path)
        result = self.discovery.add_document(self.enviornment_id, self.collection_id, file=source)

        if result.status_code != 202:
            print(result)
            print("!!! ERROR: Failed to upload document: %s" % file_path)
            return -1

        return result.result['document_id']

    def add_notes_from_dir(self, dir_path):
        '''
        Add all files with '.html', '.pdf', or '.json' as note.
        Only `dir_path` folder's files, will not look into further folders possibly inside `dir_path`.

        :param dir_path: absolute filepath to folder
        :return: list of document_ids if all succeded upload, -1 otherwise

        '''

        dir_files = os.listdir(dir_path)
        dir_files = list(filter(lambda f: re.match('.*\.(html|json|pdf)', f), dir_files))
        dir_files = list(map((lambda f: dir_path + '/' + f), dir_files))

        results = []
        for f in dir_files:
            results.append( self.add_note_file(f) )

        if -1 in results:
            print("!!! ERROR: add_notes_from_dir() failed in %s", dir_path)
            return -1

        return results

    def get_collection_status(self):
        '''
        Return status object of current document collection.
        '''
        return self.discovery.get_collection(self.enviornment_id, self.collection_id).get_result()

    def delete_doc(self, document_id):
        '''
        Delete document from collection
        '''
        return self.discovery.delete_document(self.enviornment_id, self.collection_id, document_id)

if __name__ == "__main__":


    API_KEY= ""
    URL= "https://gateway.watsonplatform.net/discovery/api"
    enviornment_id = ""
    collection_id = ""


    NLU_API_KEY = ""
    NLU_URL = "https://gateway.watsonplatform.net/natural-language-understanding/api"

    ASSISTANT_KEY = ""
    ASSISTANT_URL = ""
    ASSISSTANT_ID =

    bot = Hindsight(API_KEY, URL, enviornment_id, collection_id, NLU_API_KEY, NLU_URL,  ASSISTANT_KEY, ASSISTANT_URL, ASSISSTANT_ID)
    bot.hello()

    bot.chat()
    # print(bot.get_collection_status())

    # bot.add_note("the annual Socialist Scholars Conference in New York. ")
    # bot.add_notes_from_dir("/Users/gpro/gpc/rit/natling/project/data/wiki_data")
    # bot.add_note_file("/Users/gpro/gpc/rit/natling/project/data/small.html")
