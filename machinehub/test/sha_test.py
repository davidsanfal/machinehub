import unittest
from machinehub.sha import dict_sha1
from time import sleep


class DictShaTest(unittest.TestCase):

    def simple_loader_test(self):
        dict1 = {'a': 1,
                 'b': [1, 2, 3]}
        dict2 = {'a': 1,
                 'b': [1, 2, 3]}
        dict3 = {'a': 'hello'}
        self.assertEqual(dict_sha1(dict1),
                         '18eff0893cc200de676e24cc0e84c1027b50a25a')
        self.assertEqual(dict_sha1(dict2),
                         '18eff0893cc200de676e24cc0e84c1027b50a25a')
        self.assertEqual(dict_sha1(dict3),
                         '60966e549ed6ef2bdaaff8e8b76bd6bd7864351b')
        id1 = dict_sha1({})
        sleep(1/60)
        id2 = dict_sha1({})
        self.assertNotEqual(id1, id2)
