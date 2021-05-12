import logging
import random
import os
import re
import sentry_sdk

import common.constants as common_constants
import common.dialogflow_framework.stdm.dialogflow_extention as dialogflow_extention
import common.dialogflow_framework.utils.state as state_utils
from common.utils import is_no, is_yes
from common.animals import MY_CAT, MY_DOG, pet_games, stop_about_animals
import dialogflows.scopes as scopes
from dialogflows.flows.my_pets_states import State as MyPetsState
from dialogflows.flows.animals_states import State as AnimalsState
from dialogflows.flows.animals import make_my_pets_info

sentry_sdk.init(os.getenv('SENTRY_DSN'))
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

questions_pets = ["Would you like to learn more about {}?", "More about {}?", "Do you want to hear more about {}?",
                  "Something else about {}?", "Should I continue?"]
random.shuffle(MY_CAT)
random.shuffle(MY_DOG)

CONF_1 = 1.0
CONF_2 = 0.99
CONF_3 = 0.95


def answer_users_question(vars):
    make_my_pets_info(vars)
    user_uttr = state_utils.get_last_human_utterance(vars)
    user_text = user_uttr["text"]
    shared_memory = state_utils.get_shared_memory(vars)
    my_pet = shared_memory.get("my_pet", "")
    my_pets_info = shared_memory.get("my_pets_info", {})
    my_pet_name = my_pets_info[my_pet]["name"]
    my_pet_breed = my_pets_info[my_pet]["breed"]
    mention_pet = re.findall(r"(cat|dog)", user_text)
    if mention_pet and mention_pet[0] != my_pet:
        my_pet = mention_pet[0]
        my_pet_name = my_pets_info[my_pet]["name"]
        my_pet_breed = my_pets_info[my_pet]["breed"]

    answer = ""
    logger.info(f"answer_users_question {user_text} {my_pet_name}")
    if "?" in user_text and ("your" in user_text or (my_pet_name and my_pet_name in user_text)):
        if "name" in user_text and my_pet and my_pet_name:
            answer = f"My {my_pet}'s name is {my_pet_name}."
        elif "breed" in user_text and my_pet and my_pet_breed:
            answer = f"My {my_pet}'s breed is {my_pet_breed}."
        elif "play" in user_text and my_pet:
            games = " and ".join(pet_games[my_pet])
            answer = f"I like to play with my {my_pet} different games, such as {games}."
        elif "walk" in user_text and my_pet:
            answer = f"I walk with my {my_pet} every morning."
        elif "like" in user_text or "love" in user_text and my_pet:
            answer = f"Yes, I love my {my_pet}."
    return answer, my_pet


def stop_animals_request(ngrams, vars):
    flag = False
    user_uttr = state_utils.get_last_human_utterance(vars)
    shared_memory = state_utils.get_shared_memory(vars)
    stop_about_animals(user_uttr, shared_memory)
    if stop_about_animals(user_uttr, shared_memory):
        flag = True
    logger.info(f"stop_animals_request={flag}")
    return flag


def about_cat_request(ngrams, vars):
    flag = False
    text = state_utils.get_last_human_utterance(vars)["text"]
    isno = is_no(state_utils.get_last_human_utterance(vars))
    shared_memory = state_utils.get_shared_memory(vars)
    told_about_cat = shared_memory.get("told_about_cat", False)
    have_cat = re.findall(r"(do|did) you have (a )?(cat)s?", text)
    ans, pet = answer_users_question(vars)
    if (not isno or have_cat) and not told_about_cat:
        flag = True
    if ans and pet != "cat":
        flag = False
    logger.info(f"about_cat_request={flag}")
    return flag


def about_dog_request(ngrams, vars):
    flag = False
    text = state_utils.get_last_human_utterance(vars)["text"]
    isno = is_no(state_utils.get_last_human_utterance(vars))
    shared_memory = state_utils.get_shared_memory(vars)
    told_about_dog = shared_memory.get("told_about_dog", False)
    have_dog = re.findall(r"(do|did) you have (a )?(dog)s?", text)
    ans, pet = answer_users_question(vars)
    if (not isno or have_dog) and not told_about_dog:
        flag = True
    if ans and pet != "dog":
        flag = False
    logger.info(f"about_dog_request={flag}")
    return flag


