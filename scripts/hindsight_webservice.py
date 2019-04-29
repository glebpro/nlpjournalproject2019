
from hindsight import Hindsight
from flask import Flask
from flask import request
from flask import jsonify
app = Flask(__name__)

API_KEY= ""
URL= "https://gateway.watsonplatform.net/discovery/api"
enviornment_id = ""
collection_id = ""

NLU_API_KEY = ""
NLU_URL = "https://gateway.watsonplatform.net/natural-language-understanding/api"

ASSISTANT_KEY = ""
ASSISTANT_URL = ""
ASSISSTANT_ID = ""

S2T_KEY = ""
S2T_URL = ""

SMMRY_API_KEY = ""

bot = Hindsight(API_KEY, URL, enviornment_id, collection_id, NLU_API_KEY, NLU_URL, ASSISTANT_KEY, ASSISTANT_URL, ASSISSTANT_ID, S2T_KEY, S2T_URL, SMMRY_API_KEY)

@app.route("/get_state", methods=['GET'])
def get_state():
    return jsonify({'state': bot.state})

@app.route("/web_chat", methods=['POST'])
def web_chat_runner():

    # assert request input
    if request.method != 'POST':
        return "Only POST to this endpoint"

    data = request.get_json()

    if list(data.keys()) != ['input_text', 'key']:
        return "Bad input format"

    if data['key'] != SMMRY_API_KEY:
        return "Invalid use key"

    return jsonify(bot.web_chat(data['input_text']))
