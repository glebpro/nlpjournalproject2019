# "hindsight." - Journalling Chatbot
Term project for ENGL 582 _Seminar in Computational Linguistics (Chatbots and Virtual Assistants)_ at RIT, 2019.

[@glebpro](https://github.com/glebpro) Gleb Promokhov
[@LambStack](https://github.com/LambStack) Joseph Agnelli


## Abstract:
Hindsight combines the latest advancements in computational linguistics and artificial intelligence with a series of cloud-based API calls to streamline the collection, summarization, and analyzation of consumer-driven data. All this to say, Hindsight is a command line interface that allows users to store and retrieve notes in a intuitive way using their natural language. After loading your notes into Hindsight you can ask it "What did I say about dogs?", or "What is the most important thing I said about dogs?" or even, "How do I feel about dogs?" and hindsight will provide you with a meaningful response which is based directly off the notes you've taken.

## Technicals

##### Setup API Enviornment
1. Go to [IBM Waton's Discovery Service](https://www.ibm.com/watson/services/discovery/), make a free account and create a Discovery resource
2. `$ export API_KEY={key}` replace `{key}` with API Key found in IBM Environment Console
3. `$ export URL={url}` replace `{key}` with URL found
4. `$ ./scripts/setup_ibm_enviornment.sh` to setup environment
5. Several more IBM services are needed to run hindsight. Populate the variables in `scripts/hindsight.py -> main()` with:
[IBM NLU Service](https://www.ibm.com/watson/services/natural-language-understanding/),
[IBM Assistant Service](https://www.ibm.com/cloud/watson-assistant/),
[IBM Speech2Text Service](https://www.ibm.com/watson/services/speech-to-text/)
[SMMRY Text Summarization Service](https://smmry.com/)

```
    API_KEY= "{API_KEY_of_Discovery_Serivce}"
    URL= "{URL_of_Discovery_Serivce}"
    enviornment_id = "{ID_of_Enviornment_of_Discovery_Serivce}"
    collection_id = "{ID_of_Collection_of_Discovery_Serivce}"
    NLU_API_KEY = "{API_KEY_of_NLU_Service}"
    NLU_URL = "{URL_of_NLU_Service}"
    ASSISTANT_KEY = "{API_Key_of_Assistant_Service}"
    ASSISTANT_URL = "{URL_of_Assistant_Service}"
    ASSISSTANT_ID = "{ID_of_Assistant_Service}"
    S2T_KEY = "{API_Key_of_Speech2Text_Service}"
    S2T_URL = "{URL_of_Speech2Text_Service}"
    SMMRY_API_KEY = "{API_KEY_of_SMMY_Service}"
  ```

##### hindsight app

To run the chatbot as a command line app: `$ python scripts/hindsight.py`

To run the chatbot as a web service, populate `scripts/hindsight_webservice.py` with the needed keys and run : `$ export FLASK_APP=scripts/hindsight_webservice.py` then `$ python -m flask run`

The following `curl` command retrieves the current chatbot ask/add state:
`curl -X GET http://127.0.0.1:5000/get_state`

To issue command to hindsight:
`curl -d '{"input_text":"/ask", "key":"<SMMRY_API_KEY>"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/web_chat`

##### Sample Data

Run `python data/download_tcse_data.py` to download TED transcription utterances about the terms listed in `data/tcse_terms.txt` into `data/tcse_data`. These closely resemble the spoken utterances we expect users of hindsight to say. Uncomment the `bot.add_mode_file_input()` in `hindsight.py -> main()` to add all those notes.

#### Requirements
`pip install --user -r requirements.txt`

#### License
MIT licensed. See the bundled [LICENSE](/LICENSE) file for more details.

#### Works cited

`https://yohasebe.com/tcse/` Hasebe, Yoichiro. (2015) Design and Implementation of an Online Corpus of Presentation Transcripts of TED Talks. Procedia: Social and Behavioral Sciences 198(24), 174–182.
