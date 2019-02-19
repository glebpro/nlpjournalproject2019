#
#
#   Run evaluation/scoring script against `hindsight` app.
#
#   Usage: scripts/test.py
#   Ouput: stdout, 'results.txt'
#
#   @author Gleb Promokhov gleb.promokhov@gmail.com
#
#

from hindsight import Hindsight

def test_query_response_pairs(query_list, response_list):
    '''
    Tally how many question/pairs answered 'correctly'.
    'Correctness' of response judged by included subfunctions.

    :param query_list: list of strings, queries to feed into system
    :param response_list: list of strings, expected response to `query_list`
    :return: accuracy score
    '''

    def bag_of_words_match(ground_response, test_response):
        '''
        If more than some treshold of words match between responses,
        return true.
        '''
        THRESHOLD = .80
        ground_response = ground_response.split()
        test_response = test_response.split()
        matching_words = set(ground_response + test_response)

        if( (len(matching_words)/len(ground_response)) >= THRESHOLD and \
            (len(matching_words)/len(test_response)) >= THRESHOLD ):
            return True

        return False

    def match_ngrams(ground_response, test_response):
        '''
        If more than some threshold of n-grams match between resonses,
        return true
        '''
        pass

    if len(query_list) != len(response_list):
        print("!!! test.test_query_response_pairs():  len(query_list) != len(response_list)")

    chatbot = Hindsight(API_KEY, URL, enviornment_id, collection_id)
    correct_count = 0

    print('~~~ Testing %s Q/A pairs.' % len(query_list))

    for idx,query in enumerate(query_list):
        response = chatbot.query(query)
        response = response.result['passages'][0]['passage_text']

        # if match_ngrams(response_list[idx], response):
        if bag_of_words_match(response_list[idx], response):
            correct_count+=1

        print('\t~~~ Tested %s' % idx)

    return round(correct_count/len(query_list), 4)


def openQuestionAnswerPairs(question_answer_path):
    qa_pairs = open(question_answer_path).readlines()
    qa_pairs = [q.split(' %%% ') for q in qa_pairs]
    questions = [q[0] for q in qa_pairs]
    answers = [q[1] for q in qa_pairs]
    return questions, answers


q, a = openQuestionAnswerPairs('/Users/gpro/gpc/rit/natling/project/data/question-generation/question_answer_pairs.txt')
result = test_query_response_pairs(q, a)
print('~~~ RESULT: %s%% accuracy.' % result)
