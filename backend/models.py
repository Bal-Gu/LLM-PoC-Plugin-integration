import json
import os
from typing import List, Dict

import requests

from backend.plugin import PluginController


class Model:
    def __init__(self, plugincontroller: PluginController):
        self.plugin_controller = plugincontroller
        re = requests.get("http://localhost:11434/api/tags")
        if re.status_code != 200:
            raise Exception("Server not running")

        self.installed = []
        for i in re.json()["models"]:
            self.installed.append(i["model"])
        self.config = json.load(open("../config/config.json", "rb"))
        models = self.config["required_models"]
        models += self.config["addition_models"]

        for required_model in models:
            if required_model not in self.installed:
                self.install([required_model])
                self.installed.append(required_model)

    def privacy(self, message):
        if not self.config["enforce_privacy"]:
            return message
        # TODO request the message and remove all of the privacy concerns

    def ethics(self, message):
        if not self.config["enforce_ethics"]:
            return message

    def integrity(self, message):
        if not self.config["enforce_integrity"]:
            return message

    def plugin_filtering(self, message):
        pass

    def process_message(self, messages: Dict, model: str, status: Dict, user: str, chain: List[int]):
        new_message = self.privacy(messages)
        new_message = self.ethics(new_message)
        if new_message == "I am sorry I can't comply":
            # TODO save this responsce and exit early
            pass
        ff = new_message

        for i in chain:
            if i == -1:
                ff = self.send_message_to_original_model(ff, model)
            else:
                ff = self.plugin_filtering(ff)
                ff = self.plugin_controller.execute_plugin(ff)

        self.integrity(messages)
        pass

    def install(self, models):
        print("Installing {}".format(models))
        for model in models:
            data = {"name": model}
            requests.post('http://localhost:11434/api/pull', json=data)

    def send_message_to_original_model(self, ff, model):
        response = requests.post("http://localhost:11434/api/chat", json={
            "model": model,
            "messages": ff,
            "stream": False
        })
