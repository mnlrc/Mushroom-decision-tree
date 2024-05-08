"""
Auteur: Rocca Manuel
Matricule: 000596086
Date: 7/05/2023
Ce code analyse un ensemble de champignons donné dans un fichier
et classe ces champignons de manière optimale dans un arbre 
avant de l'afficher.
"""


import os
import csv
from math import log2


class Mushroom:
    '''
    Represents a mushroom with its attributes and edibility.

    Attributes:
        edible (bool): Indicates if the mushroom is edible.
    '''

    def __init__(self, edible: bool):
        '''
        Initializes a Mushroom object.

        Args:
            edible (bool): Indicates if the mushroom is edible.
        '''
        self.mushroom = {'edible': edible}

    
    def is_edible(self) -> bool:
        '''
        Checks if the mushroom is edible.

        Returns:
            bool: True if the mushroom is edible, False otherwise.
        '''
        return self.mushroom['edible']

    
    def add_attribute(self, name: str, value: str) -> None:
        '''
        Adds an attribute to the mushroom.

        Args:
            name (str): The name of the attribute.
            value (str): The value of the attribute.

        Returns:
            None
        '''
        self.mushroom[name] = value

    
    def get_attribute(self, name: str) -> str:
        '''
        Retrieves the value of a specific attribute.

        Args:
            name (str): The name of the attribute to retrieve.

        Returns:
            str: The value of the specified attribute.
        '''
        return self.mushroom[name]

    
    def general_attributes(self):
        '''
        Returns all attributes except edible.

        Returns:
            list: List of attribute names.
        '''
        keys = list(self.mushroom.keys())
        keys.remove('edible')
        return keys

    
class Node:
    '''
    Represents a node in the decision tree.

    Attributes:
        criterion_ (str): The criterion used to split the data at this node.
        is_leaf_ (bool): Indicates if the node is a leaf node.
        edges_ (list): List of edges leading to child nodes.
    '''

    def __init__(self, criterion: str, is_leaf: bool = False):
        '''
        Initializes a Node object.

        Args:
            criterion (str): The criterion used to split the data at this node.
            is_leaf (bool): Indicates if the node is a leaf node.

        Returns:
            None
        '''
        self.criterion_ = criterion
        self.is_leaf_ = is_leaf
        self.edges_ = []

    
    def is_leaf(self) -> bool:
        '''
        Checks if the node is a leaf node.

        Returns:
            bool: True if the node is a leaf node, False otherwise.
        '''
        return self.is_leaf_

    
    def add_edge(self, label: str, child: 'Node') -> None:
        '''
        Adds an edge to connect the current node to a child node.

        Args:
            label (str): The label associated with the edge.
            child (Node): The child node connected by the edge.

        Returns:
            None
        '''
        self.edges_.append(Edge(self, child, label))
    

    def get_labels(self):
        '''
        Retrieves the labels associated with the outgoing edges.

        Returns:
            list: List of edge labels.
        '''
        ret = []
        for edge in self.edges_:
            ret.append(edge.label_)
        return ret


class Edge:
    '''
    Represents an edge connecting two nodes in the decision tree.

    Attributes:
        parent_ (Node): The parent node.
        child_ (Node): The child node.
        label_ (str): The label associated with the edge.
    '''
    
    def __init__(self, parent: Node, child: Node, label: str):
        '''
        Initializes an Edge object.

        Args:
            parent (Node): The parent node.
            child (Node): The child node.
            label (str): The label associated with the edge.

        Returns:
            None
        '''
        self.parent_ = parent
        self.child_ = child
        self.label_ = label


