import json
import string
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from bs4 import BeautifulSoup


docids = []
doclength = {}
postings = {}
vocab = []
parsed_urls = []
titles = {}
tempheads = []
headings = {}
ner_headings = {}
ner_titles = {}


def main():

    read_index_files()

    parser()

    write_index_files()


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


def write_index_files():
    # n can be 0,1
    # declare refs to global variables
    global headings
    global titles
    # decide which files to open
    # open files
    out_h = open('headings.txt', 'w')
    out_t = open('titles.txt', 'w')
    # write to index files: docids, vocab, postings
    # use JSON as it preserves the dictionary structure (read/write treat it as a string)
    json.dump(headings, out_h)
    json.dump(titles, out_t)
    # close files
    out_h.close()
    out_t.close()

    h = len(headings)
    t = len(titles)
    print('===============================================')
    print('Indexing: ', h, ' headings ', t, ' title written to file')
    print('===============================================')

    return


def parser():
    for docid, url in enumerate(docids):
        parsed_url = BeautifulSoup(open('ueapeople/page' + str(docid) + '.html'), 'lxml')
        parsed_urls.append(parsed_url)
        print('Done:Doc ', docid)

        for heading in parsed_url.find_all(["h1", "h2", "h3"], {"class": "title"}):
            tempheads.append(heading.text)

        headings[str(docid)] = tempheads.copy()
        tempheads.clear()

        title = parsed_url.title.text.strip()
        titles[str(docid)] = title

    return


def get_continuous_chunks(text):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
        if type(i) == Tree:
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        if current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue
    return continuous_chunk


def findentities():

    for docid, heads in headings.items():
        for head in heads:
            ner_head = get_continuous_chunks(head)
            ner_headings[str(docid)] = ner_head.copy()

    for docid, title in titles.items():
        ner_title = get_continuous_chunks(title)
        ner_titles[str(docid)] = ner_title.copy()

    #my_sent = "WASHINGTON -- In the wake of a string of abuses by New York police officers in the 1990s, Loretta E. Lynch, the top federal prosecutor in Brooklyn, spoke forcefully about the pain of a broken trust that African-Americans felt and said the responsibility for repairing generations of miscommunication and mistrust fell to law enforcement."
    #nersent = get_continuous_chunks(my_sent)
    #print(nersent)

    return


# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
