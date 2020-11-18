import nltk
from nltk.corpus import wordnet
from nltk.tree import ParentedTree
from nltk.stem import WordNetLemmatizer

grammar = r"""
  NP: {<DT|PP\$>?<JJ.*>*<NN.*>+}    # Chunk sequences of DT, JJ, NN
  PP: {<IN><NP>}                    # Chunk prepositions followed by NP
  VP: {<VB.*><NP|PP|CLAUSE>+$}      # Chunk verbs and their arguments
  CLAUSE: {<NP><VP>}                # Chunk NP, VP
  """
# grammar = r"""
#   NP: {<DT|PP\$>?<JJ.*>*<NN.*>+}  # Chunk sequences of DT, JJ, NN
#   PP: {<IN><NP>}                  # Chunk prepositions followed by NP
#   VP: {<VB.*><NP|PP>$}            # Chunk verbs and their arguments
#   """

def preprocess(document):
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

def get_pos(tag):
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('N'):
            return wordnet.NOUN
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

def extract_relations(sentences):
    sentences = preprocess(sentences)
    lemmatizer = WordNetLemmatizer()
    stop_words = set(nltk.corpus.stopwords.words("english"))

    exp = {}
    verb = ''
    adverb = ''
    to = 0
    for sentence in sentences:
        cp = nltk.RegexpParser(grammar)
        result = cp.parse(sentence)
        for index, n in enumerate(result):
            if str(n[-1]).startswith("VB"):
                if verb == '':
                    verb = n[0]
            elif n[-1] == 'WRB':
                if adverb == '':
                    adverb = n[0]
            elif n[-1] == 'TO':
                to = 1
            if isinstance(n, nltk.tree.Tree):
                newn = ParentedTree.convert(n)
                if n.label() == 'PP':
                    req = ''
                    for leaf in n.leaves():
                        req += lemmatizer.lemmatize(leaf[0], pos=get_pos(leaf[1])) + ' '
                    
                    words = req.split(' ')[1:]
                    exp[(' '.join([w for w in words if w not in stop_words])).strip()] = ['PP', req.split(' ')[0]]
                    # exp[' '.join(req.split(' ')[1:])] = ['PP', req.split(' ')[0]]

                elif n.label() == 'NP' and newn.parent() != 'PP':
                    req = ''
                    for leaf in n.leaves():
                        req += lemmatizer.lemmatize(leaf[0], pos=get_pos(leaf[1])) + ' '
                        
                    words = req.split(' ')
                    if verb != '':
                        if to == 1:
                            exp[(' '.join([w for w in words if w not in stop_words])).strip()] = ['NP', verb + '_to']
                            # exp[req] = ['NP', verb + '_to']
                            verb = ''
                            if adverb != '':
                                adverb = ''
                        elif adverb != '':
                            exp[(' '.join([w for w in words if w not in stop_words])).strip()] = ['NP', verb + '_' + adverb]
                            # exp[req] = ['NP', verb + '_' + adverb]
                            verb = ''
                            adverb = ''
                        else:
                            exp[(' '.join([w for w in words if w not in stop_words])).strip()] = ['NP', verb]
                            # exp[req] = ['NP', verb]
                            verb = ''
                    else:
                        exp[(' '.join([w for w in words if w not in stop_words])).strip()] = ['NP', 'is']
                        # exp[req] = ['NP', 'is']

                elif n.label() == 'VP':
                    req = ''
                    for leaf in n.leaves():
                        req += lemmatizer.lemmatize(leaf[0], pos=get_pos(leaf[1])) + ' '

                    if verb != '':                                      # can be extended like above for NP.
                        words = req.split(' ')
                        exp[(' '.join([w for w in words if w not in stop_words])).strip()] = ['VP', verb]
                    else:
                        words = req.split(' ')[1:]
                        exp[(' '.join([w for w in words if w not in stop_words])).strip()] = ['VP', req.split(' ')[0]]

    return exp