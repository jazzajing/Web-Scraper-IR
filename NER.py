import json
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

docids = []
doclength = {}
postings = {}
vocab = []
titles = {}
headings = {}
tempheads = []
ner_headings = {}
ner_titles = {}


def main():

    read_index_files()

    findentities()

    write_index_files()


def read_index_files():
    # reads existing data from index files: docids, vocab, postings
    # uses JSON to preserve list/dictionary data structures
    # declare refs to global variables
    global docids
    global doclength
    global postings
    global vocab
    global titles
    global headings
    # open the files
    in_d = open('docids2.txt', 'r')
    in_l = open('doclength2.txt', 'r')
    in_v = open('vocab2.txt', 'r')
    in_p = open('postings2.txt', 'r')
    in_h = open('headings.txt', 'r')
    in_t = open('titles.txt', 'r')
    # load the data
    docids = json.load(in_d)
    doclength = json.load(in_l)
    vocab = json.load(in_v)
    postings = json.load(in_p)
    titles = json.load(in_t)
    headings = json.load(in_h)
    # close the files
    in_d.close()
    in_l.close()
    in_v.close()
    in_p.close()
    in_h.close()
    in_t.close()

    return


def write_index_files():
    # n can be 0,1
    # declare refs to global variables
    global ner_headings
    global ner_titles
    # decide which files to open
    # open files
    out_nh = open('nerheads.txt', 'w')
    out_nt = open('nertitles.txt', 'w')
    # write to index files: docids, vocab, postings
    # use JSON as it preserves the dictionary structure (read/write treat it as a string)
    json.dump(ner_headings, out_nh)
    json.dump(ner_titles, out_nt)
    # close files
    out_nh.close()
    out_nt.close()

    nh = len(ner_headings)
    nt = len(ner_titles)
    print('===============================================')
    print('Indexing: ', nh, ' headings ', nt, ' title written to file')
    print('===============================================')

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

    for docid, title in titles.items():
        ner_titles[docid] = get_continuous_chunks(title).copy()
        print('Doc Title: ', docid)

    for docid, heading in headings.items():
        for head in heading:
            ner_head = get_continuous_chunks(head)
            tempheads.append(ner_head)
        ner_headings[docid] = tempheads.copy()
        tempheads.clear()
        print('Doc Headings: ', docid)


# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
