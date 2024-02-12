import json
import string

from bs4 import BeautifulSoup

docids = []
doclength = {}
postings = {}
vocab = []
parsed_urls = []
titles = []
headings = []


def main():
    read_index_files()

    parser()

    write_index_files(0)


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


def parser():
    # for i, url in enumerate(docids):
    # parsed_url = BeautifulSoup(open('ueapeople/page' + str(i) + '.html'), features='lxml')
    # parsed_urls.append(parsed_url)

    for docid, url in enumerate(docids):
        parsed_url = BeautifulSoup(open('ueapeople/page' + str(docid) + '.html'), 'lxml')
        parsed_urls.append(parsed_url)

        for heading in parsed_url.find_all(["h1", "h2", "h3"], {"class": "title"}):
            head = heading.text
            head = head.replace("-", " ")
            head = head.translate(str.maketrans('', '', string.punctuation))
            head = head.translate(str.maketrans('', '', string.digits))
            head = head.replace("“", "")
            head = head.replace("’", "")
            head = head.replace("”", "")
            head = head.replace("‘", "")
            head = head.lower()
            headings.append(head)

            for word in head.split():
                docid = str(docid)
                if word in vocab:
                    wordid = str(vocab.index(word))
                    if docid in postings[wordid].keys():
                        frequency = postings[wordid][docid]
                        frequency = frequency*3
                        postings[wordid][docid] = frequency
                        print(word)
                else:
                    continue

        title = parsed_url.title.text.strip()
        title = title.replace("-", " ")
        title = title.lower()
        titles.append(title)
        for word in title.split():
            docid = str(docid)
            if word in vocab:
                wordid = str(vocab.index(word))
                if docid in postings[wordid].keys():
                    frequency = postings[wordid][docid]
                    frequency = frequency * 3
                    postings[wordid][docid] = frequency
                    print(word)
            else:
                continue

    return


# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
