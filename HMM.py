import glob
import xml.etree.ElementTree as ET
import pickle
import os
from typing import Iterator


WORD_TAG_DICT =dict()
WORD_DICT = dict()
TAG_DICT = dict()
TAG_TRANSITION = dict()
start_count = 0


def parse_sentence(sentence: list, train: bool) -> list:
    global TAG_TRANSITION
    prev_tags = ["^"]
    word_list = list()
    for word in sentence:
        if word.tag != "mw":
            try:
                text = word.text.strip()
                tags = word.get("c5").split("-")
            except:
                continue
        else:
            text = ""
            for w in word:
                text += w.text
            text = text.strip()
            tags = word.get("c5").split("-")


        word_list.append([text, tags])
        if train:
            for prev_tag in prev_tags:
                for tag in tags:
                    TAG_TRANSITION[f"{tag}_{prev_tag}"] = TAG_TRANSITION.get(f"{tag}_{prev_tag}", 0) + 1
        prev_tags = tags
    return word_list


def parse_single_xml(xml_fname: str, train=False) -> list:
    tree = ET.parse(xml_fname)
    sentences = tree.findall(".//s") # get all sentences

    sentence_list = list()
    for sentence in sentences:
        sentence_list.append(parse_sentence(sentence, train))
    return sentence_list


def train():
    global WORD_TAG_DICT
    global WORD_DICT
    global TAG_DICT
    global TAG_TRANSITION
    global start_count

    if os.path.exists("./cache"):
        with open('./cache', 'rb') as f:
            WORD_TAG_DICT, WORD_DICT, TAG_DICT, TAG_TRANSITION, start_count = pickle.load(f)
        return

    for fname in glob.glob("Train-corups/A*/*.xml"):
        sentence_list = parse_single_xml(fname, train=True)
        for word_list in sentence_list:
            for word, tags in word_list:
                for tag in tags:
                    WORD_DICT[word] = WORD_DICT.get(word, 0) + 1
                    TAG_DICT[tag] = TAG_DICT.get(tag, 0) + 1
                    WORD_TAG_DICT[f"{word}_{tag}"] = WORD_TAG_DICT.get(f"{word}_{tag}", 0) + 1

    start_count = sum(TAG_TRANSITION.values())
    with open('./cache', 'wb') as f:
        pickle.dump([WORD_TAG_DICT, WORD_DICT, TAG_DICT, TAG_TRANSITION, start_count], f)


def probability_tag_tag(tag: str, prev_tag: str) -> float:
    if prev_tag == "^":
        return TAG_TRANSITION.get(f"{tag}_{prev_tag}", 0) / start_count
    else:
        return TAG_TRANSITION.get(f"{tag}_{prev_tag}", 0) / TAG_DICT.get(prev_tag, 0)


def probability_word_tag(word: str, tag: str) -> float:
    tmp = WORD_TAG_DICT.get(f"{word}_{tag}", 0)
    if tmp == 0:
        return 1 / TAG_DICT.get(tag, 0)
    return  tmp / TAG_DICT.get(tag, 0)

def viterbi(sentence: list) -> list:
    probability_matrix = [{key: 0.0 for key in TAG_DICT} for _ in range(len(sentence))]
    back_ptr = [{key: None for key in TAG_DICT} for _ in range(len(sentence))]
    for tag in TAG_DICT:
        probability_matrix[0][tag] = probability_tag_tag(tag, "^") * probability_word_tag(sentence[0], tag)
        back_ptr[0][tag] = None

    for idx in range(len(sentence)):
        for tag in TAG_DICT:
            for prev_tag in TAG_DICT:
                back_probability = probability_matrix[idx - 1][prev_tag] * probability_tag_tag(tag, prev_tag) * probability_word_tag(sentence[idx], tag)
                if  back_probability > probability_matrix[idx][tag]:
                    probability_matrix[idx][tag] = back_probability
                    back_ptr[idx][tag] = prev_tag
    
    best_probability = max(probability_matrix[idx], key=probability_matrix[idx].get)
    sequence = list()
    iterator = best_probability
    while iterator is not None:
        sequence.append(iterator)
        iterator = back_ptr[idx][iterator]
        idx -= 1
    sequence.reverse()
    return sequence


def main():
    train()

    tag_dict = dict()
    idx = 0
    for key in TAG_DICT.keys():
        tag_dict[key] = idx
        idx += 1


    confusion_matrix = list()

    for i in range(len(tag_dict.keys()) + 1):
        t = list()
        for j in range(idx + 1):
            t.append(0)
        confusion_matrix.append(t)

    word_count = 0
    for fname in glob.glob("Test-corpus/A*/*.xml"):
        for sentence in parse_single_xml(fname):
            words = [word[0] for word in sentence]
            predicted_tags = viterbi(words)
            try:
                for i in range(len(sentence)):
                    word_count += 1
                    tag_predicted = predicted_tags[i]
                    for tag in sentence[i][1]:
                        confusion_matrix[tag_dict[tag]][tag_dict[tag_predicted]] = confusion_matrix[tag_dict[tag]][tag_dict[tag_predicted]] + 1
            except:
                print(sentence)
                print(predicted_tags)

            # break
        break

    for i in range(len(tag_dict.keys())):
        sum_row = 0
        for j in range(len(tag_dict.keys())):
            sum_row += confusion_matrix[i][j]

        confusion_matrix[i][idx] = sum_row

    for i in range(len(tag_dict.keys())):
        sum_col = 0
        for j in range(len(tag_dict.keys())):
            sum_col += confusion_matrix[j][i]

    correct_pred = 0
    for i in range(len(tag_dict.keys())):
        correct_pred += confusion_matrix[i][i]

    print(correct_pred, word_count)

if __name__ == "__main__":
    main()
