from nltk.corpus import stopwords
from neo4j import GraphDatabase
from dotenv import load_dotenv
import ast
import os

load_dotenv()
stop_words = set(stopwords.words("english"))

def env(key, default=None, required=True):
    try:
        value = os.getenv(key)
        # return ast.literal_eval(value)
        return value
    except (SyntaxError, ValueError):
        return value
    except KeyError:
        if default or not required:
            return default
        raise RuntimeError("Missing required environment variable '%s'" % key)


# def retrieve_results(driver, methods, nouns, verbs):
#     methods = [method[0] for method in methods]
#     query = "MATCH (a:Code)-[r:Calls]->(b:JavaMethod) WHERE b.name IN " + str(methods) + " RETURN a.uri LIMIT 50"

#     with driver.session() as session:
#         records = session.run(query).data()
#         records = [record['a.uri'] for record in records]

#         for string in nouns:
#             query = "MATCH (a:Code)-[r]->(b:Description) WHERE b.name CONTAINS '" + string + "' AND a.uri IN " + str(records) + " RETURN a.uri LIMIT 25"
#             records = session.run(query).data()

#     return records

def retrieve_results(driver, query):
    query = query.strip().split(' ')
    query = [word for word in query if word!="" and (word not in stop_words)]
    # Filter by description
    cypher1 = "MATCH (a:Code)-[r]->(d:Description) WHERE d.name IN " + str(query) + " RETURN a.uri, COUNT(r) AS C ORDER BY C DESC"
    # Filter by function name
    cypher2 = "MATCH (a:Code) WHERE ANY(item IN " + str(query) + " WHERE a.name CONTAINS item) RETURN a.name, a.uri"
    with driver.session() as session:
        records1 = session.run(cypher1).data()
        records2 = session.run(cypher2).data()
        # print("records1\n", records1)
        # print("records2\n", records2)
        
        for record in records2:
            count = 0
            for word in query:
                if word in record['a.name']:
                    count += 1
            del record['a.name']        ## Remember this while processing further.
            record['C'] = count*10
        
        # WEights????
        newlist = records1 + records2
        # print("newlist\n", newlist)
        newlist = sorted(newlist, key=lambda k: k['C'], reverse=True)
        # print("newlist\n", newlist)
        return newlist