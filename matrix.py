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
        word_list.append(word)

    idx = 0
    for punctuation in tree.findall(".//c"):
        try:
            word = punctuation.text.strip()
            word_list.append(word)
        except AttributeError:
            pass

    for multi_word in tree.findall(".//mw"):
        mw = ""

        for word in multi_word:
            mw += word.text
        
        mw = mw.strip()
        word_list.append(mw)
    
    return word_list

def main():

    global TAG_DICT
    TAG_DICT = generate_dict('tag')
    global WORD_TAG_DICT
    WORD_TAG_DICT = generate_dict('word_tag')
    global WORD_DICT
    WORD_DICT = generate_dict('word')


    word_list = list()

    testing_files = glob.glob("Test-corpus/*/*.xml")
    for fname in testing_files:
        word_list += parse_single_xml(fname)

    for word in word_list:
        try:
            text = colored(f'{word}: {predict_tag_naive(word)}', 'green')
        except KeyError:
            pass

if __name__ == '__main__':
    main()
