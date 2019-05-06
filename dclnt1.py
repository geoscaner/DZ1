import ast
import os
import collections

from nltk import pos_tag

TOT_FILES = 100


def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])


def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] == 'VB'


def get_filenames(path):
    filenames = []
    symptome = 0
    for dirname, dirs, files in os.walk(path, topdown=True):
        if symptome:
            break
        for file in files:
            if file.endswith('.py'):
                filenames.append(os.path.join(dirname, file))
                if len(filenames) == TOT_FILES:
                    symptome = 1
                    break
    print('total %s files' % len(filenames))
    # print('filenames',filenames)
    return filenames


def get_trees(path, with_filenames=False, with_file_content=False):
    trees = []
    # path= Path
    for filename in get_filenames(path):
        with open(filename, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()
        try:
            tree = ast.parse(main_file_content)
        except SyntaxError as e:
            print(e)
            tree = None
        if with_filenames:
            if with_file_content:
                trees.append((filename, main_file_content, tree))
            else:
                trees.append((filename, tree))
        else:
            trees.append(tree)
    print('trees generated')
    return trees


def get_all_names(tree):
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_verbs_from_function_name(function_name):
    return [word for word in function_name.split('_') if is_verb(word)]


def get_all_words_in_path(path):
    trees = [t for t in get_trees(path) if t]
    all_names = []
    for t in trees:
        all_names.append(get_all_names(t))
    function_names = [f for f in flat(all_names) if not (f.startswith('__') and f.endswith('__'))]

    def split_snake_case_name_to_words(name):
        return [n for n in name.split('_') if n]
    return flat([split_snake_case_name_to_words(function_name) for function_name in function_names])


def get_nodes(path):
    nodes = []
    for i, t in enumerate(get_trees(path)):
        nodes.append([])
        for node in ast.walk(t):
            if isinstance(node, ast.FunctionDef):
                nodes[i].append(node.name.lower())
    return nodes


def get_top_verbs_in_path(path, top_size=10):
    fncs = [f for f in flat(get_nodes(path)) if not (f.startswith('__') and f.endswith('__'))]
    print('functions extracted')
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in fncs])
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=10):
    nms = [f for f in flat(get_nodes(path)) if not (f.startswith('__') and f.endswith('__'))]
    return collections.Counter(nms).most_common(top_size)


if __name__ == '__main__':
    wds = []
    nms = []
    aws = []

    projects = [
        'django',
        'flask',
        'pyramid',
        'reddit',
        'requests',
        'sqlalchemy',
    ]

    for project in projects:
        path = os.path.join('.', project)
        wds += get_top_verbs_in_path(path)
        nms += get_top_functions_names_in_path(path)
        aws += get_all_words_in_path(path)
        print('path', path)

    print('WDS', wds)
    top_size = 200
    print('total %s words, %s unique' % (len(wds), len(set(wds))))

    for word, occurence in collections.Counter(wds).most_common(top_size):
        print('Total', word, occurence)
