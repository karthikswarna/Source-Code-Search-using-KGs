from extract_relations import extract_relations
from nltk.corpus import stopwords
from neo4j import GraphDatabase
import json
import re
import os


'''
TYPES of ARTIFACTS to be used (Spell Strictly):
1) Method
2) Comment
3) String
'''
# TODO:
# Migrate to javalang parser?
# May be merge "method" and "javamethod"?
# ***connetions to multiple nodes with same type.
# ***remove stop words and lemmatize the words.

# Both comments and string literals are nodes of type "Description". But the relations which connect them to the code nodes are has_comment, has_string.
# These relations can be used to identify them as comment/string nodes.

stop_words = set(stopwords.words("english"))

def update_kg(session, code, code_lines, code_name, docstring, uri):
    # create_code_nodes(session, code_name, docstring, uri)
    
    comments = retrieve_comments(code, code_lines)
    strings = retrieve_strings(code)
    methods = retrieve_methods(code)
    methods = methods[1:]       # First one is name of the main function.
    print("comments\n", comments)
    print("strings\n", strings)
    # new_methods = create_artifact_nodes(session, strings, "StringLiteral")
    # new_methods = create_artifact_nodes(session, comments, "Comment")
    # new_methods = create_artifact_nodes(session, methods, "Method")

    # edges = []
    # for method in methods:
    #     edges.append([uri, "Code", method, "Method", "Calls"])
    # for comment in comments:
    #     edges.append([uri, "Code", comment, "Comment", "has_comment"])
    # for string in strings:
    #     edges.append([uri, "Code", string, "StringLiteral", "has_string"])

    # create_relations(session, edges)

    # return [len(methods), new_methods]

# returns a list of method names used in the code.
def retrieve_methods(test_func):
    method_calls = []
    cur_word = ''
    test_func = re.sub(' +', ' ', test_func)

    for i in range(len(test_func)-1):
        cur_let = test_func[i]
        nxt_let = test_func[i+1]
    #     print(cur_let, nxt_let)
    #     print(test_func[i])

        if (cur_let!=" " and cur_let.isalpha() or cur_let == "."):
            cur_word += cur_let
        elif cur_let==" ":
            cur_word = ""
        if nxt_let == "(":
            if len(cur_word) > 1:
                method_calls.append(cur_word)
            cur_word = ""


    new_method_calls = []
    for j in method_calls:
        if "." in j:
            new_temp = j.split('.')
            for word in new_temp:
                if word != "":
                    # temp = camel_case_split(word)
                    # for k in temp:
                        # new_method_calls.append(k)
                    new_method_calls.append(word)
        else:
            # temp = camel_case_split(j)
            # for k in temp:
            #     new_method_calls.append(k)
            new_method_calls.append(j)

    return new_method_calls

def retrieve_strings(test_func):
    comms = re.findall('"(.*?)"', test_func)
    final_list = []
    for tent in comms:
        tent = strip(tent).split(' ')
        for ww in tent:
                if ww != "" and (ww not in stop_words):
                    # temp = camel_case_split(ww)
                    # for k in temp:
                    #     final_list.append(k)
                    final_list.append(ww)

    return final_list

def retrieve_comments(code, code_lines):
    # comms = re.findall('/\[(.*?)\]/', test_func)
    pattern = re.compile('(?:/\*(.*?)\*/)|(?://(.*?)\n)', re.S)
    comments = pattern.findall(code)

    final_list = []
    for line in code_lines:
        if '//' in line:
            tent = strip(line).split(' ')
            for ww in tent:
                if ww != "" and (ww not in stop_words):
                    # temp = camel_case_split(ww)                     
                    # for k in temp:
                    #     final_list.append(k)
                    final_list.append(ww)
    return final_list

def camel_case_split(string):
    
    string = strip(string)
    words = [[string[0]]] 
    for c in string[1:]: 
        if words[-1][-1].islower() and c.isupper(): 
            words.append(list(c)) 
        else: 
            words[-1].append(c) 
    
    new_ar = []
    for word in words:
        word = [i for i in word if i != ' ']
        new_ar.append(''.join(word).lower())
    
    return new_ar

def CamelCase_tokens(lis):


    new_list = []
    for i in lis:
        
        encoded_string = i.encode("ascii", "ignore")
        temp = encoded_string.decode()
        temp = re.split(',| |_|/|-|\\s+', temp)
        
        for j in temp:
            if j != "":
                try:
                    new_list.extend(camel_case_split(j))
                    
                except:
                    pass

    new_list = [i.lower().strip() for i in new_list if i not in stop_elements and len(i.lower().strip()) > 1]
    return new_list

def strip(string):

    string =  string.replace(',', ' ').replace('_', ' ').replace('!', ' ').replace('\"', ' ').replace('.', ' ').replace('\'', ' ').replace('@', ' ')\
            .replace('>', ' ').replace('?', ' ').replace('<', ' ').replace('=',' ').replace('+',' ')\
            .replace('-', ' ').replace('(', ' ').replace('/', ' ').replace(')', ' ')\
            .replace('*', ' ').replace('\\', ' ').replace('%', ' ').replace(';', ' ')\
            .replace(':', ' ').replace(']', ' ').replace('[', ' ').replace('}', ' ').replace('{', ' ')\
            .replace('\n', ' ').replace('\t', ' ').replace('#', ' ').replace('.', ' ')
    

    pattern = '[0-9]'
    return re.sub(pattern, '', string)

