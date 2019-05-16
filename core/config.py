import sys
from copy import deepcopy
from pathlib import Path

import yaml

# from deeppavlov import configs

MAX_WORKERS = 4
root = Path(__file__).parent.parent

SKILLS = [
    # {
    #     "name": "odqa",
    #     "url": "http://0.0.0.0:2080/odqa",
    #     "path": configs.dp_assistant.agent_ru_odqa_retr_noans_rubert_infer
    # },
    {
        "name": "chitchat",
        "url": "http://0.0.0.0:2081/chitchat",
        "path": root / "skills/ranking_chitchat/agent_ranking_chitchat_2staged_tfidf_smn_v4_prep.json",
        "env": {
            "CUDA_VISIBLE_DEVICES": ""
        },
        "profile_handler": True
    },
    # {
    #     "name": "hellobot",
    #     "url": "http://127.0.0.1:2085/ruler_call/",
    #     "path": None,
    #     "profile_handler": True
    # },
    # {
    #     "name": "sberchat",
    #     "url": "http://23.102.48.212:8443/api/",
    #     "path": None
    # },
    # {
    #     "name": "gen_chitchat",
    #     "url": "http://0.0.0.0:2086/gen_chitchat",
    #     "path": configs.dp_assistant.agent_transformer_chit_chat_40k_v01_1_20
    # },
    # {
    #     "name": "kbqa",
    #     "url": "http://0.0.0.0:2087/kbqa",
    #     "path": configs.dp_assistant.agent_kbqa_rus
    # },
    {
        "name": "mailruqa",
        "url": "http://0.0.0.0:2089/mailruqa",
        "path": root / "skills/text_qa/agent_ranking_mailru_bert_3.json"
    }
    # {
    #     "name": "generalqa",
    #     "url": "http://0.0.0.0:2090/generalqa",
    #     "path": configs.dp_assistant.agent_general_qa
    #
    # }
]

ANNOTATORS = [
    {
        "name": "ner",
        "url": "http://0.0.0.0:2083/ner_rus",
        "path": root / "annotators/ner/preproc_ner_rus_vpc.json",
        "env": {
            "CUDA_VISIBLE_DEVICES": ""
        }
    },
    {
        "name": "sentiment",
        "url": "http://0.0.0.0:2084/rusentiment",
        "path": root / "annotators/sentiment/preproc_rusentiment.json",
        "env": {
            "CUDA_VISIBLE_DEVICES": ""
        }
    },
    {
        "name": "obscenity",
        "url": "http://0.0.0.0:2088/obscenity",
        "path": root / "annotators/obscenity/obscenity_classifier.json",
        "env": {
            "CUDA_VISIBLE_DEVICES": ""
        }
    }
]

SKILL_SELECTORS = [
    {
        "name": "chitchat_odqa",
        "url": "http://0.0.0.0:2082/chitchat_odqa_selector",
        "path": root / "skill_selectors/chitchat_odqa_selector/sselector_chitchat_odqa.json",
        "env": {
            "CUDA_VISIBLE_DEVICES": ""
        }
    }
]

RESPONSE_SELECTORS = [

]

POSTPROCESSORS = [

]

# TODO include Bot?


def _get_config_path(component_config: dict) -> dict:
    component_config = deepcopy(component_config)
    raw_path = component_config.get('path', None)

    if not raw_path:
        return component_config

    config_path = Path(raw_path)
    if not config_path.is_absolute():
        config_path = Path(__file__).resolve().parents[2] / config_path

    if isinstance(config_path, Path) and config_path.is_file():
        component_config['path'] = config_path
    else:
        raise FileNotFoundError(f'config {raw_path} does not exists')

    return component_config


_run_config_path: Path = Path(__file__).resolve().parent / 'config.yaml'
_component_groups = ['SKILLS', 'ANNOTATORS', 'SKILL_SELECTORS', 'RESPONSE_SELECTORS', 'POSTPROCESSORS']
_module = sys.modules[__name__]

if _run_config_path.is_file():
    with _run_config_path.open('r', encoding='utf-8') as f:
        config: dict = yaml.safe_load(f)

    if config.get('use_config', False) is True:
        config = config.get('agent_config', {})

        MAX_WORKERS = config.get('MAX_WORKERS', MAX_WORKERS)

        for group in _component_groups:
            setattr(_module, group, list(map(_get_config_path, config.get(group, []))))
