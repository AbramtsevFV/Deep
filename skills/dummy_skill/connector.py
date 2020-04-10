#!/usr/bin/env python

import asyncio
import csv
import json
import logging
import re
import time
from collections import defaultdict
import random
from random import choice
from typing import Callable, Dict
from copy import copy

from common.universal_templates import opinion_request_question
from common.link import link_to, skills_phrases_map
import sentry_sdk
from os import getenv


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

sentry_sdk.init(getenv('SENTRY_DSN'))

ASK_QUESTION_PROB = 0.7
ASK_NORMAL_QUESTION_PROB = 0.5
LINK_TO_PROB = 0.5

np_ignore_list = ["'s", 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
                  "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
                  'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their',
                  'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
                  'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                  'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
                  'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before',
                  'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
                  'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
                  'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
                  'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
                  "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn',
                  "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven',
                  "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't",
                  'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't",
                  'wouldn', "wouldn't", "my name", "your name", "wow", "yeah", "yes", "ya", "cool", "okay", "more",
                  "some more", " a lot", "a bit", "another one", "something else", "something", "anything",
                  "someone", "anyone", "play", "mean", "a lot", "a little", "a little bit",
                  "boring", "radio", "type", "call", "fun", "fall", "name", "names", "lgbtq families", "day", "murder",
                  "amazon", "take", "interest", "days", "year", "years", "sort", "fan", "going", "death", "part", "end",
                  "watching", "thought", "thoughts", "man", "men", "listening", "big fan", "fans", "rapping", "reading",
                  "going", "thing", "hanging", "best thing", "wife", "things"]

np_ignore_expr = re.compile("(" + "|".join([r'\b%s\b' % word for word in np_ignore_list]) + ")")
rm_spaces_expr = re.compile(r'\s\s+')

donotknow_answers = [
    "What do you want to talk about?",
    "I am a bit confused. What would you like to chat about?",
    "Sorry, probably, I didn't get what you meant. What do you want to talk about?",
    "Sorry, I didn't catch that. What would you like to chat about?"
]

with open("skills/dummy_skill/questions_map.json", "r") as f:
    QUESTIONS_MAP = json.load(f)

with open("skills/dummy_skill/nounphrases_questions_map.json", "r") as f:
    NP_QUESTIONS = json.load(f)

with open("skills/dummy_skill/facts_map.json", "r") as f:
    FACTS_MAP = json.load(f)

with open("skills/dummy_skill/nounphrases_facts_map.json", "r") as f:
    NP_FACTS = json.load(f)

with open("skills/dummy_skill/normal_questions.json", "r") as f:
    NORMAL_QUESTIONS = json.load(f)


class RandomTopicResponder:
    def __init__(self, filename, topic, text):
        self.topic_phrases = defaultdict(list)
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.topic_phrases[row[topic]].append(row[text])
        self.current_index = {k: 0 for k in self.topic_phrases.keys()}
        self.topics = set(self.topic_phrases.keys())

    def get_random_text(self, topics):
        available_topics = self.topics.intersection(set(topics))
        if not available_topics:
            return ''

        selected_topic = choice(list(available_topics))
        result = self.topic_phrases[selected_topic][self.current_index[selected_topic]]

        self.current_index[selected_topic] += 1
        if self.current_index[selected_topic] >= len(self.topic_phrases[selected_topic]):
            self.current_index[selected_topic] = 0
        return result


questions_generator = RandomTopicResponder("skills/dummy_skill/questions_with_topics.csv", 'topic', 'question')
facts_generator = RandomTopicResponder("skills/dummy_skill/facts_with_topics.csv", 'topic', 'fact')