def create_edges(entity_index, _type, lis_items):
    edges = []

    count_dict = CountFrequency(lis_items)

    for i in count_dict.keys():
        temp = (entity_index, i ,_type, count_dict[i])
        edges.append(temp)
    
    return edges

def CountFrequency(_list):       
   count = {} 
   for i in _list: 
    count[i] = count.get(i, 0) + 1
   return count 




def create_database(session):
    pass

def delete_database(session):
    session.run("MATCH (n) DETACH DELETE n")


# INPUT: session, code_name, uri of the code snippet
# If the code with given URI doesn't exist already, adds it into DB as a "Code" node.
def create_code_nodes(session, code_name, docstring, uri):
    # records = session.run("MATCH (n:Code) WHERE (n.uri = $uri) RETURN (n)", uri=uri).data()
    # if len(records) == 0:
    #     session.run("CREATE (n:Code {name: $name, uri: $uri})", name=code_name, uri=uri)
    session.run("MERGE (n:Code {name: $name, uri: $uri})", name=code_name, uri=uri)
    ## DOCSTRING AS DESCRIPTION
    # relations = extract_relations(docstring)
    # for entity, relation in relations.items():
    #     session.run("MATCH (c: Code) WHERE c.name = $cname MERGE (d: Description {name: $dname}) CREATE (c)-[r: action {name: $rname}]->(d)", cname=code_name, rname=relation[1], dname=entity)


# INPUT: session, list of artifact names, type of artifacts in the list
# For each artifact, if it doesn't exist in DB, inserts it as a "_type" node.
def create_artifact_nodes(session, artifacts, _type):
    new_methods = 0
    for art in artifacts:
        if _type == "Method":
            # Check if javamethod is present else, add normal method
            records = session.run("MATCH (m: JavaMethod) WHERE (m.name = $mname) RETURN COUNT(m)", mname=art).data()
            records1 = session.run("MATCH (m: Method) WHERE (m.name = $mname) RETURN COUNT(m)", mname=art).data()
            if records == 0 and records1 == 0:
                session.run("CREATE (a:" + _type + " {name: $name})", name=art)
                new_methods = new_methods + 1
            # session.run("MERGE (a:" + _type + " {name: $name})", name=art)
        elif _type == "StringLiteral" or _type == "Comment":
            # session.run("MERGE (a:Description {name: $name, type: $type})", name=art, type=_type)
            session.run("MERGE (a:Description {name: $name})", name=art)

    return new_methods

# INPUT: session, list of edges. Each edge contains [name1, type1, name2, type2, relation]. (1)-[relation]->(2)
def create_relations(session, edges):
    for edge in edges:
        prop1 = "uri" if edge[1] == "Code" else "name"
        prop2 = "uri" if edge[3] == "Code" else "name"
        
        # Finding type1
        if edge[1] == "Code":
            type1 = "Code"
        elif edge[1] == "Method":
            records = session.run("MATCH (m: JavaMethod) WHERE (m.name = $mname) RETURN COUNT(m)", mname=edge[0]).data()
            type1 = "Method" if records == 0 else "JavaMethod"
        else:
            type1 = "Description"

        # Finding type2
        if edge[3] == "Code":
            type2 = "Code"
        elif edge[3] == "Method":
            records = session.run("MATCH (m: JavaMethod) WHERE (m.name = $mname) RETURN COUNT(m)", mname=edge[2]).data()
            type2 = "Method" if records == 0 else "JavaMethod"
        else:
            type2 = "Description"

        query = "MATCH (a:" + type1 + "), (b:" + type2 + ") WHERE a." + prop1 + "=\"" + edge[0] + "\" AND b." + prop2 + " = \"" + edge[2] + "\" MERGE (a)-[r:" + edge[4] + "]->(b)"
        res = session.run(query)


def return_all(session):
    session.run("MATCH (a)-[r]->(b) RETURN *")


def insert_codes(path, driver):
    index = 0
    with driver.session() as session:
        for i in range(16):
            with open(os.path.join(path, 'java_train_' + str(i) + '.jsonl')) as f:
                for i, line in enumerate(f):
                    if i % 40 == 0:             # Consider only 10K codes randomly
                        instance = json.loads(line)
                        code = instance['code']
                        code_lines = code.split('\n')
                        code_lines = [i.strip() for i in code_lines]
                        code_name = instance['func_name']
                        docstring = instance['docstring']
                        
                        stats = update_kg(session, code, code_lines, code_name, docstring, instance['url'])
                        
                        # instance['stats'] = {"total": stats[0], "non-standard": stats[1]}
                        # with open('stats.jsonl', 'a') as f1:
                        #     f1.write(json.dumps(instance) + '\n')


if __name__ == '__main__':
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "123"))
    path = 'C:\\Users\\karthik chandra\\Desktop\\CS\\DEMO\\CodeSearchNet\\resources\\data\\java\\final\\jsonl\\train'
    insert_codes(path, driver)