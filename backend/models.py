import json
import os
import re
from typing import List, Dict

import requests

from backend.database import Database
from backend.jaccard import is_text_similar
from backend.plugin import PluginController


class Model:
    def __init__(self, plugincontroller: PluginController, database: Database):
        self.plugin_controller = plugincontroller
        self.db = database
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

    def redact_sensitive_info(self, text: str):
        # Define regular expressions for different types of sensitive information
        email_regex = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        phone_regex = r'\b[0-9]{3}-\[0-9]{3}-\[0-9]{4}\b'
        social_regex = r'-?\d{4}[/-]?\d{4}[/-]?\d{4}'
        financial_regex = r'(?:^|[\s\t])(\d{4}[/-]?\d{4}[/-]?\d{4})$'
        new_text = text
        # Loop through the text and replace sensitive information with '^^'
        for match in re.finditer(email_regex, new_text):
            new_text = new_text.replace(match.group(), '^^')
        for match in re.finditer(phone_regex, new_text):
            new_text = new_text.replace(match.group(), '^^')
        for match in re.finditer(social_regex, new_text):
            new_text = new_text.replace(match.group(), '^^')
        for match in re.finditer(financial_regex, new_text):
            new_text = new_text.replace(match.group(), '^^')

        return text

    def privacy(self, message,message_id):
        if not self.config["enforce_privacy"]:
            return message

        prompt = """
        The objective is to identify and redact any piece of information that could be deemed sensitive or personal.
        This includes, but is not limited to, names, addresses, phone numbers, email addresses, social security numbers, financial information, and any other details that could compromise privacy or confidentiality.
        Whenever the LLM detects such information, it should replace the entire segment with '^^'.
        The output should be the original text with all the sensitive content effectively obscured, ensuring privacy and security are maintained.
        Include examples of different types of sensitive information in the text and demonstrate how the LLM processes and redacts these segments, replacing them with '@@@@@'
        It is very important mark the start of the censored
        text with ¦ and end it with ¦
        The following text is:\n
        """

        private_message = """
        ¦
        {}
        ¦
        """.format(message)
        size = len(self.config["required_models"])
        counter = 1
        for model in ["gemma:7b", "llama2:7b", "mistral:7b", "vicuna:7b", "openchat:7b"]:
            self.db.parallelize_and_ignore("UPDATE message SET content = %s WHERE id = %s",
                                           ["Ethics calculations for {} {}/{}".format(model, counter, size),
                                            message_id])
            response = requests.post("http://localhost:11434/api/chat", json={
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": prompt + private_message
                }],
                "stream": False
            })

            print(response.json()["message"]["content"])
            if re.search(r"¦(.|\n)*\S+(.|\n)*¦", response.json()["message"]["content"]):
                new_message = str(response.json()["message"]["content"]).split("¦")[1]
                if not re.search("I cannot fulfill your request", new_message):
                    tmp_private_message = "¦\n" + new_message + "¦\n"
                    if is_text_similar(tmp_private_message,private_message):
                        # dismisses hallucination cases
                        private_message = tmp_private_message

        return self.redact_sensitive_info(private_message).split("¦")[1]
        # TODO request the message and remove all of the privacy concerns


    def ethics(self, message, message_id):
        if not self.config["enforce_ethics"]:
            return True
        size = len(self.config["required_models"])
        counter = 1
        for model in self.config["required_models"]:
            self.db.parallelize_and_ignore("UPDATE message SET content = %s WHERE id = %s",
                                           ["Ethics calculations for {} {}/{}".format(model, counter, size),
                                            message_id])
            counter += 1
        return True

    def integrity(self, message):
        if not self.config["enforce_integrity"]:
            return message
        return message

    def plugin_filtering(self, message):
        pass

    def process_message(self, messages: Dict, model: str, user_message_id: int, assistant_message_id: int,
                        chain: List[int]):
        message_to_process = messages["messages"][-1]["content"]
        new_message = self.privacy(message_to_process,user_message_id)
        # update the message to the filtered one and close the loading
        self.db.parallelize_and_ignore("UPDATE message SET content = %s, status = 1 WHERE id = %s",
                                       [new_message, user_message_id])
        passed_ethics = self.ethics(new_message,assistant_message_id)
        if not passed_ethics:
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
        self.db.parallelize_and_ignore("UPDATE message SET content = %s, status = 1 WHERE id = %s",
                                       [ff, assistant_message_id])
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
