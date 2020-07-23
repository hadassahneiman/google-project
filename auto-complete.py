import json
from string import ascii_letters, ascii_lowercase

queries = []
trie_list = {}


def load():
    global queries, trie_list
    print("loading data 1 2 3.....")
    files = {letter: 'trie_' + letter + '.json' for letter in ascii_lowercase}
    queries = json.load(open("queries.json"))
    for letter, file in files.items():
        trie_list[letter] = json.load(open(file))[0]


class AutoComplete:
    def __init__(self, completed_string, source_text, offset, score):
        self.completed_string = completed_string
        self.source_text = source_text
        self.offset = offset
        self.score = score


def simplify_query(query):
    query = ' '.join(query.split())
    query = [letter.lower() for letter in query if letter in ascii_letters + ' ']
    return query


def get_info(completions):
    return [AutoComplete(queries[completion[0]][0],
                         queries[completion[0]][1],
                         completion[1],
                         completion[2]) for completion in completions]


def find_substrings(query):
    cursor = trie_list[query[0]]
    found_queries = []

    for letter in query:
        if letter in cursor['dict']:
            cursor = cursor['dict'][letter]
        else:
            break
    else:
        found_queries = cursor['completions']

    result = get_info(found_queries)
    return result


def print_matches(matches, query):
    for i, match in enumerate(matches):
        offset = match.offset + len(match.completed_string[:match.offset]) - len(simplify_query(match.completed_string[:match.offset]))
        print(i + 1,
              match.completed_string[:offset] +
              f'\033[91m{match.completed_string[offset: offset + len(query)]}\033[00m' +
              match.completed_string[offset + len(query):],
              '(', match.source_text, ')', match.score)


def find_top_five(query):
    query = simplify_query(query)
    print(query)
    substrings = find_substrings(query)
    print_matches(substrings, query)


def get_input():
    string = input("Please enter a search: ")
    find_top_five(string[:8])
    while True:
        if string[-1] == '#':
            return
        str_ = input(string)
        string += str_
        find_top_five(string[:8])


def main():
    load()
    print("Click ctrl c to exit")
    while True:
        get_input()


if __name__ == '__main__':
    main()