def my_cat_1_request(ngrams, vars):
    flag = False
    text = state_utils.get_last_human_utterance(vars)["text"]
    isno = is_no(state_utils.get_last_human_utterance(vars))
    shared_memory = state_utils.get_shared_memory(vars)
    my_pet = shared_memory.get("my_pet", "")
    told_about_cat = shared_memory.get("told_about_cat", False)
    start_about_cat = shared_memory.get("start_about_cat", False)
    have_cat = re.findall(r"(do|did) you have (a )?(cat)s?", text)
    if (not isno or have_cat) and (not told_about_cat or start_about_cat) and my_pet != "dog":
        flag = True
    logger.info(f"my_cat_1_request={flag}")
    return flag


def my_dog_1_request(ngrams, vars):
    flag = False
    text = state_utils.get_last_human_utterance(vars)["text"]
    isno = is_no(state_utils.get_last_human_utterance(vars))
    shared_memory = state_utils.get_shared_memory(vars)
    my_pet = shared_memory.get("my_pet", "")
    told_about_dog = shared_memory.get("told_about_dog", False)
    start_about_dog = shared_memory.get("start_about_dog", False)
    have_dog = re.findall(r"(do|did) you have (a )?(dog)s?", text)
    if (not isno or have_dog) and (not told_about_dog or start_about_dog) and my_pet != "cat":
        flag = True
    logger.info(f"my_dog_1_request={flag}")
    return flag


def my_cat_2_request(ngrams, vars):
    flag = False
    isyes = is_yes(state_utils.get_last_human_utterance(vars))
    ans, _ = answer_users_question(vars)
    if isyes or ans:
        flag = True
    logger.info(f"my_cat_2_request={flag}")
    return flag


def my_dog_2_request(ngrams, vars):
    flag = False
    isyes = is_yes(state_utils.get_last_human_utterance(vars))
    ans, _ = answer_users_question(vars)
    if isyes or ans:
        flag = True
    logger.info(f"my_dog_2_request={flag}")
    return flag


def my_cat_3_request(ngrams, vars):
    flag = False
    isyes = is_yes(state_utils.get_last_human_utterance(vars))
    ans, _ = answer_users_question(vars)
    if isyes or ans:
        flag = True
    logger.info(f"my_cat_3_request={flag}")
    return flag


def my_dog_3_request(ngrams, vars):
    flag = False
    isyes = is_yes(state_utils.get_last_human_utterance(vars))
    ans, _ = answer_users_question(vars)
    if isyes or ans:
        flag = True
    logger.info(f"my_dog_3_request={flag}")
    return flag


def tell_about_cat_response(vars):
    shared_memory = state_utils.get_shared_memory(vars)
    my_pets_info = shared_memory["my_pets_info"]
    sentence = my_pets_info["cat"]["sentence"]
    state_utils.save_to_shared_memory(vars, start_about_cat=True)
    state_utils.save_to_shared_memory(vars, my_pet="cat")
    answer, _ = answer_users_question(vars)
    response = f"{answer} {sentence} Would you like to learn more about my cat?".strip()
    state_utils.set_confidence(vars, confidence=CONF_1)
    state_utils.set_can_continue(vars, continue_flag=common_constants.MUST_CONTINUE)
    return response


def tell_about_dog_response(vars):
    shared_memory = state_utils.get_shared_memory(vars)
    my_pets_info = shared_memory["my_pets_info"]
    sentence = my_pets_info["dog"]["sentence"]
    state_utils.save_to_shared_memory(vars, start_about_dog=True)
    state_utils.save_to_shared_memory(vars, my_pet="dog")
    answer, _ = answer_users_question(vars)
    response = f"{answer} {sentence} Would you like to learn more about my dog?".strip()
    state_utils.set_confidence(vars, confidence=CONF_1)
    state_utils.set_can_continue(vars, continue_flag=common_constants.MUST_CONTINUE)
    return response


