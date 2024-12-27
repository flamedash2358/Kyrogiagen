import os
from glob import glob
import json
from googletrans import Translator

DEST_LANGUAGE = 'sv'
SRC_LANGUAGE = 'en'

PLACE_HOLDER_START_LETTER = [
    '%',
    '{',
    '[',
]

WORDS_TO_NOT_TRANSLATE = [
    'm_c',
    'r_c',
    'c_n',
    's_c',
    'p_l',
    'o_n_g'
]

KEYS_TO_NOT_TRANSLATE = [
    "comment",
    #resources\lang\sv\events\death
    'event_id',
    'location',
    'season',
    'tags',
    'weight',
    #resources\lang\sv\events\disasters
    'event',
    'camp',
    'season',
    'priority',
    'duration',
    'rarity',
    'disaster',
    'triggers_during',
    'chance',
    #resources\lang\sv\events\injury
    'event_id',
    'location',
    'status',
    'trait',
    'age',
    'Values',
    'amount',
    'mutual',
    #resources\lang\sv\events\leader_den
    'interaction_type',
    'rel_change',
    'player_clan_temper',
    'other_clan_temper',
    'skill',
    'relationships',
    #resources\lang\sv\events\misc
    'sub_type',
    'not_trait',
    'current_rep'
    #resources\lang\sv\events\relationship_events\group_interactions
    "id",
    "cat_amount",
    "intensity",
    "relationship_constraint",
    'specific_reaction',
    'trait_constraint',
    'general_reaction',
    'status_constraint',
    #resources\lang\sv\events\relationship_events\normal_interactions
    'reaction_random_cat',
    'main_status_constraint',
    'random_status_constraint',
    'also_influences',
    'main_trait_constraint',
    'random_trait_constraint',
    #resources\lang\sv\events
    'lead_trait',
    'star_trait',
    'rank',
    #resources\lang\sv\patrols
    'patrol_id',
    'biome',
    'types',
    'patrol_art',
    'min_cats',
    'max_cats',
    'min_max_status',
    'chance_of_success',
    'cats_to',
    'cats_from',
    'stat_trait',
    'dead_cats',
    'stat_skill'



]

translator = Translator()


def get_files_to_translate(base_path:str): 
    '''
    Get all .json-files inside base path recursivly
    '''
    language_file_paths = [
        y 
        for x in os.walk(f"{base_path}\\") 
        for y in glob(os.path.join(x[0], '*.json'))
        if y != 'sv\\config.json'
        and y != '\\sv\\events\\ceremonies\\ceremony-master.json'
    ]
    return language_file_paths

def make_backup_file_name(file_path):
    '''
    Copy a file and add "_original" in file name
    '''
    backup_file_path = file_path
    if f".{DEST_LANGUAGE}.json" in backup_file_path:
        backup_file_path = backup_file_path.replace(
            f".{DEST_LANGUAGE}.json"
            ,f"_original.{DEST_LANGUAGE}.json"
        )
    else:
        backup_file_path = backup_file_path.replace(
            f".json"
            ,f"_original.json"
        )
    return backup_file_path

def save_json(file_path,data):
    # Open and owerwrite the JSON file
    json_data = json.dumps(data, indent=4)
    with open(file_path, "w") as outfile:
        outfile.write(json_data)

def load_json_file(file_path: str):
    # Open and read the JSON file
    with open(file_path, 'r') as file:
        return json.load(file)

def translate(data):
    '''
    Take a sentence, divide into individual word and then translate
    the word as long as it's not a replacement holder, such as 'm_c'
    '''
    if (type(data) is str):
        words = data.split(' ')
        for word_index in range(len(words)):
            if(
                words[word_index] != ''
                and '_' not in words[word_index]
                and words[word_index][0] not in PLACE_HOLDER_START_LETTER
                and words[word_index] not in WORDS_TO_NOT_TRANSLATE
            ):
                words[word_index] = translator.translate(
                    words[word_index]
                    , src=SRC_LANGUAGE,dest=DEST_LANGUAGE
                ).text
        data = ' '.join(words)
        return data
    else:
        return data

# Print the data
def get_translated_list_content(data: list):
    '''
    Recursive search and replace for text to translate
    '''
    for index in range(len(data)):
        if (type(data[index]) is list):
            data[index] = get_translated_list_content(data[index])
        elif (type(data[index]) is dict):
            data[index] = get_translated_dict_content(data[index])
        else:
            #print(data[index])
            data[index] = translate(data[index])
            #print('->',data[index])
    return data

def is_text_tag(key):
    '''
    filter out dictionary keys that should not be translated
    '''
    if ( key in KEYS_TO_NOT_TRANSLATE):
        return False
    return True
    
def get_translated_dict_content(data: dict):
    '''
    Recursive search and replace for text to translate
    '''
    for key, val in data.items():
        if (is_text_tag(key)):
            if (type(val) is list):
                data[key] = get_translated_list_content(val)
            elif (type(val) is dict):
                data[key] = get_translated_dict_content(val)
            else:
                #print(data[key])
                data[key] = translate(val)
                #print('->',data[key])
    return data

def translate_all_files(language_file_paths):
    for language_file_path in language_file_paths:
        '''
        Take a list of json file paths and translate any string type
        that is not specified to not translate.
        '''
        if True:
            if('_original' not in language_file_path):
                print(f"File to translate: {language_file_path}")
                data = load_json_file(language_file_path)
                update_data = False
                if not os.path.isfile(make_backup_file_name(language_file_path)):
                    #save_json(make_backup_file_name(language_file_path), data)
                    #translate file if it has never been transalted before
                    if (type(data) is list and len(data) > 0):
                        if (type(data[0]) is dict) and 'translation_type' in data[0].keys():
                            print("File already transalted, skipping file")
                        else:
                            update_data = True
                            get_translated_list_content(data)
                            data = [{'translation_type': 'Google translate'}] + data
                    else:
                        if 'translation_type' not in data.keys():
                            update_data = True
                            get_translated_dict_content(data)
                            translation_type = {'translation_type': 'Google translate'}
                            translation_type.update(data)
                            data = translation_type
                        else:
                            print("File already transalted, skipping file")
                    if update_data == True:
                        save_json(language_file_path,data)
                else:
                    print("File already transalted, skipping file")

translate_all_files(get_files_to_translate(DEST_LANGUAGE))


