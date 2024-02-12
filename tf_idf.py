#!/usr/bin/python3
# 
import sys
import math
import json

# The queries for the project are:
#
# Emma Sutton
# North Sea fish
# European Union climate policy
# anime culture
# food technology
# smoking food
# internet privacy rights
# Gold Coast
# virus testing
# General Data Protection Regulation

# global declarations for docids, lengths, postings, vocabulary
docids = []
doclength = {}
postings = {}
vocab = []


def read_index_files():
    # reads existing data from index files: docids, vocab, postings
    # uses JSON to preserve list/dictionary data structures
    # declare refs to global variables
    global docids
    global doclength
    global postings
    global vocab
    # open the files
    in_d = open('docids2.txt', 'r')
    in_l = open('doclength2.txt', 'r')
    in_v = open('vocab2.txt', 'r')
    in_p = open('postings2.txt', 'r')
    # load the data
    docids = json.load(in_d)
    doclength = json.load(in_l)
    vocab = json.load(in_v)
    postings = json.load(in_p)
    # close the files
    in_d.close()
    in_l.close()
    in_v.close()
    in_p.close()

    return


def main():
    # code for testing offline
    if len(sys.argv) < 2:
        print('usage: ./retriever.py term [term ...]')
        sys.exit(1)
    query_terms = sys.argv[1:]

    read_index_files()

    retrieve_vector(query_terms)


def retrieve_vector(query_terms):

    global docids  # list of doc names - the index is the docid (i.e. 0-4)
    global doclength  # number of terms in each document
    global vocab  # list of terms found (237) - the index is the termid
    global postings  # postings dictionary; the key is a termid
    # the value is a list of postings entries,
    # each of which is a list containing a docid and frequency

    answer = []  # a ranked list of the relevant documents (URLs)
    idf = {}
    tf = {}
    tfidf = {}
    doc_scores = {}
    #### your code starts here ####
    query_terms = [x.lower() for x in query_terms]
    # remove duplicates from query - also removes order
    print('Query: ', query_terms)
    query_terms = set(query_terms)

    ## iterate over the query terms
    for term in query_terms:
        # is the term in the vocab?
        if term in vocab:
            wordid = str(vocab.index(term))
            noofdocs = len(doclength)
            noofrelevant = len(postings[wordid])
            # if so, calculate idf for that term
            term_idf = math.log(noofdocs / noofrelevant)
            idf[wordid] = term_idf
        # len(doclength) gives N, the number of docs in collection
        # the length of the postings list for a term gives the number of documents containing the term
        else:
            break

    for wordid in idf:
        tf[wordid] = {}
        for doc in postings[wordid]:
            freq = postings[wordid][doc]
            wordsindoc = doclength[doc]
            tf_value = (freq / wordsindoc)
            tf[wordid][doc] = tf_value

    for wordid in tf:
        tfidf[wordid] = {}
        doc_tf_pair = tf[wordid]
        for doc in doc_tf_pair:
            tfidf_value = doc_tf_pair[doc] * idf[wordid]
            tfidf[wordid][doc] = tfidf_value

    for wordid in tfidf:
        doc_idf_pair = tfidf[wordid]
        for doc in doc_idf_pair:
            if doc not in doc_scores:
                doc_scores[doc] = []
                doc_scores[doc].append(doc_idf_pair[doc])
            else:
                doc_scores[doc].append(doc_idf_pair[doc])

    for doc in doc_scores:
        doc_scores[doc] = sum(doc_scores[doc])

    for doc in sorted(doc_scores, key=doc_scores.get, reverse=True):
        answer.append(doc)

    result = answer[:10]
    print(result)


    #### your code ends here ####
    return answer


# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
