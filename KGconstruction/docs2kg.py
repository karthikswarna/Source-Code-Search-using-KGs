from neo4j import GraphDatabase
from extract_relations import *
import json

# Modules - 59
# Packages - 223
# Classes - 4352
# Methods - 33968
#*** No modules, packages with same name. But classes with same name are there in different packages/modules. ***
# These functions require {classes, packages, modules, methods}.json files to be present parallely to this file.

not_requires_base = [
    'java.base', 'java.desktop', 'java.management.rmi', 'java.se', 'java.sql', 'java.sql.rowset', 'java.xml.crypto',
    'jdk.accessibility','jdk.compiler','jdk.javadoc','jdk.jconsole','jdk.jshell','jdk.management','jdk.management.jfr','jdk.security.auth','jdk.security.jgss','jdk.xml.dom'
]
builtin_types = ['byte', 'char', 'short', 'int', 'long', 'float', 'double', 'boolean', 'void']
repeated_classes = ["Accessible", "AlreadyBoundException", "Annotation", "Array", "ArrayType ", "Attribute ", "AttributeList ", "Attributes ", "AttributeSet", "AuthenticationException", "Authenticator", "Certificate ", "CertificateEncodingException", "CertificateException", "CertificateExpiredException", "CertificateNotYetValidException", "CertificateParsingException", "Channels", "Comment", "Configuration ", "ConnectException", "Connection", "ContentHandler", "Control", "Date", "DefaultLoaderRepository", "Document", "DocumentEvent", "DOMLocator", "DTD", "Duration", "Element ", "Entity", "EntityReference", "ErroneousTree", "Event ", "EventListener", "EventQueue", "FactoryConfigurationError", "Field", "FileFilter", "Filter", "Formatter", "GarbageCollectorMXBean", "GroupLayout", "HTMLDocument", "IdentifierTree", "IntrospectionException", "InvalidAttributeValueException", "InvalidKeyException", "Label", "List", "LiteralTree", "Location", "Manifest", "MarshalException", "MemoryAddress", "Method", "Modifier", "ModuleReference", "MonitorInfo", "MouseEvent", "Namespace", "Notification", "OpenType", "OperatingSystemMXBean", "Operation", "ParagraphView", "Parser", "Period", "Predicate", "PrimitiveType", "ProcessingInstruction", "ProvidesTree", "Proxy", "Reference ", "ReferenceType", "ReturnTree", "Statement", "StyleSheet", "ThreadMXBean", "Timer ", "Timestamp ", "ToolProvider", "TreePath", "Type", "Types", "TypeVariable", "UnknownHostException", "UserPrincipal", "UsesTree", "VirtualMachine", "WildcardType", "XPathException", "XPathExpression"]


# Deleting all the data.
def delete_all(driver):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")


## Inserting modules into the graph.
def insert_modules(driver):
    with driver.session() as session:
        with open('modules.json') as f:
            modules = json.load(f)['modules']
            for module in modules:
                session.run("CREATE (n:JavaModule {name: $name, uri: $uri})", name = module['name'], uri=module['link'])
                
                # relations = extract_relations(module['description'])
                # for entity, relation in relations.items():
                #     session.run("MATCH (m: JavaModule) WHERE m.name = $mname MERGE (d: Description {name: $dname}) CREATE (m)-[r: action {name: $rname}]->(d)", mname=module['name'], rname=relation[1], dname=entity)
                description = preprocess_new(module['description'])
                for word in description:
                    session.run("MATCH (m: JavaModule) WHERE m.name = $mname MERGE (d: Description {name: $dname}) CREATE (m)-[r: has_description]->(d)", mname=module['name'], dname=word)


## Inserting module dependencies and packages into the graph.
def insert_packages(driver):
    with driver.session() as session:
        with open('packages.json') as f:
            mod_pack = json.load(f)['packages']     # mod_pack is an Array of (module - packages) mapping/dictionaries.
            for module in mod_pack:                 # module is a dictionary.
                for module_name, dependencies in module.items():
                    for package in dependencies['Exported packages']:
                        session.run("MATCH (m: JavaModule) WHERE m.name = $mname CREATE (p: JavaPackage {name: $pname, uri: $puri}) CREATE (m)-[r:exports]->(p)", mname = module_name, pname = package['name'], puri = package['link'])
                        
                        # relations = extract_relations(package['description'])
                        # for entity, relation in relations.items():
                        #     session.run("MATCH (p: JavaPackage) WHERE p.name = $pname MERGE (d: Description {name: $dname}) CREATE (p)-[r: action {name: $rname}]->(d)", pname = package['name'], rname = relation[1], dname = entity)
                        description = preprocess_new(package['description'])
                        for word in description:
                            session.run("MATCH (p: JavaPackage) WHERE p.name = $pname MERGE (d: Description {name: $dname}) CREATE (m)-[r: has_description]->(d)", pname=package['name'], dname=word)


                    for reqmodule in dependencies['Required modules']:
                        session.run("MATCH (a: JavaModule), (b: JavaModule) WHERE a.name = $aname AND b.name = $bname CREATE (a)-[r:requires]->(b)", aname = module_name, bname = reqmodule)
            
                    if module_name not in not_requires_base:
                        session.run("MATCH (a: JavaModule), (b: JavaModule) WHERE a.name = $aname AND b.name = \"java.base\" CREATE (a)-[r:requires]->(b)", aname = module_name)


