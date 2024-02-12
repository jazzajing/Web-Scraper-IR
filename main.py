import json
import math
from tkinter import *
from nltk.stem import WordNetLemmatizer
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from nltk.corpus import wordnet

lemmatizer = WordNetLemmatizer()

# global declarations for docids, lengths, postings, vocabulary
docids = []
doclength = {}
postings = {}
vocab = []
results_list = []
file_results = []
text_entry = ""
titles = {}
ner_headings = {}
ner_titles = {}


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


def read_index_files():
    # reads existing data from index files: docids, vocab, postings
    # uses JSON to preserve list/dictionary data structures
    # declare refs to global variables
    global docids
    global doclength
    global postings
    global vocab
    global titles
    global ner_titles
    global ner_headings
    # open the files
    in_d = open('docids2.txt', 'r')
    in_l = open('doclength2.txt', 'r')
    in_v = open('vocab2.txt', 'r')
    in_p = open('postings2.txt', 'r')
    in_t = open('titles.txt', 'r')
    in_nh = open('nerheads.txt', 'r')
    in_nt = open('nertitles.txt', 'r')
    # load the data
    docids = json.load(in_d)
    doclength = json.load(in_l)
    vocab = json.load(in_v)
    postings = json.load(in_p)
    titles = json.load(in_t)
    ner_titles = json.load(in_nt)
    ner_headings = json.load(in_nh)
    # close the files
    in_d.close()
    in_l.close()
    in_v.close()
    in_p.close()
    in_t.close()
    in_nt.close()
    in_nh.close()

    return


def main():
    read_index_files()

    for i, word in enumerate(vocab):
        vocab[i] = lemmatizer.lemmatize(word)

    guisearch()


def search_command(results):
    global results_list
    print(results)
    results_list.insert(0, results)


def add_to_file():
    global file_results

    text = "StudentNo:100263301\nSystem{weighted}\nQueryNo,Rank,URL\n"
    for i, query in enumerate(file_results):
        query_no = i
        for n, result in enumerate(query):
            rank = n
            text = text + str(query_no + 1) + ',' + str(rank + 1) + ',' + result + '\n'

    filename = 'IR_relevantdocs_OLDQUERIES.csv'
    file = open(filename, 'w')
    file.write(text)

    return "Written to file: " + filename


def guisearch():
    global results_list
    global text_entry

    window = Tk()
    window.title('Jared\'s Search Engine')

    heading = Label(window, text="Welcome to UEA People Search")
    heading.config(font=("Helvetica", 30))
    heading.grid(row=1, column=1, pady=2, sticky=NSEW)

    canvas = Canvas(window, width=300, height=150)
    canvas.grid(row=2, column=1, pady=2, sticky=NSEW)
    uea_logo = PhotoImage(file="uea-logo.gif")
    canvas.create_image(120, 20, anchor=NW, image=uea_logo)

    instructions = Label(window, text="Input your search terms below:")
    instructions.config(font=("Helvetica", 15))
    instructions.grid(row=3, column=1, pady=2, sticky=NSEW)

    text_entry = Entry(window, bd=5)
    text_entry.grid(row=4, column=1, pady=2, sticky=NSEW)

    search_button = Button(window, text="Search")
    search_button.config(command=lambda: query.config(text=retrieve_vector(text_entry.get())))
    search_button.grid(row=5, column=1, pady=2, sticky=NSEW)

    query = Label(window)
    query.grid(row=9, column=1, pady=2, sticky=NSEW)

    write_button = Button(window, text="Write to file")
    write_button.config(command=lambda: written.config(text=add_to_file()))
    write_button.grid(row=6, column=1, pady=2, sticky=NSEW)

    results_list = Listbox(window)
    results_list.grid(row=7, column=1, pady=2, sticky=NSEW)

    clear_button = Button(window, text="Clear", command=clear_text)
    clear_button.grid(row=8, column=1, pady=2, sticky=NSEW)

    quit_button = Button(window, text="QUIT", command=window.quit)
    quit_button.grid(row=9, column=1, pady=2, sticky=NSEW)

    query = Label(window)
    query.grid(row=10, column=1, pady=2, sticky=NSEW)

    written = Label(window)
    written.grid(row=11, column=1, pady=2, sticky=NSEW)

    window.grid_rowconfigure(0, weight=1)
    window.grid_rowconfigure(12, weight=1)
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(2, weight=1)

    window.mainloop()


def clear_text():
    global text_entry
    global results_list

    text_entry.delete(0, END)
    results_list.delete(0, END)


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


def retrieve_vector(query_terms):
    global docids  # list of doc names - the index is the docid (i.e. 0-4)
    global doclength  # number of terms in each document
    global vocab  # list of terms found (237) - the index is the termid
    global postings  # postings dictionary; the key is a termid
    global titles
    global ner_titles
    global ner_headings
    global results_list
    global file_results
    # the value is a list of postings entries,
    # each of which is a list containing a docid and frequency

    answer = []  # a ranked list of the relevant documents (URLs)
    idf = {}
    tf = {}
    tfidf = {}
    doc_scores = {}
    synonyms = []
    neshead_scores = {}
    nestitle_scores = {}

    nes = get_continuous_chunks(query_terms)

    count = 0
    for docid, title in ner_titles.items():
        for word in nes:
            if word in title:
                count += 1
        if count > 0:
            nestitle_scores[docid] = count
        count = 0

    for docid, score in sorted(nestitle_scores.items(), key=lambda x: x[1], reverse=True):
        answer.append(docid)

    nestitle_scores.clear()


    # for docid, heading in ner_headings.items():
    # for word in nes:
    # if word in title:
    # count += 1
    # if count > 0:
    # nestitle_scores[docid] = count
    # count = 0

    query_terms = query_terms.split()
    query_terms = [x.lower() for x in query_terms]
    for i, term in enumerate(query_terms):
        query_terms[i] = lemmatizer.lemmatize(term)

    for term in query_terms:
        for syn in wordnet.synsets(term):
            for lemma in syn.lemmas():
                if '_' or '-' in lemma.name():
                    continue
                else:
                    synonyms.append(str(lemma.name()))

    # remove duplicates from query - also removes order
    print('Query: ', query_terms)
    print('Named Entities: ', nes)
    syn_query_terms = set(query_terms + synonyms)
    syn_query_terms = [x.lower() for x in syn_query_terms]
    print('Syn Query: ', syn_query_terms)

    results_list.delete(0, END)

    # iterate over the query terms
    for term in syn_query_terms:
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
    # create merge_list in descending idf order
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

    docs = []
    for doc in result:
        doc = int(doc)
        docs.append(docids[doc])

    file_results.append(docs)

    i = 1
    for doc in docs:
        title = titles[str(docids.index(doc))]
        results_list.insert(END, str(i) + ') ' + title)
        results_list.insert(END, '  URL:  ' + doc)
        i += 1
    print(result)

    # your code ends here
    return "Query: " + str(query_terms)


# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
