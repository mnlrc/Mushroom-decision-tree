import unittest
from unittest.mock import patch
from project import *

class TestMushroomDataLoading(unittest.TestCase):
    def setUp(self):
        self.mushrooms = load_dataset('mushrooms.csv')

    def test_load_dataset(self):
        m1 = self.mushrooms[0]
        self.assertFalse(m1.is_edible(), "Le premier champignon devrait être non comestible.")
        self.assertEqual(m1.get_attribute('cap-shape'), 'Convex')
        self.assertEqual(m1.get_attribute('odor'), 'Pungent')

        m2 = self.mushrooms[1]
        self.assertTrue(m2.is_edible(), "Le deuxième champignon devrait être comestible.")
        self.assertEqual(m2.get_attribute('cap-color'), 'Yellow')
        self.assertEqual(m2.get_attribute('odor'), 'Almond')

        m3 = self.mushrooms[2]
        self.assertTrue(m3.is_edible(), "Le troisième champignon devrait être comestible.")
        self.assertEqual(m3.get_attribute('cap-shape'), 'Bell')
        self.assertEqual(m3.get_attribute('odor'), 'Anise')

def make_mushroom(attributes):
    ret = Mushroom(None)
    for k, v in attributes.items():
        ret.add_attribute(k, v)
    return ret

class TestBuildTree(unittest.TestCase):
    def setUp(self):
        self.test_tree_root = build_decision_tree(load_dataset('mushrooms.csv'))

    def test_tree_main_attribute(self):
        self.assertEqual(self.test_tree_root.criterion_, 'odor', "Le premier critère de division doit être 'odor'")
        nos = ['Pungent', 'Creosote', 'Foul', 'Fishy', 'Spicy', 'Musty']
        odors = {edge.label_: edge.child_ for edge in self.test_tree_root.edges_}
        for odor in nos:
            self.assertTrue(
                odors[odor].is_leaf() and odors[odor].criterion_ == 'No',
                f'Les champignons avec une odeur \'{odor}\' doivent être non-comestibles'
            )
    def test_tree_prediction(self):
        root = self.test_tree_root
        self.assertTrue(is_edible(root, make_mushroom({'odor': 'Almond'})))
        self.assertFalse(is_edible(root, make_mushroom({'odor': 'None', 'spore-print-color': 'Green'})))


#------------------------TESTS PERSONNALISES------------------------#


#tests P1
class TestsP1(unittest.TestCase):
    def setUp(self):
        self.mushrooms = load_dataset('mushrooms.csv')

    def test_attribute_values(self):
        self.assertTrue(get_attribute_values('habitat', self.mushrooms).keys(), get_values_of_attribute(self.mushrooms, 'habitat'))
        self.assertTrue(get_attribute_values('odor', self.mushrooms).keys(), get_values_of_attribute(self.mushrooms, 'odor'))
                

    def test_information_gain(self):
        self.assertEqual(get_info_gain(get_attribute_values('odor', self.mushrooms), get_entropy(self.mushrooms),  len(self.mushrooms)),  0.9092380018563967)
        self.assertNotEqual(get_info_gain(get_attribute_values('habitat', self.mushrooms), get_entropy(self.mushrooms), len(self.mushrooms)), 0.0245435465465)


def get_values_of_attribute(mushrooms, attribute : str):
    attribute_values = []
    for mushroom in mushrooms:
        attribute_value = mushroom.get_attribute(attribute)
        if attribute_value not in attribute_values:
            attribute_values.append(attribute_value)
    
    return attribute_values



class TestsP2(unittest.TestCase):
    def setUp(self):
        self.test_tree_root = build_decision_tree(load_dataset('mushrooms.csv'))

    @patch('builtins.input', side_effect = ['', 'None', 'White', 'Waste', 'E'])
    def test_chosen_path_comestible(self, mock_input):
        self.assertTrue(chosen_path(self.test_tree_root))

    @patch('builtins.input', side_effect = ['', 'None', 'White', 'Woods', 'Narrow', 'E'])
    def test_chosen_path_comestible(self, mock_input):
        self.assertFalse(chosen_path(self.test_tree_root))



#tests arbre booléen
class TestBoolTree(unittest.TestCase):
    def setUp(self):
        self.test_tree_root = build_decision_tree(load_dataset('mushrooms.csv'))
        self.bool_tree = bool_tree(self.test_tree_root)


    def test_right_attributes_in_bool_tree(self):
        self.assertEqual(tree_attributes_to_set(self.test_tree_root), bool_string_to_set(self.bool_tree))

    
    def test_bool_tree_string(self):
        self.assertIn('odor = Almond', self.bool_tree)
        self.assertNotIn('odor = Spicy', self.bool_tree)
        self.assertEqual(self.bool_tree.count('('), self.bool_tree.count(')'))
        self.assertIn('(habitat = Woods AND (gill-size = Broad))', self.bool_tree)


def tree_attributes_to_set(tree, res = []):
    for edge in tree.edges_:
        if edge.child_.is_leaf() and edge.child_.criterion_ == 'Yes':
            res.append(edge.label_) 
        elif not edge.child_.is_leaf():
            res.append(edge.label_)
            tree_attributes_to_set(edge.child_)
    return set(res)


def bool_string_to_set(bool_tree):
    bool_tree = bool_tree.replace('AND', '').replace('OR', '')
    special_chars = ['(', ')', '=']
    for char in bool_tree:
        if char in special_chars:
            bool_tree = bool_tree.replace(char, ' ')
            special_chars.remove(char)
        if len(special_chars) == 0:
            break
    bool_tree = bool_tree.strip().split()
    for word in bool_tree:
        if word[0].islower():
            bool_tree.remove(word)

    return (set(bool_tree))





if __name__ == '__main__':
    unittest.main()