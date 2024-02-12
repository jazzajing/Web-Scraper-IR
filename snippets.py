import json
import string

from bs4 import BeautifulSoup

docids = []
doclength = {}
postings = {}
vocab = []
parsed_urls = []


def main():
    read_index_files()

    snip()


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


def snip():
    # for i, url in enumerate(docids):
    # parsed_url = BeautifulSoup(open('ueapeople/page' + str(i) + '.html'), features='lxml')
    # parsed_urls.append(parsed_url)

    for docid, url in enumerate(docids):
        parsed_url = BeautifulSoup(open('ueapeople/page' + str(docid) + '.html'), 'lxml')
        parsed_urls.append(parsed_url)
        print('Doc: ', docid)

    for url in parsed_urls:
        content = url.find_all("p", limit=1)
        content = content.text
        print(content)

    return


# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
