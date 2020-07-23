import json
from string import ascii_lowercase
from os import walk, path

query_id = 0
queries = []
files = {letter: 'trie_' + letter + '.json' for letter in ascii_lowercase + ' '}
dicts = {letter: [{'completions': [], 'dict': {}}] for letter in ascii_lowercase + ' '}


def simplify_query(query):
    query = ' '.join(query.split())
    query = [letter.lower() for letter in query if letter.isalpha() or letter == ' ']
    return query


def add_completion(cursor, dic):
    for completion in cursor['completions']:
        if dic[0] == completion[0]:
            if dic[2] > completion[2]:
                completion[1] = dic[1]
                completion[2] = dic[2]
            break

    else:
        cursor['completions'].append(dic)
        cursor['completions'] = sorted(cursor['completions'], key=lambda x: x[2], reverse=True)[:5]


def add_query_to_trie(query, _id, offset, minus_score):
    if not query:
        return

    cursor = dicts[query[0]][0]

    for index, letter in enumerate(query):
        add_completion(cursor, [_id, offset, 2 * index - minus_score])
        if letter not in cursor['dict']:
            cursor['dict'][letter] = {'completions': [], 'dict': {}}
        cursor = cursor['dict'][letter]

    add_completion(cursor, [_id, offset, 2*len(query) - minus_score])


def manipulate_by_switching(query, index, letter, offset):
    score_to_minus = 7 - index if index < 4 else 3
    add_query_to_trie(query[:index] + [letter] + query[index + 1:], query_id, offset, score_to_minus)


def manipulate_by_erasing(query, index, letter, offset):
    score_to_minus = 12 - 2 * index if index < 4 else 4
    add_query_to_trie(query[:index] + [letter] + query[index:], query_id, offset, score_to_minus)


def manipulate_by_adding(query, index, offset):
    score_to_minus = 10 - 2*index if index < 4 else 2
    add_query_to_trie(query[:index] + query[index + 1:], query_id, offset, score_to_minus)


def add_with_manipulations(query, offset):
    for j in range(len(query)):
        manipulate_by_adding(query, j, offset)

        for letter in ascii_lowercase + ' ':
            manipulate_by_switching(query, j, letter, offset)
            manipulate_by_erasing(query, j, letter,  offset)


def add_query(query, file):
    global query_id, queries

    if not query:
        return

    queries.append([query, file])
    query = simplify_query(query)

    for i in range(len(query) - 8):
        add_query_to_trie(query[i:i + 8], query_id, i, 0)
        add_with_manipulations(query[i:i + 8], i)

    query_id += 1


def get_files():
    file_names = []
    for (dirpath, dirname, filename) in walk('technology_texts'):
        file_names += [path.join(dirpath, file) for file in filename]
    return file_names


def read_files_into_trie(file_names):
    for file in file_names:
        _queries = open(file).read().split('\n')
        print(file)
        for query in _queries:
            if query != ' ':
                add_query(query, file)


def init_trie():
    file_names = get_files()
    read_files_into_trie(file_names)

    with open('queries.json', 'w') as queries_file:
        json.dump(queries, queries_file)

    for letter in files:
        with open(files[letter], "w") as trie_file:
            json.dump(dicts[letter], trie_file)


if __name__ == '__main__':
    init_trie()
