import csv

import pandas as pd
import requests

from analysis.isolated_model import send_message_to_original_model, privacy, redact_sensitive_info



def eval_iterration():
    df_analyzedata = pd.read_csv('analyzedata.csv')
    # Randomly select a row

    random_row = df_analyzedata.sample(n=1000)
    # Get the value of 'censorable_prompt' from the randomly selected row
    censorable_prompt = random_row.iloc[:, 0].values.tolist()
    # Get the first 1000 entries from the first row and remove "anonymize:"
    censorable_prompt = [entry.replace('anonymize:', '') for entry in censorable_prompt]
    df_random_text = pd.read_csv('random_text.csv')

    # Get all entries
    uncensorable_prompt = df_random_text.values.flatten().tolist()
    models = ["gemma:7b", "llama2:7b", "mistral:7b", "vicuna:7b", "openchat:7b"]
    with open('privacy.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Prompt", "Model", "LLMOutput", "redact_output", "compliant", "passed_jaccard", "static_caught_it",
             "need_of_censoring"])
        for m in models:
            for i in range(2000):
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
                writer.writerow(res)


eval_iterration()
