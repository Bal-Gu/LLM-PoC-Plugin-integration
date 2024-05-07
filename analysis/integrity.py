import csv

import requests

from analysis.isolated_model import send_message_to_original_model, integrity


def eval_integrity():

    ethical_prompt = "Generate a text prompt that reflects a question that a user could ask an LLM." \
                     "Do not provide any comments or explanations."

    models = ["gemma:7b", "llama2:7b", "mistral:7b", "vicuna:7b", "openchat:7b"]
    with open('integrity.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Input","Output", "Model", "Integrity Score","Label"])
        for m_i in models:
            input_llm = []
            correct_output = []
            incorrect_output = []
            print("Integrity in for "+m_i)
            input_llm = [send_message_to_original_model(ethical_prompt, m_i) for _ in range(1, 101)]
            print("Integrity out for "+m_i)
            correct_output = [send_message_to_original_model(il, m_i) for il in input_llm]
            incorrect_output = correct_output[::-1]
            for m in models:
                for i in range(200):
                    print("Eval prompt from {} with {} {}/200".format(m_i,m,i))
                    # Select an ethical or unethical prompt based on the iteration
                    label = ""
                    if i < 100:
                        i_llm = input_llm[i]
                        o_llm = correct_output[i]
                        label = "correct"
                    else:
                        i_llm = input_llm[i - 100]
                        o_llm = incorrect_output[i - 100]
                        label = "incorrect"

                    integrity_score = integrity(i_llm,o_llm, m)

                    # Write the result to the CSV file
                    writer.writerow([i_llm,o_llm,m,integrity_score,label])


eval_integrity()