def my_cat_1_response(vars):
    fact = MY_CAT[0]
    shared_memory = state_utils.get_shared_memory(vars)
    my_pets_info = shared_memory["my_pets_info"]
    my_pet_name = my_pets_info["cat"]["name"]
    question_cat = random.choice(questions_pets)
    question_cat = question_cat.format(random.choice(["my cat", my_pet_name]))
    answer, _ = answer_users_question(vars)
    response = f"{answer} {fact} {question_cat}".strip()
    state_utils.save_to_shared_memory(vars, told_about_cat=True)
    state_utils.save_to_shared_memory(vars, start_about_cat=False)
    state_utils.save_to_shared_memory(vars, cat=True)
    state_utils.set_confidence(vars, confidence=CONF_2)
    state_utils.set_can_continue(vars, continue_flag=common_constants.CAN_CONTINUE_SCENARIO)
    logger.info(f"my_cat_1_response: {response}")
    return response


def my_cat_2_response(vars):
    fact = MY_CAT[1]
    shared_memory = state_utils.get_shared_memory(vars)
    my_pets_info = shared_memory["my_pets_info"]
    my_pet_name = my_pets_info["cat"]["name"]
    question_cat = random.choice(questions_pets)
    question_cat = question_cat.format(random.choice(["my cat", my_pet_name]))
    answer, _ = answer_users_question(vars)
    response = f"{answer} {fact} {question_cat}".strip()
    state_utils.save_to_shared_memory(vars, cat=True)
    state_utils.save_to_shared_memory(vars, start_about_cat=False)
    state_utils.set_confidence(vars, confidence=CONF_2)
    state_utils.set_can_continue(vars, continue_flag=common_constants.CAN_CONTINUE_SCENARIO)
    logger.info(f"my_cat_2_response: {response}")
    return response


def my_cat_3_response(vars):
    fact = MY_CAT[2]
    about_dog = "I also have a dog."
    shared_memory = state_utils.get_shared_memory(vars)
    told_about_dog = shared_memory.get("told_about_dog", False)
    answer, _ = answer_users_question(vars)
    if told_about_dog:
        response = f"{answer} {fact}".strip()
    else:
        response = f"{answer} {fact} {about_dog}".strip()
    state_utils.save_to_shared_memory(vars, cat=True)
    state_utils.save_to_shared_memory(vars, start_about_cat=False)
    state_utils.set_confidence(vars, confidence=CONF_3)
    state_utils.set_can_continue(vars, continue_flag=common_constants.CAN_CONTINUE_SCENARIO)
    logger.info(f"my_cat_3_response: {response}")
    return response


def my_dog_1_response(vars):
    fact = MY_DOG[0]
    shared_memory = state_utils.get_shared_memory(vars)
    my_pets_info = shared_memory["my_pets_info"]
    my_pet_name = my_pets_info["dog"]["name"]
    question_dog = random.choice(questions_pets)
    question_dog = question_dog.format(random.choice(["my dog", my_pet_name]))
    answer, _ = answer_users_question(vars)
    response = f"{answer} {fact} {question_dog}".strip()
    state_utils.save_to_shared_memory(vars, told_about_dog=True)
    state_utils.save_to_shared_memory(vars, dog=True)
    state_utils.save_to_shared_memory(vars, start_about_dog=False)
    state_utils.set_confidence(vars, confidence=CONF_2)
    state_utils.set_can_continue(vars, continue_flag=common_constants.CAN_CONTINUE_SCENARIO)
    logger.info(f"my_dog_1_response: {response}")
    return response


