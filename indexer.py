#!/usr/bin/python3  indexer.py -d ./LookingGlass 5

import sys
import os
import re
import json
import string
import math

# global declarations for docids, lengths, postings, vocabulary
docids = []
doclength = {}
postings = {}
vocab = []


def main():
    # code only for testing offline only - not used for a crawl
    max_files = 64000
    if len(sys.argv) == 1:
        print('usage: ./indexer.py file | -d directory [maxfiles]')
        sys.exit(1)
    elif len(sys.argv) == 2:
        filename = sys.argv[1]
    elif len(sys.argv) == 3:
        if re.match('-d', sys.argv[1]):
            dirname = sys.argv[2]
            dir_index = True
        else:
            print('usage: ./indexer.py file | -d directory [maxfiles]')
            sys.exit(1)
    elif len(sys.argv) == 4:
        if re.match('\d+', sys.argv[3]):
            max_files = int(sys.argv[3])
        else:
            print('usage: ./indexer.py file | -d directory [maxfiles]')
            sys.exit(1)
    else:
        print('usage: ./indexer.py file | -d directory [maxfiles]')

    if len(sys.argv) == 2:
        index_file(filename)
    elif re.match('-d', sys.argv[1]):
        for filename in os.listdir(sys.argv[2]):
            if re.match('^_', filename):
                continue
            if max_files > 0:
                max_files -= 1
                filename = sys.argv[2] + '/' + filename
                index_file(filename)
            else:
                break

    write_index_files(1)


def index_file(filename):  # code only for testing offline only - not used for a crawl
    try:
        input_file = open(filename, 'rb')
    except (IOError) as ex:
        print('Cannot open ', filename, '\n Error: ', ex)
    else:
        page_contents = input_file.read()  # read the input file
        url = 'http://www.' + filename + '/'
        # print (url, page_contents)
        make_index(url, page_contents)
        input_file.close()


def write_index_files(n):
    # n can be 0,1
    # declare refs to global variables
    global docids
    global postings
    global vocab
    global doclength
    # decide which files to open
    # there are 2 sets, written to on alternate calls
    nn = n + 1
    # open files
    out_d = open('docids' + str(nn) + '.txt', 'w')
    out_l = open('doclength' + str(nn) + '.txt', 'w')
    out_v = open('vocab' + str(nn) + '.txt', 'w')
    out_p = open('postings' + str(nn) + '.txt', 'w')
    # write to index files: docids, vocab, postings
    # use JSON as it preserves the dictionary structure (read/write treat it as a string)
    json.dump(docids, out_d)
    json.dump(doclength, out_l)
    json.dump(vocab, out_v)
    json.dump(postings, out_p)
    # close files
    out_d.close()
    out_l.close()
    out_v.close()
    out_p.close()

    d = len(docids)
    v = len(vocab)
    p = len(postings)
    print('===============================================')
    print('Indexing: ', d, ' docs ', v, ' terms ', p, ' postings lists written to file')
    print('===============================================')

    return


def read_index_files():
    # declare refs to global variables
    global docids
    global postings
    global vocab
    global doclength
    nn = 1

    # reads existing data into index files: docids, lengths, vocab, postings
    in_d = open('docids' + str(nn) + '.txt', 'r')
    in_l = open('doclength' + str(nn) + '.txt', 'r')
    in_v = open('vocab.txt' + str(nn) + '', 'r')
    in_p = open('postings' + str(nn) + '.txt', 'r')

    docids = json.load(in_d)
    doclength = json.load(in_l)
    vocab = json.load(in_v)
    postings = json.load(in_p)

    in_d.close()
    in_l.close()
    in_v.close()
    in_p.close()

    return


