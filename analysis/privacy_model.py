import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, f1_score, precision_score

# Load the privacy_model.csv
data = pd.read_csv('privacy_model2.csv')

# Add a new column "predict" that checks if the output column contains the char '^'.
data['predict'] = data['output'].apply(lambda x : '^' in str(x))

# Convert the boolean values to integers (True to 1 and False to 0)
data['predict'] = data['predict'].astype(int)
data['boolean'] = data['boolean'].astype(int)

# Compute the confusion matrix
tn, fp, fn, tp = confusion_matrix(data['boolean'], data['predict']).ravel()

# Print out the TP, FP, FN, FP
print(f'True Positives: {tp}')
print(f'False Positives: {fp}')
print(f'False Negatives: {fn}')
print(f'True Negatives: {tn}')

# Print out the accuracy, precision, recall, f-score
print(f'Accuracy: {accuracy_score(data["boolean"], data["predict"])}')
print(f'Precision: {precision_score(data["boolean"], data["predict"])}')
print(f'Recall: {recall_score(data["boolean"], data["predict"])}')
print(f'F1 Score: {f1_score(data["boolean"], data["predict"])}')

# Compute specificity
specificity = tn / (tn+fp)
print(f'Specificity: {specificity}')