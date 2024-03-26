import os

import requests


class Model:
    def __init__(self):
        if requests.get("http://localhost:11434/api/tags").status_code != 200:
            raise Exception("Server not running")

        self.installed = []
        self.config = os.read("config/config.json")
        for required_model in self.config["models"]:
            if required_model not in self.installed:
                self.install([required_model])
                self.installed.append(required_model)

    def install(self, models):
        for model in models:
            requests.post("http://localhost:11434/api/pull/" + model, data={"name": model})