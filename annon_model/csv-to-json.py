import pandas as pd
import json

# Load the data
data = pd.read_csv('data.csv')

# Initialize an empty list to hold the data
json_data = []

# Iterate over the DataFrame
for index, row in data.iterrows():
    # Create a dictionary for each row
    row_dict = {
        "instruction": "Anonymize :",
        "input": row[0].replace("Anonymize:",""),
        "output": row[1]
    }
    # Append the dictionary to the list
    json_data.append(row_dict)

# Convert the list to JSON
json_data = json.dumps(json_data)

with open('anon.json', 'w') as f:
    f.write(json_data)