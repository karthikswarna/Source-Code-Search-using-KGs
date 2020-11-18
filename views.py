from flask import Flask, render_template, request
from neo4j import GraphDatabase, basic_auth
from KGconstruction.extract_relations import preprocess
from gensim.test.utils import get_tmpfile
from gensim.models import FastText
import itertools
from models import *

app = Flask(__name__)

DATABASE_USERNAME = env('DATABASE_USERNAME')
DATABASE_PASSWORD = env('DATABASE_PASSWORD')
DATABASE_URL = env('DATABASE_URL')
DEBUG = env('DEBUG')
TESTING = env('TESTING')
DEVELOPMENT = env('DEVELOPMENT')
CSRF_ENABLED = env('CSRF_ENABLED')
app.config['SECRET_KEY'] = env('SECRET_KEY')

driver = GraphDatabase.driver(DATABASE_URL, auth=basic_auth(DATABASE_USERNAME, str(DATABASE_PASSWORD)))


@app.route('/')
def hello():
    return render_template("main.html")

@app.route('/search', methods=['POST'])
def get_query():
    query = request.form["query"]
    
    # # Preprocess the query and get nouns and verbs.
    # pos_sentences = preprocess(query)
    # pos_sentences = [word for sentence in pos_sentences for word in sentence]
    # verbs = list(filter(lambda word: word[1].startswith("VB"), pos_sentences))
    # nouns = list(filter(lambda word: word[1].startswith("NN"), pos_sentences))
    # nouns = [noun[0] for noun in nouns]
    # verbs = [verb[0] for verb in verbs]

    # if len(nouns) != 0 and len(verbs) != 0:
    #     arr1 = nouns
    #     arr2 = verbs
    # elif len(nouns) == 0 and len(verbs) != 0:
    #     arr1 = verbs
    #     arr2 = verbs
    # elif len(nouns) != 0 and len(verbs) == 0:
    #     arr1 = nouns
    #     arr2 = nouns
    # else:
    #     return render_template("main.html", codes=[])
        
    # # Create combinations of nouns and verbs
    # search_words = []
    # for element in itertools.product(*[arr1, arr2]):
    #     search_words.append(element)

    # Use fasttext and get method names which are similar to the noun-verb combinations in the query.
    # similar_methods = []        # List of lists of similar methods
    # model = FastText.load('fasttext.model')
    # for word in search_words:
    #     # similar = model.wv.similar_by_word(noun[0], topn=10)
    #     similar = model.wv.most_similar(positive=[word[0][0], word[1][0]], topn=10)
    #     similar_methods.append(similar)
    
    # Flattening the similar_methods list, and ordering the methods in the order of the importance(all most similar methods are placed at first)
    # methods_list = []
    # max_length = max([len(method_list) for method_list in similar_methods])
    # for i in range(max_length):
    #     for method_list in similar_methods:
    #         if i < len(method_list):
    #             methods_list.append(method_list[i])

    # codes = retrieve_results(driver, methods_list, nouns, verbs)
    codes = retrieve_results(driver, query)

    return render_template('main.html', codes=codes)

if __name__ == '__main__':
    app.run(debug=DEBUG)