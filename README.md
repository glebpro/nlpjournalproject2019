# Journalling Chatbot
Term project for ENGL 582 _Seminar in Computational Linguistics (Chatbots and Virtual Assistants)_ at RIT, 2019.

[@glebpro](https://github.com/glebpro)

## Abstract:
TBD

## Technicals

###### Setup IBM Watson Discovery Environment
1. Go to [IBM Watons Discovery Page](https://www.ibm.com/watson/services/discovery/) and make a free account, create `hindsight-service`
1. `$ export API_KEY={key}` replace `{key}` with API Key found in IBM Environment Console
2. `$ export URL={url}` replace `{key}` with URL found
3. `$ ./scripts/setup_ibm_enviornment.sh` to setup environment

###### hindsight app

To run the chatbot: `python scripts/hindsight.py`

Run `python data/download_wiki_data.py` to download random wikipedia articles into `/wiki_data` as test notes. Use `hindsight.add_notes_from_dir(path_to_wiki_data)` to add them as notes.

#### Requirements
`pip install --user -r requirements.txt`

#### License
MIT licensed. See the bundled [LICENSE](/LICENSE) file for more details.
