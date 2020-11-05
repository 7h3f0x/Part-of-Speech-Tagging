#!/usr/bin/python3

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


def main():

    global TAG_DICT
    TAG_DICT = generate_dict('tag')
    global WORD_TAG_DICT
    WORD_TAG_DICT = generate_dict('word_tag')
    global WORD_DICT
    WORD_DICT = generate_dict('word')


    word_input = input("Please enter your word\n").strip('\n')

    if not (WORD_DICT.get(word_input, None)):
        print(colored("Word not in dictionary", "red"))
        exit(1)

    for tag in TAG_DICT.keys():
        print(f'{word_input}_{tag}: {generate_probability(word_input, tag)}')


if __name__ == '__main__':
    main()
