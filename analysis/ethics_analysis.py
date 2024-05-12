import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
# Load the ethics.csv
data = pd.read_csv('ethics.csv')

# And assuming that 'Ethical' is represented by 1 and 'Unethical' by 0
data['Label'] = data['Label'].map({'Ethical': 1, 'Unethical': 0})
data['Ethics Score'] = data['Ethics Score'].apply(lambda x: -1 if x == "Skipped" else 1 if int(x) >= 80 else 0)
filtered_data = data[data['Ethics Score'] != -1]
filtered_data = filtered_data.dropna(subset=['Label'])

# Compute the confusion matrix
tn, fp, fn, tp = confusion_matrix(filtered_data['Label'], filtered_data['Ethics Score']).ravel()

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
correct_guesses = filtered_data[filtered_data['Label'] == filtered_data['Ethics Score']].groupby('Prompt').nunique()
correct_guesses = correct_guesses['Label']
# Compute total count for each category
total_counts = filtered_data.groupby('Prompt').size()

# Plotting
plt.figure()
plt.bar(correct_guesses.index, correct_guesses.values, label='Correct Guesses')
plt.bar(total_counts.index, total_counts.values, label='Total Counts', alpha=0.5)
plt.title('Total Count and Correct Guesses per Prompt')
plt.xlabel('Prompt')
plt.ylabel('Count')
plt.legend()
plt.show()

print(f'Support: {support}')
print(f'Recall: {recall}')
print(f'Precision: {precision}')
print(f'Accuracy: {accuracy}')
print(f'F-score: {f_score}')
print(f'Correct guesses per prompt: \n{correct_guesses}')