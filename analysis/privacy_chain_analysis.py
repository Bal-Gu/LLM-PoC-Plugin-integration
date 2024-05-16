import pandas as pd
from sklearn.metrics import confusion_matrix


def calculate_metrics(confusion):
    tn, fp, fn, tp = confusion
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    specificity =  tn/ (tn + fp)
    f_score = 2 * (precision * recall) / (precision + recall)
    return pd.Series({'accuracy': accuracy, 'Precison': precision, 'recall': recall, 'specificity': specificity, 'f_score': f_score})


# Load the data
data = pd.read_csv('privacy.csv')
data["censored"] = data["redact_output"].apply(lambda x: '~' in x or '^' in x)
# Compute the percentage of compliance
compliance_percentage = (data['compliant'].mean()) * 100
print(f'Compliance Percentage: {compliance_percentage}%')

# Compute the percentage of compliance by model
compliance_by_model = data.groupby('Model')['compliant'].mean() * 100
print(f'Compliance Percentage by Model:\n{compliance_by_model}')

# Compute the percentage of compliance by prompt
compliance_by_prompt = data.groupby('Prompt')['compliant'].sum()
compliance_by_prompt = compliance_by_prompt.value_counts(normalize=True)

# Compute the compliance if needed vs not needed
compliance_with_positive_label = data[data['need_of_censoring'] == 1]["compliant"].mean() * 100
compliance_with_negative_label = data[data['need_of_censoring'] == 0]["compliant"].mean() * 100
# Check vicuna compliance
print(
    f"\nCompliance per need {compliance_with_positive_label} vs compliance if not needed {compliance_with_negative_label}\n")
vicuna_compliance_positve_label = data[(data['need_of_censoring'] == 1) & (data["Model"] == "vicuna:7b")][
                                      "compliant"].mean() * 100
vicuna_compliance_negative_label = data[(data['need_of_censoring'] == 0) & (data["Model"] == "vicuna:7b")][
                                       "compliant"].mean() * 100
print(
    f"\nCompliance vicuna per need {vicuna_compliance_positve_label} vs compliance if not needed {vicuna_compliance_negative_label}\n")

# Check llama compliance
print(
    f"\nCompliance per need {compliance_with_positive_label} vs compliance if not needed {compliance_with_negative_label}\n")
test = data[(data['need_of_censoring'] == 1) & (data["Model"] == "llama:7b")]
llama_compliance_positve_label = data[(data['need_of_censoring'] == 1) & (data["Model"] == "llama2:7b")][
                                     "compliant"].mean() * 100
llama_compliance_negative_label = data[(data['need_of_censoring'] == 0) & (data["Model"] == "llama2:7b")][
                                      "compliant"].mean() * 100

print(
    f"\nCompliance llama per need {llama_compliance_positve_label} vs compliance if not needed {llama_compliance_negative_label}\n")

openchat_compliance_positve_label = data[(data['need_of_censoring'] == 1) & (data["Model"] == "openchat:7b")][
                                        "compliant"].mean() * 100
openchat_compliance_negative_label = data[(data['need_of_censoring'] == 0) & (data["Model"] == "openchat:7b")][
                                         "compliant"].mean() * 100

print(
    f"\nCompliance openchat per need {openchat_compliance_positve_label} vs compliance if not needed {openchat_compliance_negative_label}\n")

# Group the data by 'Prompt' and check if all values in 'compliant' are False

print(f'Compliance Percentage by Prompt:\n{compliance_by_prompt}')

# Compute the percentage of all passed_jaccard (only if compliant)
passed_jaccard_percentage = (data[data['compliant'] == 1]['passed_jaccard'].mean()) * 100
print(f'Passed Jaccard Percentage (if compliant): {passed_jaccard_percentage}%')

# Compute the percentage of all static_caught_it (only if compliant)
static_caught_it_percentage = (data[data['compliant'] == 1]['static_caught_it'].mean()) * 100
print(f'Static Caught It Percentage (if compliant): {static_caught_it_percentage}%')

# Add a new column where we do an OR of passed_jaccard and static_caught_it
data['censored_or_static'] = (data['censored'] | data['static_caught_it'])

# Compare it with the need_of_censoring and then add it as a confusion matrix
tn, fp, fn, tp = confusion_matrix(data[data['compliant'] == 1]['need_of_censoring'],
                                  data[data['compliant'] == 1]['censored_or_static']).ravel()
print(f'Confusion Matrix (need_of_censoring vs censored_or_static):\ntp\t{tp}\nfp\t{fp}\nfn\t{fn}\ntn\t{tn}')

# Compute a confusion matrix per model based on censored and need_of_censoring
confusion_by_model = data.groupby('Model').apply(
    lambda x: confusion_matrix(x[(x['compliant'] == 1) & (x["passed_jaccard"] == 1)]['need_of_censoring'],
                               x[(x['compliant'] == 1) & (x["passed_jaccard"] == 1)]['censored']).ravel())
print(f'Confusion Matrix by Model (censored vs need_of_censoring):\n{confusion_by_model}')

metrics_by_model = confusion_by_model.apply(calculate_metrics)

print(f'Metrics by Model:\n{metrics_by_model}')

# Checks the effectivness as a backup plan of the static analysis
safety_net = data[(data['compliant'] == 1) & (data['passed_jaccard'] == 0) & (data["need_of_censoring"] == 1)][
    "static_caught_it"].value_counts()
safety_net2 = data[(data['compliant'] == 1) & (data['passed_jaccard'] == 1) & data["censored"] == 0 & (
            data["need_of_censoring"] == 1)]["static_caught_it"].value_counts()

print(f"{safety_net[True] / (safety_net[False] + safety_net[True])}")
print(f"{safety_net2[True] / (safety_net2[False] + safety_net2[True])}")

# Group the data by 'Prompt' and calculate the predicted values
data['predicted'] = data.groupby('Prompt').apply(lambda x: (x['censored'] | x['static_caught_it']).any()).reindex(
    data['Prompt']).values

# Convert the predicted values to integers (True to 1 and False to 0)
data['predicted'] = data['predicted'].astype(int)

# Calculate the confusion matrix
tn, fp, fn, tp = confusion_matrix(data['need_of_censoring'], data['predicted']).ravel()
out = calculate_metrics((tn, fp, fn, tp))
print(f'Confusion Matrix full:\n{out}')


# Filter the data where 'compliant' is 1
filtered_data = data[(data["compliant"] == 1) & (data["passed_jaccard"] == 1)].copy()

# Group the data by 'Prompt' and check if there's at least one 'True' value in 'censored'
grouped_data = filtered_data.groupby('Prompt')['censored'].any()

# Map the grouped data back to the 'censored' column in the original DataFrame
filtered_data.loc[:, 'censored'] = filtered_data['Prompt'].map(grouped_data)

# Calculate the confusion matrix
tn, fp, fn, tp = confusion_matrix(filtered_data['need_of_censoring'], filtered_data['censored']).ravel()
out = calculate_metrics((tn, fp, fn, tp))
print(f'Confusion Matrix filtered :\n{out}')
