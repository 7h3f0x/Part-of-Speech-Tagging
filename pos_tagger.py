#!/usr/bin/env python3

# vim:sw=4:ts=4:expandtab
import glob
import xml.etree.ElementTree as ET
import os

dirname = "./tag-list"
TRAINING_LISTS = list()


def print_as_table(dictionary: dict, first_col_name: str):
    print("-"*57)
    print(f"| {first_col_name:>30} | {'count':>20} |")
    print("-"*57)
    for key, value in sorted(dictionary.items(), key=lambda x:x[0]):
        print(f"| {key:>30} | {value:20} |")
    print("-"*57)


def report_top_n(dictionary:dict, n=10):
    print("-"*57)
    for key, value in sorted(dictionary.items(), key=lambda x:x[1], reverse=True)[:n]:
        print(f"| {key:>30} | {value:20} |")
    print("-"*57)


def write_to_file(fname, data):

    # Let's use the same func to write lists as well as dicts to file
    if type(data) == type({}):
        write_data = ''
        for key in data:
            write_data += f"{key}: {data[key]}\n"
        with open(fname, 'w') as f:
            f.write(write_data)

    if type(data) == type([]):
        write_data = ''
        for val in data:
            write_data += f"{val}\n"

        with open(fname, 'w') as f:
            f.write(write_data)


def parse_single_xml(xml_file):
    tree = ET.parse(xml_file)
    pos_list = tree.findall(".//w")

    word_tag_list = list()
    for pos in pos_list:
        word = pos.text.strip()
        tags = pos.get('c5').split('-')

        for tag in tags:
            word_tag_list.append(f"{word}_{tag}")

    for punctuation in tree.findall(".//c"):
        word = punctuation.text.strip()
        tags = punctuation.get('c5').split('-')

        for tag in tags:
            word_tag_list.append(f"{word}_{tag}")

    for multi_word in tree.findall(".//mw"):
        mw = ""

        for word in multi_word:
            mw += word.text

        mw = mw.strip()
        tags = multi_word.get("c5")

        for tag in tags:
            word_tag_list.append(f"{mw}_{tag}")


    TRAINING_LISTS.append(word_tag_list)    # We keep a list of all the word_tag lists generate
    # Let's dump it to a file now
    fname = f"{dirname}/{xml_file.split('/')[-1].replace('.xml','')}"
    write_to_file(fname, word_tag_list)


WORD_TAG_COUNT = dict()
WORD_COUNT = dict()
TAG_COUNT = dict()


def main():

    # Let's first create a directory to store all the lists we create
    try:
        os.mkdir(dirname)
    except FileExistsError:
        pass

    training_files = glob.glob("Train-corups/*/*.xml")
    for fname in training_files:
        parse_single_xml(fname)

    for word_tag_list in TRAINING_LISTS:

        for word_tag in word_tag_list:
            word, tag = word_tag.split('_')
            WORD_COUNT[word] = WORD_COUNT.get(word, 0) + 1
            WORD_TAG_COUNT[f"{word}_{tag}"] = WORD_TAG_COUNT.get(f"{word}_{tag}", 0) + 1
            TAG_COUNT[tag] = TAG_COUNT.get(tag, 0) + 1

    print("Top 10 most frequent words:")
    report_top_n(WORD_COUNT)
    print("\nTop 10 most frequent tags:")
    report_top_n(TAG_COUNT)

if __name__ == "__main__":
    main()