def generate_question_not_from_last_responses(dialog):
    # get previous active skills
    prev_active_skills = [uttr.get("active_skill", "") for uttr in dialog["bot_utterances"]
                          if uttr.get("active_skill", "") != ""]
    # remove prev active skills from those we can link to
    available_links = set(skills_phrases_map.keys()).difference(set(prev_active_skills))
    if len(available_links) > 0:
        # if we still have skill to link to, try to generate linking question
        linked_question = link_to(list(available_links)).get("phrase", "")
    else:
        linked_question = ""

    to_choose = copy(NORMAL_QUESTIONS)
    to_remove = []
    for prev_bot_uttr in dialog["bot_utterances"]:
        for i, quest in enumerate(to_choose):
            if quest.lower() in prev_bot_uttr["text"].lower():
                to_remove += [quest]
            if len(linked_question) != 0 and linked_question in prev_bot_uttr["text"].lower():
                linked_question = ""
    for quest in set(to_remove):
        to_choose.remove(quest)

    if len(linked_question) > 0 and random.random() < LINK_TO_PROB:
        result = linked_question
    else:
        if len(to_choose) > 0:
            result = choice(to_choose)
        else:
            result = choice(NORMAL_QUESTIONS)
    return result


class DummySkillConnector:
    async def send(self, payload: Dict, callback: Callable):
        try:
            st_time = time.time()
            dialog = payload['payload']["dialogs"][0]

            curr_topics = dialog["utterances"][-1]["annotations"]["cobot_topics"].get("text", [])
            curr_nounphrases = dialog["utterances"][-1]["annotations"]["cobot_nounphrases"]

            if len(curr_topics) == 0:
                curr_topics = ["Phatic"]
            logger.info(f"Found topics: {curr_topics}")
            for i in range(len(curr_nounphrases)):
                curr_nounphrases[i] = re.sub(rm_spaces_expr, ' ',
                                             re.sub(np_ignore_expr, ' ', curr_nounphrases[i])).strip()

            logger.info(f"Found nounphrases: {curr_nounphrases}")

            cands = []
            confs = []
            attrs = []

            cands += [choice(donotknow_answers)]
            confs += [0.5]
            attrs += [{"type": "dummy"}]

            if len(dialog["utterances"]) > 14:
                questions_same_nps = []
                for i, nphrase in enumerate(curr_nounphrases):
                    for q_id in NP_QUESTIONS.get(nphrase, []):
                        questions_same_nps += [QUESTIONS_MAP[str(q_id)]]

                if len(questions_same_nps) > 0:
                    logger.info("Found special nounphrases for questions. Return question with the same nounphrase.")
                    cands += [choice(questions_same_nps)]
                    confs += [0.6]
                    attrs += [{"type": "nounphrase_question"}]
                else:
                    if random.random() < ASK_NORMAL_QUESTION_PROB:
                        logger.info("No special nounphrases for questions. Return question of the same topic.")
                        cands += [questions_generator.get_random_text(curr_topics)]
                        confs += [0.55]
                        attrs += [{"type": "topic_question"}]
                    else:
                        logger.info("No special nounphrases for questions. Return normal question.")
                        cands += [generate_question_not_from_last_responses(dialog)]
                        confs += [0.7]
                        attrs += [{"type": "normal_question"}]
            else:
                logger.info("Dialog begins. No special nounphrases for questions. Return normal question.")
                cands += [generate_question_not_from_last_responses(dialog)]
                confs += [0.7]
                attrs += [{"type": "normal_question"}]

            facts_same_nps = []
            for i, nphrase in enumerate(curr_nounphrases):
                for fact_id in NP_FACTS.get(nphrase, []):
                    facts_same_nps += [FACTS_MAP[str(fact_id)] + ". " + (opinion_request_question()
                                       if random.random() < ASK_QUESTION_PROB else "")]

            if len(facts_same_nps) > 0:
                logger.info("Found special nounphrases for facts. Return fact with the same nounphrase.")
                cands += [choice(facts_same_nps)]
                confs += [0.6]
                attrs += [{"type": "nounphrase_fact"}]
            '''
            else:
                logger.info("No special nounphrases for facts. Return fact of the same topic.")
                cands += [f"Listen what I found on Reddit: {facts_generator.get_random_text(curr_topics)}"
                          f". What do you think about it?"]
                confs += [0.6]
                attrs += [{"type": "topic_fact"}]
            '''

            total_time = time.time() - st_time
            logger.info(f'dummy_skill exec time: {total_time:.3f}s')
            asyncio.create_task(callback(
                task_id=payload['task_id'],
                response=[cands, confs, attrs]
            ))
        except Exception as e:
            logger.exception(e)
            sentry_sdk.capture_exception(e)
            asyncio.create_task(callback(
                task_id=payload['task_id'],
                response=e
            ))
