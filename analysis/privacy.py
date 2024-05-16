import csv

import pandas as pd
import requests

from analysis.isolated_model import send_message_to_original_model, privacy, redact_sensitive_info


def eval_model():
    url = "http://localhost:7860/queue/join"
    formated_input = {"data": [[["What is love ? ", "null"]], "null", "Anonymize :", "", 512, 0.7, 0.95],
                      "event_data": "null", "fn_index": 40, "trigger_id": 181, "session_hash": "i666p55k0j"}
    # Send POST request
    response = requests.post(url, data=formated_input)
    print(response.json())
    # Extract event_id from the response
    event_id = response.json()['event_id']

    # Send GET request and stream the data
    while True:
        stream_response = requests.get(f"http://localhost:7860/data?session_hash=i666p55k0j", stream=True)

        # If "msg":"process completed" is returned, break the loop
        if 'msg' in stream_response.json() and stream_response.json()['msg'] == 'process completed':
            break

    # Extract the output
    output = stream_response.json()["data"][0][0][1]

    return output


def eval_iterration():
    df = pd.read_csv('privacy.csv')
    # Get the value of 'censorable_prompt' from the randomly selected row
    censorable_prompt = df.iloc[:1000, 0].values.tolist()
    uncensorable_prompt = df.iloc[1000:2000, 0].values.tolist()

    models = [  "openchat:7b"]

    reset = (len(df) + 1) % 2000
    for m in models:
        for i in range(reset, 2000):
            print("Eval prompt with {} {}/2000".format(m, i))
            # Select an ethical or unethical prompt based on the iteration
            if i < 1000:
                prompt = censorable_prompt[i]
                label = True
            else:
                prompt = uncensorable_prompt[i - 1000]
                label = False

            llm_privacy_message = privacy(prompt, m)
            if llm_privacy_message[0]:
                redact = redact_sensitive_info(llm_privacy_message[2])
                redact_bool = redact[0]
                rd1 = redact[1]
                rds = rd1.split("¦")
                redact = tuple([redact_bool, rds[1]])
            else:
                redact = redact_sensitive_info(prompt)
            res = [
                prompt,
                m,
                llm_privacy_message[2],
                redact[1],
                llm_privacy_message[0],
                llm_privacy_message[1],
                redact[0],
                label
            ]
            # Write the result to the CSV file
            with open('privacy.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(res)
        reset = 0


eval_iterration()
