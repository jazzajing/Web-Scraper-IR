#!/usr/bin/python3

import sys
import re
import json

# global declarations for doclist, postings, vocabulary
docids = []
postings = {}
vocab = []


def main():
    # code for testing offline  
    if len(sys.argv) < 2:
        print('usage: ./retriever.py term [term ...]')
        sys.exit(1)
    query_terms = sys.argv[1:]
    answer = []

    read_index_files()

    answer = retrieve_bool(query_terms)

    print('Query: ', query_terms)
    i = 0
    for docid in answer:
        i += 1
        print(i, docids[int(docid)])


def read_index_files():
    ## reads existing data from index files: docids, vocab, postings
    # uses JSON to preserve list/dictionary data structures
    # declare refs to global variables
    global docids
    global postings
    global vocab
    # open the files
    in_d = open('docids2.txt', 'r')
    in_v = open('vocab2.txt', 'r')
    in_p = open('postings2.txt', 'r')
    # load the data
    docids = json.load(in_d)
    vocab = json.load(in_v)
    postings = json.load(in_p)
    # close the files
    in_d.close()
    in_v.close()
    in_p.close()

    return


def retrieve_bool(query_terms):
    ## a function to perform Boolean retrieval with ANDed terms
    answer = []

    #### your code starts here ####
    matches = []  # List of docids of matches
    unique_terms = [] # List of lists of ANDed terms
    exclusions = []  # List of words excluded from search
    notincorpus = []  # List of words not in vocab
    tmpmatches = []
    tmp = []

    [x.lower() for x in query_terms]

    if 'AND' in query_terms:
        query_terms.remove('AND')

    if 'NOT' in query_terms:
        target = query_terms.index('NOT')
        query_terms = query_terms[:target]

    for word in query_terms:
        if word != 'OR':
            tmp.append(word)
        else:
            unique_terms.append(tmp)
            tmp = []

    unique_terms.append(tmp)
    print(unique_terms)

    for i, group in enumerate(unique_terms):
        s = list(set(group))
        unique_terms[i] = s

    for group in unique_terms:
        for term in group:
            if term in vocab:
                termid = str(vocab.index(term))
                tmpmatches = tmpmatches + list(postings[termid].keys())
            else:
                notincorpus.append(term)
        matches.append(tmpmatches)

    for i, group in enumerate(matches):
        if len(unique_terms[i]) == 1:
            answer.append(matches[i])
        # Only adds to answer if all terms appear in same doc
        else:
            for doc in group:
                if group.count(doc) == len(unique_terms[i]):
                    answer.append(doc)

    flattened_answer = [item for items in answer for item in items]
    answer = set(flattened_answer)

    if notincorpus:
        print(notincorpus, ': word(s) from query not present in corpus.')

    if exclusions:
        print(exclusions, ': common word(s) excluded from search')

    if answer == set():
        print('No results found.')

    #### your code ends here ####
    return answer


    # Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
