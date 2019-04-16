# "hindsight." - Journalling Chatbot
Term project for ENGL 582 _Seminar in Computational Linguistics (Chatbots and Virtual Assistants)_ at RIT, 2019.

[@glebpro](https://github.com/glebpro)

## Abstract:
TBD

## Technicals

###### Setup IBM Watson Discovery Environment
1. Go to [IBM Waton's Discovery Service](https://www.ibm.com/watson/services/discovery/), make a free account and create a Discovery resource
2. `$ export API_KEY={key}` replace `{key}` with API Key found in IBM Environment Console
3. `$ export URL={url}` replace `{key}` with URL found
4. `$ ./scripts/setup_ibm_enviornment.sh` to setup environment
5. Several more IBM services are needed to run hindsight. Populate the variables in `scripts/hindsight.py -> main()` with:
[IBM NLU Service](https://www.ibm.com/watson/services/natural-language-understanding/),
[IBM Assistant Service](https://www.ibm.com/cloud/watson-assistant/),
[IBM Speech2Text Service](https://www.ibm.com/watson/services/speech-to-text/)

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
  ```

###### hindsight app

To run the chatbot: `python scripts/hindsight.py`

Run `python data/download_tcse_data.py` to download TED transcription utterances about the terms listed in `data/tcse_terms.txt` into `data/tcse_data`.

#### Requirements
`pip install --user -r requirements.txt`

#### License
MIT licensed. See the bundled [LICENSE](/LICENSE) file for more details.

#### Works cited

`https://yohasebe.com/tcse/` Hasebe, Yoichiro. (2015) Design and Implementation of an Online Corpus of Presentation Transcripts of TED Talks. Procedia: Social and Behavioral Sciences 198(24), 174–182.

`http://www.cs.cmu.edu/~ark/mheilman/questions/papers/heilman-question-generation-dissertation.pdf`
