#!/usr/bin/env python3

# vim:sw=4:ts=4:expandtab
import glob
import xml.etree.ElementTree as ET

def print_as_table(dictionary: dict, first_col_name: str):
    print("-"*57)
    print(f"| {first_col_name:>30} | {'count':>20} |")
    print("-"*57)
    for key, value in sorted(dictionary.items(), key=lambda x:x[0]):
        print(f"| {key:>30} | {value:20} |")
    print("-"*57)


TRAINING_FILES = glob.glob("Train-corups/*/*.xml")

WORD_TAG_COUNT = dict()
WORD_COUNT = dict()
TAG_COUNT = dict()


for fname in TRAINING_FILES:
    tree = ET.parse(fname)
    pos_list = tree.findall(".//w") # Get all children with w tag
    for pos in pos_list:
        word = pos.get('hw')
        WORD_COUNT[word] = WORD_COUNT.get(word, 0) + 1
        tags = pos.get('c5').split("-")
        for tag in tags:
            WORD_TAG_COUNT[f"{word}_{tag}"] = WORD_TAG_COUNT.get(f"{word}_{tag}", 0) + 1
            TAG_COUNT[tag] = TAG_COUNT.get(tag, 0) + 1

print("Finished")

print_as_table(WORD_TAG_COUNT, "word_tag")
print_as_table(WORD_COUNT, "word")
print_as_table(TAG_COUNT, "tag")