## Inserting classes into the graph.
def insert_classes(driver):
    with driver.session() as session:
        with open('classes.json') as f:
            classes = json.load(f)['classes']
            for classs in classes:
                session.run("MATCH (p: JavaPackage) WHERE p.name = $pname CREATE (c:JavaClass {name: $name, uri: $uri}) CREATE (p)-[r:has_class]->(c)", pname = classs['package'], name = classs['name'], uri = classs['link'])
                
                # relations = extract_relations(classs['description'])
                # for entity, relation in relations.items():
                #     session.run("MATCH (p: JavaPackage)-[:has_class]->(c: JavaClass) WHERE p.name = $pname AND c.name = $cname MERGE (d: Description {name: $dname}) CREATE (c)-[r: action {name: $rname}]->(d)", pname = classs['package'], cname = classs['name'], rname = relation[1], dname = entity)
                description = preprocess_new(classs['description'])
                for word in description:
                    session.run("MATCH (p: JavaPackage)-[:has_class]->(c: JavaClass) WHERE p.name = $pname AND c.name = $cname MERGE (d: Description {name: $dname}) CREATE (c)-[r: has_description]->(d)", pname = classs['package'], cname = classs['name'], dname = word)


## Inserting inheritence relations and methods into the graph.
def insert_methods(driver):
    with driver.session() as session:
        with open('methods.json') as f:
            clas_meth = json.load(f)['methods']         # clas_meth is an array of (class - method) mappings/dictionaries.
            for classs in clas_meth:                    # classs is a dictionary.
                for class_name, methods in classs.items():
                    for method in methods['Own']:
                        session.run( """MATCH (p:JavaPackage)-[:has_class]->(c:JavaClass) WHERE p.name = $pname AND c.name = $cname
                                        CREATE (m:JavaMethod {name: $name, returns: $returns, params: $params}) 
                                        CREATE (c)-[:has_method]->(m)""", 
                                        pname = methods['package'], cname = class_name, name = method['name'], returns = method['returns'], params = method['parameters'])

                        # relations = extract_relations(method['description'])
                        # for entity, relation in relations.items():
                        #     session.run( """MATCH (p:JavaPackage)-[has_class]->(c:JavaClass)-[:has_method]->(m:JavaMethod) WHERE p.name = $pname AND c.name = $cname AND m.name = $mname
                        #                     MERGE (d: Description {name: $dname})
                        #                     CREATE (m)-[r:action {name: $rname}]->(d)""",
                        #                     pname = methods['package'], cname = class_name, mname = method['name'], dname = entity, rname = relation[1])
                        description = preprocess_new(method['description'])
                        for word in description:
                            session.run("""MATCH (p:JavaPackage)-[has_class]->(c:JavaClass)-[:has_method]->(m:JavaMethod) WHERE p.name = $pname AND c.name = $cname AND m.name = $mname
                                            MERGE (d: Description {name: $dname})
                                            CREATE (m)-[r:has_description]->(d)""",
                                            pname = methods['package'], cname = class_name, mname = method['name'], dname = word)

                    for method in methods['Inherited']:
                        session.run( """MATCH (p:JavaPackage)-[:has_class]->(c:JavaClass) WHERE p.name = $pname AND c.name = $cname
                                        MATCH (pp:JavaPackage)-[:has_class]->(cc:JavaClass) WHERE pp.name = $ppname AND cc.name = $ccname
                                        CREATE (cc)-[:inherits_from]->(c)""",
                                        pname = method['package'], cname = method['class'], ppname = methods['package'], ccname = class_name)


## Inserting the builtin types nodes.
def insert_types(driver):
    with driver.session() as session:
        for typee in builtin_types:
            session.run("CREATE (t:JavaType {name: $name})", name = typee)


if __name__ == "__main__":
    # Connecting to the database.
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "123"))

    delete_all(driver)
    insert_modules(driver)
    insert_packages(driver)
    insert_classes(driver)
    insert_methods(driver)
    # insert_types(driver)