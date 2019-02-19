
#
#   Use `hindsight.` to record your notes through a journalling conversation.
#
#   Run ./step_ibm_enviornment.sh first and add credentials at the bottom.
#
#   Usage: python hindsight.py
#
#   Author: Gleb Promokhov @glebpro
#

import os
import re
import json

from watson_developer_cloud import DiscoveryV1 # https://cloud.ibm.com/apidocs/discovery?language=python

class Hindsight(object):

    def __init__(self, API_KEY, URL, enviornment_id, collection_id):
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

        self.state = self.chat_states['add_mode']
        self.prompt = '>>> '
        self.state_prompt = 'Add a note: '

        self.discovery = DiscoveryV1(
            version = '2018-12-03',
            iam_apikey = API_KEY,
            url = URL
        )

        self.enviornment_id = enviornment_id
        self.collection_id = collection_id


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

        raw_input = str(input(self.prompt + self.state_prompt))

        if raw_input == '/quit':
            return 1

        elif raw_input == '/add':
            self.state = self.chat_states['add_mode']
            self.state_prompt = 'Add a note: '
            self.chat()

        elif raw_input == '/ask':
            self.state = self.chat_states['ask_mode']
            self.state_prompt = 'Ask your notes: '
            self.chat()

        else:
            if self.state == self.chat_states['add_mode']:
                self.add_note(raw_input)

            elif self.state == self.chat_states['ask_mode']:

                print(self.prompt + "Here's what I found: \n")

                results = self.query(raw_input)

                if len(results.result['passages']) == 0:
                    print(self.prompt + "I actually didn't find anything...")

                elif len(results.result['passages']) == 1:
                    print(self.prompt + "I found this one note: ")
                    print(results.result['passages'][0]['passage_text'])

                else:
                    print(self.prompt + "I found these notes: ")
                    for passage in results['result']['passages']:
                        print(passage['passage_text'])

            self.chat()

    def add_note(self, note_text):
        '''
        Add `note_text` to given document by `title`.
        If `title` document not present, create a new one.
        '''

        with open('tmp.html', 'a') as tmp_file:
            tmp_file.write(note_text + "\n")

        # get if titled note in collection already exists
        # if not, create one

        # save
        result = self.add_note_file('tmp.html')
        return result

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

    def query(self, query_text, notes_count=1):
        '''
        Use IBM Discovery 'query' API to access notes.

        :param notes_count: max note count to get
        :param query_text: raw query text
        :return: top relevant notes
        '''

        # can access IBM Collection with query language `query=` or for IBM NLP `natural_language_query=`
        # many parameters in API

        result = self.discovery.query(self.enviornment_id, self.collection_id,
                                        natural_language_query = query_text,
                                        passages_count=notes_count)

        return result

    def query_entity(self, entity, notes_count=5):
        '''
        Use IBM Discovery 'query_entity' API to access notes.

        :param query_text: proper entitiy
        :return: top relevant notes
        '''

        # query specific document by title with raw query text

        pass


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
    URL= ""
    enviornment_id = ""
    collection_id = ""

    bot = Hindsight(API_KEY, URL, enviornment_id, collection_id)
    bot.hello()

    # bot.chat()
    # print(bot.get_collection_status())

    # print( bot.query("When was the Kentucky Derby?") )
    # bot.add_notes_from_dir("/Users/gpro/gpc/rit/natling/project/data/wiki_data")
    # bot.add_note_file("/Users/gpro/gpc/rit/natling/project/scripts/data/wiki_data/1948_Kentucky_Derby.html")
