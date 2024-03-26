import  requests
class Ollama:
    def __init__(self):
        res = requests.get('http://localhost:11434/api/tags')
        if res.status_code != 200:
            exit("Error: Ollama API is not running.")
        self.models = []
        for model in res.json()["models"]:
            self.models.append(model["model"])

    def get_all_models(self):
        pass

o = Ollama()
print(o.models)