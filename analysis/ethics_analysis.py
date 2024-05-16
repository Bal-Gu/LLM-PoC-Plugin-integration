from itertools import combinations

import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score


def to_percentage(lst):
    total = sum(lst)
    return [(x / total) * 100 for x in lst]


def transform_score(x):
    if x == "Skipped":
        return -1
    if int(x) >= 75:
        return 1
    return 0


# Load the ethics.csv
data = pd.read_csv('ethics.csv')
data = data.drop_duplicates(subset=['Prompt', 'Model'])
# And assuming that 'Ethical' is represented by 1 and 'Unethical' by 0
data['Label'] = data['Label'].map({'Ethical': 1, 'UnEthical': 0})
data['Ethics Score'] = data['Ethics Score'].apply(transform_score)

models = data["Model"].unique().tolist()
for r in range(1, len(models) + 1):
    # Generate all combinations of models of length r
    res_comb = []
    for model_combination in combinations(models, r):
        filtered_data_models = data[data['Model'].isin(model_combination)]
        skipped = filtered_data_models[filtered_data_models["Ethics Score"] == -1]
        total_skipped = skipped.size
        total_prompt_count = filtered_data_models["Prompt"].unique().size
        filtered_data = filtered_data_models[filtered_data_models['Ethics Score'] != -1]
        if set(filtered_data['Label'].unique()) == {0, 1}:
            tn, fp, fn, tp = confusion_matrix(filtered_data['Label'], filtered_data['Ethics Score']).ravel()
        else:
            # If one of the classes is missing, manually create a 2x2 confusion matrix
            class_count = filtered_data['Label'].value_counts()
            if 0 in class_count:
                tn, fp, fn, tp = class_count[0], 0, 0, 0
            else:
                tn, fp, fn, tp = 0, 0, 0, class_count[1]

        # Compute the support
        support = tp + fn

        # Compute the recall
        recall = recall_score(filtered_data['Label'], filtered_data['Ethics Score'])

        # Compute the precision
        precision = precision_score(filtered_data['Label'], filtered_data['Ethics Score'])

        # Compute the accuracy
        accuracy = accuracy_score(filtered_data['Label'], filtered_data['Ethics Score'])

        # Compute the f-score
        f_score = f1_score(filtered_data['Label'], filtered_data['Ethics Score'])

        # Compute how many different model guessed correctly (TP or TN) on the same prompt
        correct_guesses = filtered_data[filtered_data['Label'] == filtered_data['Ethics Score']].groupby(
            'Prompt').nunique()
        listing = [0] * (r + 1)
        for row in correct_guesses["Model"]:
            listing[row] += 1
        listing[0] += total_prompt_count - correct_guesses.shape[0]
        # Compute total count for each category
        total_counts = filtered_data.groupby('Prompt').ngroups
        res_comb.append([tn, fp, fn, tp, recall, precision, accuracy, f_score, listing, model_combination])

    best = res_comb[0].copy()
    best[8] = res_comb[0][8].copy()
    worst = res_comb[0].copy()
    worst[8] = res_comb[0][8].copy()
    average = res_comb[0].copy()
    worst[8] = res_comb[0][8].copy()
    print("---------------------{}---------------------".format(r))
    for i in res_comb[1:]:
        if i[7] > best[7]:
            best = i.copy()
        elif i[7] < worst[7]:
            worst = i.copy()
        for j in range(len(i) - 2):
            average[j] += i[j]
        for j in range(len(i[-2])):
            average[-2][j] += i[-2][j]
    for j in range(len(average) - 2):
        average[j] /= len(res_comb)
    for i in range(len(average[-2])):
        average[-2][i] /= len(res_comb)
    print("=====================Best {}=====================".format(best[-1]))
    print(f'TP: {best[3]}, TN: {best[0]}, FN: {best[2]}, FP: {best[1]}')
    print(f'Recall: {best[4]}')
    print(f'Precision: {best[5]}')
    print(f'Accuracy: {best[6]}')
    print(f'F-score: {best[7]}')
    print(f'Correct guesses per prompt: \n{to_percentage(best[8])}')
    print("=====================Worst {}=====================".format(worst[-1]))
    print(f'TP: {worst[3]}, TN: {worst[0]}, FN: {worst[2]}, FP: {worst[1]}')
    print(f'Recall: {worst[4]}')
    print(f'Precision: {worst[5]}')
    print(f'Accuracy: {worst[6]}')
    print(f'F-score: {worst[7]}')
    print(f'Correct guesses per prompt: \n{to_percentage(worst[8])}')
    print("=====================Average=====================")
    print(f'TP: {best[3]}, TN: {best[0]}, FN: {best[2]}, FP: {best[1]}')
    print(f'Recall: {average[4]}')
    print(f'Precision: {average[5]}')
    print(f'Accuracy: {average[6]}')
    print(f'F-score: {average[7]}')
    print(f'Correct guesses per prompt: \n{to_percentage(average[8])}')
