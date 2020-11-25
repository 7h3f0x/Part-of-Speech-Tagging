import pickle
import glob

number_of_files = len(glob.glob("Test-corpus/A*/*.xml"))


confusion_matrices_files = sorted(glob.glob("./confusion_matrices/*_*"))
word_count_files = sorted(glob.glob("./word_count/*_*"))


word_count = 0

for fname in word_count_files:
    with open(fname, "rb") as f:
        count = pickle.load(f)
        word_count += count

confusion_matrices = list()

tag_count = 0

for fname in confusion_matrices_files:
    with open(fname, "rb") as f:
        matrix = pickle.load(f)
        for i in matrix:
            tag_count = len(i)
            break
        confusion_matrices.append(matrix)

final_confusion_matrix = list()

for i in range(63):
    row = list()
    for j in range(63):
        row.append(0)
    final_confusion_matrix.append(row)

for i in range(62):
    for j in range(62):
        val = 0
        for matrix in confusion_matrices:
            val += matrix[i][j]
        final_confusion_matrix[i][j] = val

for i in range(62):
    sum_row = 0
    for j in range(62):
        sum_row += final_confusion_matrix[i][j]

    final_confusion_matrix[i][62] = sum_row

for i in range(62):
    sum_col = 0
    for j in range(62):
        sum_col += final_confusion_matrix[j][i]
    final_confusion_matrix[62][i] = sum_col

correct_pred = 0
for i in range(62):
    correct_pred += final_confusion_matrix[i][i]

print('\n\n')
print(f'Number of words: {word_count}\nCorrectly Predicted: {correct_pred}\n\n')

print(f'Accuracy: {correct_pred/word_count*100}')

with open('./cache', 'rb') as f:
    WORD_TAG_DICT, WORD_DICT, TAG_DICT, TAG_TRANSITION, start_count = pickle.load(f)
idx = 0


# Predicting fscore now
tag_dict = dict()

for key in TAG_DICT.keys():
    tag_dict[key] = idx
    idx += 1


for tag in tag_dict.keys():
    # false positive is basically last value of row/column :p. Maths hack
    true_positive = final_confusion_matrix[tag_dict[tag]][tag_dict[tag]]
    false_positive = final_confusion_matrix[tag_dict[tag]][62]
    false_negative = final_confusion_matrix[62][tag_dict[tag]]

    fscore = 2*true_positive/(false_negative + false_positive)