def clean_html(html):
    head = re.compile('\<head[\s\S]*?\/head\>', re.S)  # remove head section of html
    scripts = re.compile('<script.*?script>', re.S)  # remove all script tags from the html
    css = re.compile('<style.*?style>', re.S)  # remove all style tags from the html
    links = re.compile('<link.*?link>|<link.*?>', re.S)  # remove all links from the html
    tags = re.compile('<.*?>', re.S)  # remove any remaining tags from the html
    js = re.compile('{.*?}', re.S)  # remove js from the html
    comments = re.compile('<--|-->', re.S)  # remove all comments from html
    angles = re.compile('<|>', re.S)  # remove remaining angle brackets from the html
    entities = re.compile('&(.*?)\;', re.S)  # remove html entities
    hexvals = re.compile('\\\\x..', re.S)  # remove hex values in html
    slash = re.compile('\\\\\'', re.S)  # remove stray backslashes in html
    unicode = re.compile(r'[^\x00-\x7F]', re.S)  # remove unicode characters
    spaces = re.compile(r'\s +', re.S)  # remove all whitespace except for spaces
    whitespace = re.compile(r"^\s+", re.MULTILINE)  # remove all whitespace except for spaces

    cleaned = head.sub(r'', html)
    cleaned = scripts.sub(r'', cleaned)
    cleaned = css.sub(r'', cleaned)
    cleaned = links.sub(r'', cleaned)
    cleaned = tags.sub(r'', cleaned)
    cleaned = js.sub(r'', cleaned)
    cleaned = comments.sub(r'', cleaned)
    cleaned = angles.sub(r'', cleaned)
    cleaned = entities.sub(r'', cleaned)
    cleaned = hexvals.sub(r'', cleaned)
    cleaned = slash.sub(r'', cleaned)
    cleaned = unicode.sub(r'', cleaned)
    cleaned = spaces.sub(r' ', cleaned)
    cleaned = whitespace.sub(r'', cleaned)

    return cleaned.strip()


def make_index(url, page_contents):
    # declare refs to global variables
    global docids  # contains URLs + docids
    global postings  # contains termids + docids, frequencies
    global vocab  # contains words + termids
    global doclength  # contains docids + lengths

    print('make_index: url = ', url)

    # if re.search('https:..', url):  # match and remove https://
    #     stripped_url = re.sub('https://', '', url)
    # elif re.search('http:..', url):  # match and remove http://
    #     stripped_url = re.sub('http://', '', url)
    # else:
    #     print("make_index no match for protocol url=", url)
    #
    # if re.search('www.', stripped_url):  # match and remove www.
    #     stripped_url = re.sub('www.', '', stripped_url)


        ### append the url to the list of documents
    if url in docids:  # return if we've seen this before
        return
    else:
        docids.append(url)  # add url to docids table
        docid = str(docids.index(url))  # get a string version of the docid

    #### extract the words from the page contents ####
    if (isinstance(page_contents, bytes)):  # convert bytes to string if necessary
        page_contents = page_contents.decode('utf-8', 'ignore')  # ignore code errors...

    #### page_text is the initial content, transformed to words ####
    page_text = clean_html(page_contents)

    page_text = page_text.translate(str.maketrans('', '', string.punctuation))
    page_text = page_text.lower()
    #print('make_index1: page_text = ', page_text)  # for testing
    words = page_text.split()
    ###################################################

    docfreq = {}
    lengths = 0

    # add the vocab counts and postings
    for word in words:
        lengths += 1  # word count for document
        # is the word in the vocabulary
        if word in vocab:
            termid = str(vocab.index(word))
        else:
            vocab.append(word)
            termid = str(vocab.index(word))
            # keep the counts of words in docfreq
        if (termid in docfreq):
            docfreq[termid] += 1
        else:
            docfreq[termid] = 1

    doclength[docid] = lengths

    # postings now stored in nested dictionary
    for termid in docfreq:
        if termid not in postings:
            postings[termid] = {}  # initialising inner dictionary to stop KeyError
            postings[termid][docid] = docfreq[termid]
        else:
            postings[termid][docid] = docfreq[termid]

    ##### save the index after every 100 documents ####
    if len(doclength) % 100 == 0:  #
        n = int(len(doclength) / 100) % 2
        write_index_files(n)

    return


# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