def my_dog_2_response(vars):
    fact = MY_DOG[1]
    shared_memory = state_utils.get_shared_memory(vars)
    my_pets_info = shared_memory["my_pets_info"]
    my_pet_name = my_pets_info["dog"]["name"]
    question_dog = random.choice(questions_pets)
    question_dog = question_dog.format(random.choice(["my dog", my_pet_name]))
    answer, _ = answer_users_question(vars)
    response = f"{answer} {fact} {question_dog}".strip()
    state_utils.save_to_shared_memory(vars, dog=True)
    state_utils.save_to_shared_memory(vars, start_about_dog=False)
    state_utils.set_confidence(vars, confidence=CONF_2)
    state_utils.set_can_continue(vars, continue_flag=common_constants.CAN_CONTINUE_SCENARIO)
    logger.info(f"my_dog_2_response: {response}")
    return response


def my_dog_3_response(vars):
    fact = MY_DOG[2]
    about_cat = "I also have a cat."
    shared_memory = state_utils.get_shared_memory(vars)
    told_about_cat = shared_memory.get("told_about_cat", False)
    answer, _ = answer_users_question(vars)
    if told_about_cat:
        response = f"{answer} {fact}".strip()
    else:
        response = f"{answer} {fact} {about_cat}".strip()
    state_utils.save_to_shared_memory(vars, dog=True)
    state_utils.save_to_shared_memory(vars, start_about_dog=False)
    state_utils.set_confidence(vars, confidence=CONF_3)
    state_utils.set_can_continue(vars, continue_flag=common_constants.CAN_CONTINUE_SCENARIO)
    logger.info(f"my_dog_3_response: {response}")
    return response


def to_animals_flow_request(ngrams, vars):
    flag = True
    logger.info(f"to_animals_flow_request={flag}")
    return flag


def error_response(vars):
    state_utils.set_confidence(vars, 0)
    return ""


simplified_dialog_flow = dialogflow_extention.DFEasyFilling(MyPetsState.USR_START)

simplified_dialog_flow.add_user_serial_transitions(
    MyPetsState.USR_START,
    {
        MyPetsState.SYS_ERR: stop_animals_request,
        MyPetsState.SYS_MY_CAT_1: my_cat_1_request,
        MyPetsState.SYS_MY_DOG_1: my_dog_1_request,
        (scopes.ANIMALS, AnimalsState.USR_START): to_animals_flow_request,
    },
)

simplified_dialog_flow.add_user_serial_transitions(
    MyPetsState.USR_ABOUT_CAT,
    {
        MyPetsState.SYS_ERR: stop_animals_request,
        MyPetsState.SYS_MY_CAT_1: my_cat_1_request,
        (scopes.ANIMALS, AnimalsState.USR_START): to_animals_flow_request,
    },
)

simplified_dialog_flow.add_user_serial_transitions(
    MyPetsState.USR_ABOUT_DOG,
    {
        MyPetsState.SYS_ERR: stop_animals_request,
        MyPetsState.SYS_MY_DOG_1: my_dog_1_request,
        (scopes.ANIMALS, AnimalsState.USR_START): to_animals_flow_request,
    },
)

simplified_dialog_flow.add_user_serial_transitions(
    MyPetsState.USR_MY_CAT_1,
    {
        MyPetsState.SYS_ERR: stop_animals_request,
        MyPetsState.SYS_MY_CAT_2: my_cat_2_request,
        MyPetsState.SYS_ABOUT_DOG: about_dog_request,
        (scopes.ANIMALS, AnimalsState.USR_START): to_animals_flow_request,
    },
)

simplified_dialog_flow.add_user_serial_transitions(
    MyPetsState.USR_MY_DOG_1,
    {
        MyPetsState.SYS_ERR: stop_animals_request,
        MyPetsState.SYS_MY_DOG_2: my_dog_2_request,
        MyPetsState.SYS_ABOUT_CAT: about_cat_request,
        (scopes.ANIMALS, AnimalsState.USR_START): to_animals_flow_request,
    },
)

