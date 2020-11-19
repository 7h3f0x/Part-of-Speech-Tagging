#!/usr/bin/python3
import glob
import xml.etree.ElementTree as ET

from termcolor import colored

TAG_DICT = dict()
WORD_TAG_DICT = dict()
WORD_DICT = dict()

def print_as_table(dictionary: dict, first_col_name: str):
    print("-"*57)
    print(f"| {first_col_name:>30} | {'count':>20} |")
    print("-"*57)
    for key, value in sorted(dictionary.items(), key=lambda x:x[0]):
        print(f"| {key:>30} | {value:20} |")
    print("-"*57)


def generate_dict(fname, delim = '~ '):

    generated_dict = dict()

    with open(fname, 'r') as f:
        for line in f:
            key = line.split(delim)[0]
            val = int(line.split(delim)[1])
            generated_dict[key] = int(val)

    return generated_dict

def generate_probability(word: str, tag: str):

    return ( WORD_TAG_DICT.get(f'{word}_{tag}', 0) / WORD_DICT[f'{word}'] )

def predict_tag_naive(word: str):
    
    max_prob = 0.0
    tag_predicted = ''

    for tag in TAG_DICT.keys():
        tag_prob = generate_probability(word, tag)
        if max_prob < tag_prob:
            max_prob = tag_prob
            tag_predicted = tag

    if tag_predicted:
        return tag_predicted

    return None

def parse_single_xml(xml_file):
    tree = ET.parse(xml_file)
    pos_list = tree.findall(".//w")

    word_list = list()
    for pos in pos_list:
        word = pos.text.strip()
        tags = pos.get('c5').split('-')
        word_list.append([word, tags])

    idx = 0
    for punctuation in tree.findall(".//c"):
        try:
            word = punctuation.text.strip()
            tags = pos.get('c5').split('-')
            word_list.append([word, tags])
        except AttributeError:
            pass

    for multi_word in tree.findall(".//mw"):
        mw = ""

        for word in multi_word:
            mw += word.text
        
        mw = mw.strip()
        tags = multi_word.get("c5").split('-')
        word_list.append([mw, tags])
    
    return word_list

def main():

    global TAG_DICT
    TAG_DICT = generate_dict('tag')
    global WORD_TAG_DICT
    WORD_TAG_DICT = generate_dict('word_tag')
    global WORD_DICT
    WORD_DICT = generate_dict('word')


    word_list = list()

    # testing_files = glob.glob("Test-corpus/*/*.xml")
    # for fname in testing_files:
    #     word_list += parse_single_xml(fname)

    word_list = parse_single_xml("Test-corpus/AS/ASD.xml")

    for word in word_list:
        try:
            text = colored(f'{word}: {predict_tag_naive(word)}', 'green')
        except KeyError:
            pass

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

    for word_tag in word_list:
        word =word_tag[0]
        try:
            tag_predicted = predict_tag_naive(word)
            
            for tag in word_tag[1]:
                confusion_matrix[tag_dict[tag]][tag_dict[tag_predicted]] = confusion_matrix[tag_dict[tag]][tag_dict[tag_predicted]] + 1
        except:
            pass

    for i in range(len(tag_dict.keys())):
        sum_row = 0
        for j in range(len(tag_dict.keys())):
            sum_row += confusion_matrix[i][j]

        confusion_matrix[i][idx] = sum_row

    for i in range(len(tag_dict.keys())):
        sum_col = 0
        for j in range(len(tag_dict.keys())):
            sum_col += confusion_matrix[j][i]

        confusion_matrix[idx][i] = sum_col

    correct_pred = 0
    for i in range(len(tag_dict.keys())):
        correct_pred += confusion_matrix[i][i]

    print(f'{correct_pred}: {len(word_list)}')

    print(confusion_matrix)

if __name__ == '__main__':
    main()
