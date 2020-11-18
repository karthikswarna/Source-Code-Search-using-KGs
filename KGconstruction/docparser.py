from bs4 import BeautifulSoup
import bs4
import json
import os
# Class type?
# These functions require docs to be present parallel to this file.
# Having "module" field in {classes, methods}.json is not required. If needed in the future, uncomment the lines in extract_classes and extract_methods.

builtin_types = ['byte', 'char', 'short', 'int', 'long', 'float', 'double', 'boolean', 'void']


## Creates "classes.json" file which contains the list of classes along with their descriptions.
def extract_classes():
    parsed_html = BeautifulSoup(open(os.path.join(os.path.abspath(os.getcwd()), "docs\\api\\allclasses-index.html")), "html.parser")
    table = parsed_html.body.table.tbody
    i = 0
    classes = {}
    classes['classes'] = []
    for row in table.children:
        if i%2 != 0:
            class_name = row.td.a.contents[0]
            class_link = (row.td.a)['href']
            try:
                description = ""
                strings = row.th.div
                for string in strings.stripped_strings:
                    description = description + string + ' '
            except:
                description = ""
            
            # module = ""
            package = ""
            with open(os.path.join(os.path.abspath(os.getcwd()), "docs\\api\\" + str(class_link))) as f:
                parsed_html2 = BeautifulSoup(f, "html.parser")
                titles = parsed_html2.find_all("div", {"class": "sub-title"})
                # module = titles[0].a.contents[0]
                package = titles[1].a.contents[0]

            classes['classes'].append({
                'name': str(class_name),
                # 'module': str(module),
                'package': str(package), 
                'link': 'C:/Users/karthik chandra/Desktop/CS/DEMO/docs/api/' + str(class_link), 
                'description': str(description).replace('\\n', '').replace('\n', '')
            })
        i = i + 1

    with open('classes.json', 'w') as outfile:
        json.dump(classes, outfile, indent=4)

## Uses "classes.json" file to create "methods.json" file which contains the methods present in a class and their inheritence information.
def extract_methods():
    with open('classes.json') as f:
        methods = {}
        methods['methods'] = []
        classes = (json.load(f))['classes']
        # i = 0
        for clas in classes:
            # if i == 10:
            #     break
            classs = {}
            classs[clas['name']] = {"package": "", "Constructors": [], "Own": [], "Inherited": []}

            with open(clas['link']) as f2:
                parsed_html = BeautifulSoup(f2, "html.parser")

                ## Finding module and package of the class.
                titles = parsed_html.find_all("div", {"class": "sub-title"})
                # classs[clas['name']]['module'] = titles[0].a.contents[0]
                classs[clas['name']]['package'] = titles[1].a.contents[0]

                ## Finding Inherited methods and parent class names.
                method_summary = parsed_html.find("section", {"id": "method.summary"})
                if method_summary is not None:
                    inherited_list = method_summary.find_all("div", {"class": "inherited-list"})
                    for parent_class_obj in inherited_list:     # parent_class_obj is a <div>
                        # **Old code where package and class are not separated.
                        # pclass = ""
                        # for class_name in parent_class_obj.h3.stripped_strings:
                        #     pclass = pclass + class_name
                        # pclass = pclass.replace(u'\xa0', u' ').split(' ')[-1]

                        # Finding parent class name.
                        pclass = []
                        for class_name in parent_class_obj.h3.stripped_strings:
                            pclass.append(class_name)
                        pclass[0] = (pclass[0].replace(u'\xa0', u' ').split(' ')[-1])[:-1]      # This is package of parent class
                        
                        # Finding inherited methods. **Uncomment this part to include inherited method names also**
                        # inmethods = []
                        # for inherit_methods in parent_class_obj.code.stripped_strings:
                        #     if(inherit_methods != ","):
                        #         inmethods.append(inherit_methods)

                        # Adding inherited methods and parent classes details into dictionary. **Toggle these lines to toggle the use of inherited methods**
                        if(len(pclass) == 2):
                            # classs[clas['name']]["Inherited"].append({"package": pclass[0], "class": pclass[1], "methods": inmethods})
                            classs[clas['name']]["Inherited"].append({"package": pclass[0], "class": pclass[1]})

                ## Finding it's own methods.
                method_detail = parsed_html.find("section", {"id": "method.detail"})
                if method_detail is not None:
                    method_list = method_detail.find("ul", {"class": "member-list"}).findChildren("li", recursive=False)
                    for method in method_list:      # method is a <li>
                        # Extracting the method name
                        method_name = method.section.h3.contents[0]

                        # Extracting description of the method
                        description = ""
                        strings = method.section.find_all("div", {"class": "block"})
                        if len(strings) != 0:
                            for string in strings[0].stripped_strings:
                                description = description + string + ' '

                        # Extracting the return type.
                        return_type = method.find("span", {"class": "return-type"}).contents # If type is fundamental, this is sufficient.
                        if len(return_type) == 2:               # Return type is an array of objects.
                            return_type = return_type[0].contents[0] + return_type[1]
                        elif type(return_type[0]) is bs4.element.Tag:   # Return type is an object
                            return_type = return_type[0].contents[0]
                        else:                                           # Return type is primitive
                            return_type = return_type[0]

                        # Extracting the parameter types.
                        parameter_types = []
                        params = method.find("span", {"class": "parameters"})
                        if params is not None:
                            for param in params:        # param is an <a> or text
                                if type(param) is bs4.element.Tag:          # param is <a>
                                    parameter_types.append(param.contents[0])
                                else:
                                    param = param.replace(u"\u00A0", " ").replace('\n', ' ').replace(',', ' ').strip().split(' ')
                                    if len(param) > 1:        # param is a non-object type(fundamental type)
                                        for t in param:
                                            if t in builtin_types:
                                                parameter_types.append(t)

                        # Adding own methods details into dictionary.
                        classs[clas['name']]["Own"].append({
                            "name": method_name,
                            "returns": return_type,
                            "parameters": parameter_types,
                            "description": description.replace('\\n', '').replace('\n', '')
                        })
                
                ## Finding it's constructors.
                constructor_detail = parsed_html.find("section", {"id": "constructor.detail"})
                if constructor_detail is not None:
                    constructor_list = constructor_detail.find("ul", {"class": "member-list"}).findChildren("li", recursive=False)
                    for constructor in constructor_list:      # constructor is a <li>
                        # Extracting the constructor name
                        constructor_name = constructor.section.h3.contents[0]

                        # Extracting the parameter types.
                        parameter_types = []
                        params = constructor.find("span", {"class": "parameters"})
                        if params is not None:
                            for param in params:        # param is an <a> or text
                                if type(param) is bs4.element.Tag:          # param is <a>
                                    parameter_types.append(param.contents[0])
                                else:
                                    param = param.replace(u"\u00A0", " ").replace('\n', ' ').replace(',', ' ').strip().split(' ')
                                    if len(param) > 1:        # param is a non-object type(fundamental type)
                                        for t in param:
                                            if t in builtin_types:
                                                parameter_types.append(t)

                        # Adding own constructor details into dictionary.
                        classs[clas['name']]["Constructors"].append({
                            "name": constructor_name,
                            "parameters": parameter_types,
                        })

            methods['methods'].append(classs)
            # i = i + 1
        
    with open("methods.json", 'w') as f:
        json.dump(methods, f, indent=4)