simplified_dialog_flow.add_user_serial_transitions(
    MyPetsState.USR_MY_CAT_2,
    {
        MyPetsState.SYS_ERR: stop_animals_request,
        MyPetsState.SYS_MY_CAT_3: my_cat_3_request,
        MyPetsState.SYS_ABOUT_DOG: about_dog_request,
        (scopes.ANIMALS, AnimalsState.USR_START): to_animals_flow_request,
    },
)

simplified_dialog_flow.add_user_serial_transitions(
    MyPetsState.USR_MY_DOG_2,
    {
        MyPetsState.SYS_ERR: stop_animals_request,
        MyPetsState.SYS_MY_DOG_3: my_dog_3_request,
        MyPetsState.SYS_ABOUT_CAT: about_cat_request,
        (scopes.ANIMALS, AnimalsState.USR_START): to_animals_flow_request,
    },
)

simplified_dialog_flow.add_user_serial_transitions(
    MyPetsState.USR_MY_CAT_3,
    {
        MyPetsState.SYS_ERR: stop_animals_request,
        MyPetsState.SYS_ABOUT_DOG: about_dog_request,
        (scopes.ANIMALS, AnimalsState.USR_START): to_animals_flow_request,
    },
)

simplified_dialog_flow.add_user_serial_transitions(
    MyPetsState.USR_MY_DOG_3,
    {
        MyPetsState.SYS_ERR: stop_animals_request,
        MyPetsState.SYS_ABOUT_CAT: about_cat_request,
        (scopes.ANIMALS, AnimalsState.USR_START): to_animals_flow_request,
    },
)

simplified_dialog_flow.add_system_transition(MyPetsState.SYS_ABOUT_CAT, MyPetsState.USR_ABOUT_CAT,
                                             tell_about_cat_response, )
simplified_dialog_flow.add_system_transition(MyPetsState.SYS_ABOUT_DOG, MyPetsState.USR_ABOUT_DOG,
                                             tell_about_dog_response, )
simplified_dialog_flow.add_system_transition(MyPetsState.SYS_MY_CAT_1, MyPetsState.USR_MY_CAT_1, my_cat_1_response, )
simplified_dialog_flow.add_system_transition(MyPetsState.SYS_MY_DOG_1, MyPetsState.USR_MY_DOG_1, my_dog_1_response, )
simplified_dialog_flow.add_system_transition(MyPetsState.SYS_MY_CAT_2, MyPetsState.USR_MY_CAT_2, my_cat_2_response, )
simplified_dialog_flow.add_system_transition(MyPetsState.SYS_MY_DOG_2, MyPetsState.USR_MY_DOG_2, my_dog_2_response, )
simplified_dialog_flow.add_system_transition(MyPetsState.SYS_MY_CAT_3, MyPetsState.USR_MY_CAT_3, my_cat_3_response, )
simplified_dialog_flow.add_system_transition(MyPetsState.SYS_MY_DOG_3, MyPetsState.USR_MY_DOG_3, my_dog_3_response, )
simplified_dialog_flow.add_system_transition(MyPetsState.SYS_ERR, (scopes.MAIN, scopes.State.USR_ROOT),
                                             error_response, )

simplified_dialog_flow.set_error_successor(MyPetsState.USR_START, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.SYS_ABOUT_CAT, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.SYS_ABOUT_DOG, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.USR_ABOUT_CAT, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.USR_ABOUT_DOG, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.SYS_MY_CAT_1, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.SYS_MY_DOG_1, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.USR_MY_CAT_1, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.USR_MY_DOG_1, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.USR_MY_CAT_2, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.USR_MY_DOG_2, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.SYS_MY_CAT_2, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.SYS_MY_DOG_2, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.SYS_MY_CAT_3, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.SYS_MY_DOG_3, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.USR_MY_CAT_3, MyPetsState.SYS_ERR)
simplified_dialog_flow.set_error_successor(MyPetsState.USR_MY_DOG_3, MyPetsState.SYS_ERR)

dialogflow = simplified_dialog_flow.get_dialogflow()
