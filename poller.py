import argparse
import json
import logging
import sys
from typing import Optional
from pathlib import Path
from collections import defaultdict
from multiprocessing import Process, Queue
from itertools import zip_longest

import requests
import polling

from deeppavlov.core.agent.agent import Agent
from deeppavlov.agents.default_agent.default_agent import DefaultAgent
from deeppavlov.skills.default_skill.default_skill import DefaultStatelessSkill
from deeppavlov.core.commands.infer import build_model
from deeppavlov.core.common.file import read_json
from deeppavlov.deep import find_config
from deeppavlov.download import deep_download


logging.disable(logging.DEBUG)
log = logging.getLogger('convai_router_bot_poller')
log.propagate = False
log.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler(sys.stderr)
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log_handler.setFormatter(log_formatter)
log.addHandler(log_handler)


parser = argparse.ArgumentParser()
parser.add_argument('config_path', help='path to a pipeline json config', type=str)
parser.add_argument('--host', default=None, help='router bot host', type=str)
parser.add_argument('--port', default=None, help='router bot port', type=str)
parser.add_argument('--token', default=None, help='bot token', type=str)
parser.add_argument('--no-default-skill', action='store_true', help='not to wrap with default skill')
parser.add_argument('-d', '--download', action='store_true', help='download DeepPavlov components')


class Wrapper:
    def __init__(self, config: dict, agent: Agent=None):
        self.config = config
        self.agent = agent
        self.in_queue = Queue()

        self.poller = Poller(config, self.in_queue)
        self.poller.start()

        log.info('Wrapper initiated')

        while True:
            input_q = self.in_queue.get()
            log.info('Payload received')
            self._process_input(input_q)

    def _process_input(self, input_q: dict) -> None:
        buffer = defaultdict(list)

        for message in input_q['result']:
            message_text = self._process_message_text(message['message']['text'])
            if message_text:
                chat_id = message['message']['chat']['id']
                buffer[chat_id].append(message_text)

        chats = []
        chat_ids = []
        log_msg = ''

        for chat_id, chat in buffer.items():
            chats.append(chat)
            chat_ids.append(chat_id)
            log_msg = f'{log_msg}, {str(chat_id)}' if log_msg else f'Processing messages for chats: {str(chat_id)}'

        if log_msg:
            log.info(log_msg)

        # "slices" of replicas from all conversations, each slice contains replicas from different conversation
        batched_chats = zip_longest(*chats, fillvalue=None)

        for chats_batch in batched_chats:
            utts_batch = [(chat_ids[utt_id], utt) for utt_id, utt in enumerate(chats_batch) if utt]
            j = self.config['infer_batch_length']
            chunked_utts_batch = [utts_batch[i * j:(i + 1) * j] for i in range((len(utts_batch) + j - 1) // j)]

            for chunk in chunked_utts_batch:
                batch = list(zip(*chunk))
                ids_batch = list(batch[0])
                utts_batch = list(batch[1])
                response_batch = self.agent(utts_batch, ids_batch)

                for resp in zip(ids_batch, response_batch):
                    self._send_results(*resp)

    @staticmethod
    def _process_message_text(message_text: str) -> Optional[str]:
        if message_text[:6] == '/start' or message_text[:4] == '/end':
            processed_message = None
        else:
            processed_message = message_text

        return processed_message

    def _send_results(self, chat_id, response) -> None:
        resp_text = str("{\"text\":\"" + str(response) + "\"}")

        payload = {
            'chat_id': chat_id,
            'text': resp_text
        }

        requests.post(

            url=self.config['send_message_url'],
            json=payload
        )

        log.info(f'Sent response to chat: {str(chat_id)}')


class Poller(Process):
    def __init__(self, config: dict, out_queue: Queue):
        super(Poller, self).__init__()
        self.config = config
        self.out_queue = out_queue

    def run(self) -> None:
        while True:
            self._poll()

    def _poll(self) -> None:
        interval = self.config['polling_interval_secs']
        polling_url = self.config['get_updates_url']
        payload = polling.poll(
            lambda: requests.get(polling_url).json(),
            check_success=self._estimate,
            step=interval,
            poll_forever=True,
            ignore_exceptions=(requests.exceptions.ConnectionError, json.decoder.JSONDecodeError, )
        )
        self._process(payload)

    def _estimate(self, payload: dict) -> bool:
        try:
            estimation = True if payload['result'] else False
        except Exception:
            estimation = False
        return estimation

    def _process(self, payload: dict) -> None:
        self.out_queue.put(payload)


def main() -> None:
    args = parser.parse_args()

    pipeline_config_path = find_config(args.config_path)
    host = args.host
    port = args.port
    token = args.token
    no_default_skill_wrap = args.no_default_skill

    root_path = Path(__file__).resolve().parent
    config_path = root_path / 'config.json'
    config = read_json(config_path)

    send_message_url: str = config['send_message_url_template']
    get_updates_url: str = config['get_updates_url_template']

    url_params = {
        'host': host or config['router_bot_host'],
        'port': port or config['router_bot_port'],
        'token': token or config['bot_token']
    }

    config['send_message_url'] = send_message_url.format(**url_params)
    config['get_updates_url'] = get_updates_url .format(**url_params)

    if args.download:
        deep_download(pipeline_config_path)

    model = build_model(pipeline_config_path)
    skill = model if no_default_skill_wrap else DefaultStatelessSkill(model)
    agent = DefaultAgent(skills=[skill])
    Wrapper(config, agent)

    while True:
        pass


if __name__ == '__main__':
    main()

