#
#   Conduct some preprocessing on data.
#
#   @author Gleb Promokhov gxp5819@rit.edu
#


import sys
import random
import os


ROOT_PATH = sys.path[0]

def mixDataDirs_intoOneFile(dirs):

    output_file = open(ROOT_PATH+'/flat_entry_data.html', 'w')

    inputs_files = []
    for d in dirs:
        inputs_files.extend(list(map((lambda f: d + '/' + f), os.listdir(d))))

    for input_file in inputs_files:
        input_data = open(input_file).readlines()
        for i in input_data:
            output_file.write(i + '\n')

mixDataDirs_intoOneFile([ROOT_PATH+'/tcse_data', ROOT_PATH+'/wiki_data'])

def assignUtteranceToDocument():
    pass
