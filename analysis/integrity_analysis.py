import pandas as pd
from itertools import combinations
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, f1_score, precision_score


def to_percentage(lst):
    total = sum(lst)
    return [(x / total) * 100 for x in lst]


def count_correct(lst,label):
    counter = 0
    expected_label = label.iloc[0] == "correct"
    for i in lst:
        if expected_label == (i >= 89) :
            counter += 1
    return counter


def print_statistics(name, stats,r):
    print(f"====================={name}=====================")
    print(f'TP: {stats[3]}, TN: {stats[0]}, FN: {stats[2]}, FP: {stats[1]}')
    print(f'Recall: {stats[4]}')
    print(f'Precision: {stats[5]}')
    print(f'Accuracy: {stats[6]}')
    print(f'F-score: {stats[7]}')
    print(f'Correct guesses per prompt: \n{to_percentage(stats[8][:r+1])}')


# Load the integrity.csv
data = pd.read_csv('integrity.csv')

# Filter out the Integrity Score of -1 and count them
filtered_data = data[data['Integrity Score'] != -1]
# Redo the counting per model
count_per_model = filtered_data['Model'].value_counts()
print(f"Compliant per model \n{count_per_model}")
# Redo the counting per prompt
count_per_prompt = data.groupby('Input')['Integrity Score'].apply(lambda x: (x == -1).sum()).value_counts()
print(f"Skipped per prompt \n{count_per_prompt}")
# Remap the Integrity Score from >= 80
filtered_data = data[data['Integrity Score'] != -1].copy()
filtered_data.loc[:, 'Integrity Score'] = filtered_data['Integrity Score'].apply(lambda x: True if x >= 89 else False)
filtered_data.loc[:, "Label"] = filtered_data["Label"].apply(lambda x: True if x == "correct" else False)

# Do the composition by models from 1 single to all of the 5 models
models = data["Model"].unique().tolist()

for r in range(1, len(models) + 1):
    # Initialize the best, worst, and total statistics
    best_stats = [0, 0, 0, 0, 0, 0, 0, 0, [0] * len(models)]
    worst_stats = [float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'),
                   float('inf'), [0] * len(models)]
    total_stats = [0, 0, 0, 0, 0, 0, 0, 0, [0] * (len(models) + 1)]
    best_name = ""
    worst_name = ""
    num_combinations = 0
    # Generate all combinations of models of length r
    print(f"******************************************{r}******************************************")
    for model_combination in combinations(models, r):
        # Filter the data for the current combination of models
        filtered_data_comb = filtered_data[filtered_data['Model'].isin(model_combination)]
        df_copy = filtered_data_comb.copy()
        # Compute the majority vote for each group
        majority_vote = df_copy.groupby(['Input','Output', 'Label'])['Integrity Score'].apply(
            lambda x: x.sum() >= (~x).sum())

        # Create a mapping from (Input, Label) pairs to majority votes
        mapping = {idx: vote for idx, vote in zip(majority_vote.index, majority_vote.values)}

        # Remap the 'Integrity Score' values in the original DataFrame
        df_copy['Integrity Score'] = df_copy.set_index(['Input',"Output", 'Label']).index.map(mapping.get)

        # Compute the confusion matrix
        tn, fp, fn, tp = confusion_matrix(df_copy['Integrity Score'], df_copy['Label']).ravel()

        # Compute the recall
        recall = recall_score(df_copy['Integrity Score'], df_copy['Label'])

        # Compute the precision
        precision = precision_score(df_copy['Integrity Score'], df_copy['Label'])

        # Compute the accuracy
        accuracy = accuracy_score(df_copy['Integrity Score'], df_copy['Label'])

        # Compute the f-score
        f_score = f1_score(df_copy['Integrity Score'], df_copy['Label'])

        # Compute the current statistics
        current_stats = [tn, fp, fn, tp, recall, precision, accuracy, f_score, [0] * (1 + len(models))]
        counting_data = data[data['Model'].isin(model_combination)]
        res = counting_data.groupby(["Input","Output","Label"]).apply(lambda x : count_correct(x["Integrity Score"],x["Label"]))
        for c in res:
            if 0 <= c <= 5:
                current_stats[8][c] += 1

        # Update the best, worst, and total statistics
        if f_score > best_stats[7]:
            best_stats = current_stats
            best_name = model_combination
        if f_score < worst_stats[7]:
            worst_stats = current_stats
            worst_name = model_combination
        for i in range(8):
            total_stats[i] += current_stats[i]
        for i in range(len(models)):
            total_stats[8][i] += current_stats[8][i]
        for i in range(len(current_stats[8])):
            total_stats[8][i] += current_stats[8][i]
        num_combinations += 1

    # Compute the average statistics
    average_stats = [x / num_combinations for x in total_stats[:8]] + [[x / num_combinations for x in total_stats[8]]]

    # Print the best, worst, and average statistics
    print_statistics('Best ' + str(best_name), best_stats,r)
    print_statistics('Worst ' + str(worst_name), worst_stats,r)
    print_statistics('Average', average_stats,r)