## Creates "modules.json" file which contains the list of modules along with their descriptions.
def extract_modules():
    parsed_html = BeautifulSoup(open(os.path.join(os.path.abspath(os.getcwd()), "docs\\api\\index.html")), "html.parser")
    table = parsed_html.body.table.tbody
    i = 0
    modules = {}
    modules['modules'] = []
    for row in table.children:
        if i%2 != 0:            # Only in odd iterations we get bs4.tag element
            # Extracting module's name.
            module_name = row.th.a.contents[0]

            # Extracting module's uri.
            module_link = (row.th.a)['href']

            # Extracting module's description.
            try:
                description = ""
                strings = row.td.div
                for string in strings.stripped_strings:
                    description = description + string + ' '
            except:
                description = ""

            modules['modules'].append({
                'name': str(module_name), 
                'link': 'C:/Users/karthik chandra/Desktop/CS/DEMO/docs/api/' + str(module_link), 
                'description': str(description).replace('\\n', '').replace('\n', '')
            })
        i = i + 1

    with open('modules.json', 'w') as f:
        json.dump(modules, f, indent=4)

## Uses "modules.json" file to create "packages.json" file which contains the packages present in a module and their export information.
def extract_packages():
    with open('modules.json') as f:
        packages = {}
        packages['packages'] = []
        modules = (json.load(f))['modules']
        i = 0
        for module in modules:
            # if i == 10:
            #     break
            moduless = {}
            moduless[module['name']] = {"Exported packages": [], "Required modules": []}

            with open(module['link']) as f2:
                parsed_html = BeautifulSoup(f2, "html.parser")
                ## Finding exported packages.
                packages_summary = parsed_html.find("section", {"id": "packages.summary"})
                if packages_summary is not None:
                    exports = packages_summary.find("table", {"class": "summary-table"})
                    if exports is not None:
                        exports = exports.tbody             # Body of the "summary-table" which contains exported packages.
                        j = 0
                        for row in exports.children:
                            if j%2 != 0:
                                # Extracting package's name.
                                package_name = row.th.a.contents[0]

                                # Extracting package's uri.
                                package_link = row.th.a['href']

                                # Extracting package's description.
                                try:
                                    description = ""
                                    strings = row.td.div
                                    for string in strings.stripped_strings:
                                        description = description + string + ' '
                                except:
                                    description = ""

                                moduless[module['name']]["Exported packages"].append({
                                    'name': str(package_name), 
                                    'link': module['link'].rsplit('/', 1)[0] + '/' + str(package_link), 
                                    'description': str(description).replace('\\n', '').replace('\n', '')
                                })
                            j = j + 1

                ## Finding required modules.
                modules_summary = parsed_html.find("section", {"id": "modules.summary"})
                if modules_summary is not None:
                    requires = modules_summary.find_all("table", {"class": "details-table"})
                    if requires is not None:
                        requires = requires[0].tbody        # Body of first table i.e "Requires" table.
                        j = 0
                        for row in requires.children:
                            if j%2 != 0:
                                # Extracting parent module's name.
                                module_name = row.th.a.contents[0]

                                # module_link = row.th.a['href']
                                # try:
                                #     description = ""
                                #     strings = row.find("td", {"class": "col-last"}).div
                                #     for string in strings.stripped_strings:
                                #         description = description + string + ' '
                                # except:
                                #     description = ""
                                moduless[module['name']]["Required modules"].append(str(module_name))
                            j = j + 1

            packages['packages'].append(moduless)
            # i = i + 1
        
    with open("packages.json", 'w') as f:
        json.dump(packages, f, indent=4)


if __name__ == '__main__':
    extract_classes()
    extract_methods()

    extract_modules()
    extract_packages()