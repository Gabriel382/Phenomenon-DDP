from nltk.corpus import wordnet

def termEnrichment(term):
    term.term_synonyms = []
    term.term_antonyms = []
    term.term_hypernyms = []
    term.term_hyponyms = []
   
    term_synset = wordnet.synsets(term.term_name)
    for syn in term_synset:
        for l in syn.lemmas():
            term.term_synonyms.append(l.name().replace('_',' '))
            # Antonyms
            if l.antonyms():
                term.term_antonyms.append(l.antonyms()[0].name().replace('_',' '))

    term.term_synonyms = list(set(term.term_synonyms))
    term.term_antonyms = list(set(term.term_antonyms))
    if len(term_synset) > 0:
        term.term_hypernyms = list(set([i.lemmas()[0].name().replace('_',' ') for i in term_synset[0].closure(lambda s:s.hypernyms())]))
        term.term_hyponyms = list(set([i.lemmas()[0].name().replace('_',' ') for i in term_synset[0].closure(lambda s:s.hyponyms())]))
    return term