def load_dataset(path: str) -> list[Mushroom]: 
    '''
    Loads the mushroom dataset from a CSV file.

    Args:
        path (str): The path to the CSV file.

    Returns:
        list: List of Mushroom objects representing the dataset.
    '''
    mushrooms = []
    with open('mushrooms.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        characteristics = next(csvreader) #getting attributes

        for row in csvreader:
            mushroom = Mushroom(row[0].strip() == 'Yes') #creating object
            for attribute in range(1, len(row)):
                #adding attributes to corresponding object
                mushroom.add_attribute(characteristics[attribute], row[attribute])
            mushrooms.append(mushroom)
            
    return mushrooms


def build_decision_tree(mushrooms: list[Mushroom]) -> Node:
    '''
    Builds a decision tree based on the information gain of a set of mushrooms.
    The tree is built recursively by going through subsets of mushrooms.

    Args:
        mushrooms (list): List of Mushroom objects representing the dataset.

    Returns:
        Node: The root node of the decision tree.
    '''

    #base cases of recursion
    edibles = all_edible(mushrooms)
    if len(edibles) == len(mushrooms):
        return Node('Yes', True)
    elif len(edibles) == 0:
        return Node('No', True)
    
    #attribute choice
    parent_entropy = get_entropy(mushrooms)
    max_info_gain = -1
    for attribute in mushrooms[0].general_attributes():
        attribute_values = get_attribute_values(attribute, mushrooms)
        info_gain = get_info_gain(attribute_values, parent_entropy, len(mushrooms))

        if info_gain > max_info_gain:
            max_info_gain = info_gain
            #keeping the attribute with the best information gain of the
            #current set and the mushrooms that possess the attribute
            split_attr, split_attr_mushrooms = attribute, attribute_values
            
            
    #building tree recursively
    node = Node(split_attr)
    for value, shrooms in split_attr_mushrooms.items():
        child = build_decision_tree(shrooms)#recursive call
        node.add_edge(value, child)
    
    return node


def get_attribute_values(attribute: str, mushrooms: list[Mushroom]) -> dict:
    '''
    Retrieves all attribute values and mushrooms that have this value.

    Args:
        attribute (str): The name of the attribute.
        mushrooms (list): List of Mushroom objects representing the dataset.

    Returns:
        dict: Dictionary mapping attribute values to lists of corresponding mushrooms.
    '''
    subsets = {}
    for mushroom in mushrooms:
        attribute_value = mushroom.get_attribute(attribute)
        if attribute_value not in subsets:
            subsets[attribute_value] = []
        subsets[attribute_value].append(mushroom)
    
    return subsets


def number_of_edibles(mushrooms: list[Mushroom]) -> int:
    '''
    Counts the number of edible mushrooms in a dataset.

    Args:
        mushrooms (list): List of Mushroom objects representing the dataset.

    Returns:
        int: Number of edible mushrooms.
    '''
    return sum(1 for mushroom in mushrooms if mushroom.is_edible())


def get_info_gain(attribute_values: dict, parent_entropy: int, total_mushrooms: int) -> int:
    '''
    Calculates the information gain of an attribute by going through all of its possible values.
    It uses the formula given in the project guidelines

    Args:
        attribute_values (dict): Dictionary mapping attribute values to lists of corresponding mushrooms.
        parent_entropy (int): Entropy of the parent dataset.
        total_mushrooms (int): Total number of mushrooms in the dataset.

    Returns:
        int: Information gain of the attribute.
    '''
    sum = 0
    for shrooms in attribute_values.values():
        sum += (number_of_edibles(shrooms) / total_mushrooms) * get_entropy(shrooms)
    return parent_entropy - sum


def get_entropy(subset: list[Mushroom]) -> int:
    '''
    Calculates the entropy of a given dataset based on the formula given in
    the project guidelines.

    Args:
        subset (list): Subset of Mushroom objects representing a dataset.

    Returns:
        int: Entropy of the dataset.
    '''
    py = (number_of_edibles(subset) / len(subset))
    return 0 if (py == 0 or py == 1) else (py * log2((1 - py) / py)) - log2(1 - py) 


def all_edible(mushrooms: list[Mushroom]) -> list:
    '''
    Retrieves all edible mushrooms from a dataset.

    Args:
        mushrooms (list): List of Mushroom objects representing the dataset.

    Returns:
        list: List of edible Mushroom objects.
    '''
    edibles = []
    for mushroom in mushrooms:
        if mushroom.is_edible():
            edibles.append(mushroom)
    return edibles


def is_edible(root: Node, mushroom: Mushroom) -> bool:
    '''
    Checks if a given mushroom is edible by searching recursively
    in the previously built tree.

    Args:
        root (Node): The root node of the decision tree.
        mushroom (Mushroom): The mushroom to check.

    Returns:
        bool: True if the mushroom is edible, False otherwise.
    '''
    if root.criterion_ == 'Yes':
        return True
    elif root.criterion_ == 'No':
        return False

    for edge in root.edges_:
        #going through all edges to find the right route
        if mushroom.get_attribute(root.criterion_) == edge.label_:
            return is_edible(edge.child_, mushroom)


def display(tree: Node, indent = 0) -> None:
    '''
    Displays the decision tree using preorder traversal.

    Args:
        tree (Node): The root node of the decision tree.
        indent (int): The indentation level for formatting.

    Returns:
        None
    '''
    if tree.is_leaf():
        print(" " * indent, end = '')
        prt = f'\u21B3 \x1b[91m{tree.criterion_}\x1b[0m' if tree.criterion_ == 'No'\
                                                else f'\u21B3 \x1b[92m{tree.criterion_}\x1b[0m'
        print(prt)
        return None
    for edge in tree.edges_:
        print(" " * indent, end = '')
        print(f'\x1b[1m{tree.criterion_}\x1b[0m = \x1b[3m{edge.label_}\x1b[0m')
        display(edge.child_, indent + 4)
    
    
def bool_tree(tree: Node) -> str:
    '''
    Generates the boolean expression representing the decision tree.

    Args:
        tree (Node): The root node of the decision tree.

    Returns:
        str: The boolean expression representing the decision tree.
    '''
    ret = ''
    subtrees = []
    first_expression_added = False
    
    for edge in tree.edges_:
                
        if not edge.child_.is_leaf(): #gathering subtrees
            subtrees.append([edge.child_, edge.label_])
        elif edge.child_.criterion_ == 'Yes': #only treating positive ones
            if first_expression_added:
                ret += ' OR '
            ret += f'({tree.criterion_} = {edge.label_})'
            first_expression_added = True    
    
    for i in range(len(subtrees)):
        subtree, label = subtrees[i]
        if first_expression_added:
            ret += ' OR '
        
        ret += f'({tree.criterion_} = {label} AND {bool_tree(subtree)})'
        
    return ret


#--------------------------BONUS--------------------------#
def to_python(dt: Node, path: str) -> None:
    '''
    Converts the decision tree to Python code and saves it to a file.

    Args:
        dt (Node): The root node of the decision tree.
        path (str): The path to save the Python code.

    Returns:
        None
    '''
    with open(path, 'w', encoding = 'utf-8') as f:
        f.write('def to_python():\n')
        code = write_python(dt, f)
        f.write(code)
        f.write(f'{" " * 4}else:\n{" " * 8}return None')


def write_python(tree : Node, f, indent = 4, ret = '') -> str:
    '''
    Writes Python code representing the decision tree.

    Args:
        tree (Node): The root node of the decision tree.
        f (file): The file object to write to.
        indent (int): The indentation level for formatting.
        ret (str): The generated Python code.

    Returns:
        str: The generated Python code.
    '''
    first_expression_added = False
    for edge in tree.edges_:
        if edge.child_.is_leaf():
            if not first_expression_added:
                ret += f'{" " * indent}if \'{tree.criterion_}\' == \'{edge.label_}\':\n'
                ret += f'{" " * (indent + 4)}return {edge.child_.criterion_ == "Yes"}\n'
                first_expression_added = True
            else:
                ret += f'{" " * indent}elif \'{tree.criterion_}\' == \'{edge.label_}\':\n'
                ret += f'{" " * (indent + 4)}return {edge.child_.criterion_ == "Yes"}\n'
        elif not edge.child_.is_leaf():
            if not first_expression_added:
                ret += f'{" " * indent}if \'{tree.criterion_}\' == \'{edge.label_}\':\n'
                ret += write_python(edge.child_, f, indent + 4)
                first_expression_added = True
            else:
                ret += f'{" " * indent}elif \'{tree.criterion_}\' == \'{edge.label_}\':\n'
                ret += write_python(edge.child_, f, indent + 4)
    
    return ret
#---------------------------------------------------------#


def chosen_path(root : Node) -> None:
    '''
    Guides the user through the decision tree to determine the edibility of a mushroom.

    Args:
        root (Node): The root node of the decision tree.

    Returns:
        None
    '''
    while root.criterion_ != 'Yes' and root.criterion_ != 'No':
        attribute = str(input(f'Please input the {root.criterion_} of your mushroom: '))
        if attribute not in root.get_labels():
            continue
        else:
            for edge in root.edges_:
                if attribute == edge.label_:
                    root = edge.child_
    
    res = 'Your mushroom is indeed \x1b[92mcomestible\x1b[0m.' if root.criterion_ == 'Yes' else 'Your mushroom is \x1b[91mpoisonous\x1b[0m.'
    print(res)
    return True if root.criterion_ == 'Yes' else False
            

def main():
    '''
    Main function to build and interact with the decision tree.
    '''
    tree = build_decision_tree(load_dataset(os.getcwd()))
    
    print('\n\x1b[1mMushroom decision tree: \x1b[0m\n')
    display(tree)
    
    print('\n\n\n\x1b[1mMushroom decision tree\'s boolean expression: \x1b[0m\n')
    print(bool_tree(tree))
    to_python(tree, 'to_python.py')

    print('\n\n')
    user_input = str(input('Would you like to test the edibility of a mushroom?\nPress \'\u21B3\' to continue, \'E\' to exit: '))
    while user_input.upper() != 'E':
        chosen_path(tree)
        user_input = str(input('\nWould you like to test the edibility of another mushroom?\nPress \'\u21B3\' to continue, \'E\' to exit: '))




if __name__ == '__main__':
    main()