import logging
import os

import sentry_sdk

import common.dialogflow_framework.utils.state as state_utils
from common.gaming import GAMES_WITH_AT_LEAST_1M_COPIES_SOLD_COMPILED_PATTERN
from common.utils import is_yes

import dialogflows.common.intents as common_intents
import dialogflows.common.shared_memory_ops as gaming_memory
from dialogflows.common import game_info


sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))

logger = logging.getLogger(__name__)


def is_game_candidate_minecraft(ngrams, vars):
    candidate_game_id = gaming_memory.get_candidate_game_id(vars)
    assert candidate_game_id is not None and candidate_game_id, \
        gaming_memory.ASSERTION_ERROR_MSG_CANDIDATE_GAME_IS_NOT_SET
    candidate_game_id_str = str(candidate_game_id)
    assert candidate_game_id_str in game_info.games_igdb_ids, f"If igdb game id {candidate_game_id_str} was set "\
        f"as candidate for discussion, the igdb game description should have been put into global variable "\
        f"`games_igdb_ids`"
    candidate_game = game_info.games_igdb_ids[candidate_game_id_str]
    return "minecraft" in candidate_game["name"].lower()


def is_minecraft_mentioned_in_user_uttr(ngrams, vars):
    user_uttr_text = state_utils.get_last_human_utterance(vars)["text"]
    return "minecraft" in user_uttr_text.lower()


def user_wants_to_talk_about_minecraft_request(ngrams, vars):
    logger.info(f"user_wants_to_talk_about_particular_game_request")
    if common_intents.switch_to_particular_game_discussion(vars):
        user_uttr = state_utils.get_last_human_utterance(vars)
        prev_bot_uttr = state_utils.get_last_bot_utterance(vars)
        game_names_from_local_list_of_games = GAMES_WITH_AT_LEAST_1M_COPIES_SOLD_COMPILED_PATTERN.findall(
            user_uttr.get("text", ""))
        if is_yes(user_uttr):
            game_names_from_local_list_of_games += \
                GAMES_WITH_AT_LEAST_1M_COPIES_SOLD_COMPILED_PATTERN.findall(prev_bot_uttr.get("text", ""))
        logger.info(
            f"(user_wants_to_talk_about_minecraft_request)game_names_from_local_list_of_games: "
            f"{game_names_from_local_list_of_games}"
        )
        assert game_names_from_local_list_of_games,\
            "At least one game should have been found in function `switch_to_particular_game_discussion()`"
        flag = any(["minecraft" in gn.lower() for gn in game_names_from_local_list_of_games])
    else:
        flag = False
    logger.info(f"user_wants_to_talk_about_minecraft_request={flag}")
    return flag
