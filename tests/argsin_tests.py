import unittest
from argsin import ArgsIn


class ArgsInTest(unittest.TestCase):

    # def test_output(self):
    #     argsin = ArgsIn()
    #     argsin.add_action(['name', 'nickname'], lambda x: print("I'm: " + x), 2)
    #     argsin.add_action('country', lambda x: print('country: ' + x))
    #     argsin.add_action('cool', lambda: print("I'm cool!"))
    #     argsin.add_action('thing', 10)

    def test_find_arguments(self):
        argsin = ArgsIn()
        test_map = {
            'one two --name hello':
                ('one two', {'name': 'hello'}),
            'one --name "hello"':
                ('one', {'name': 'hello'}),
            "one --name 'hello'":
                ('one', {'name': 'hello'}),
            """one --name 'he"llo' """:
                ('one', {'name': 'he"llo'}),
            """one --name "he'llo" """:
                ('one', {'name': "he'llo"}),
            'one - two --name hello':
                ('one - two', {'name': 'hello'}),
            'one --int 100':
                ('one', {'int': '100'}),
            'one --negative -100':
                ('one', {'negative': '-100'}),
            'one --float 100.19':
                ('one', {'float': '100.19'}),
            'one --broken_float 100.19.1':
                ('one', {'broken_float': '100.19.1'}),
            'one --comma_float 100,191':
                ('one', {'comma_float': '100,191'}),
            'one --name hello bro':
                ('one', {'name': 'hello bro'}),
            'one --name hello bro --last cho':
                ('one', {'last': 'cho', 'name': 'hello bro'}),
            'one --name hello bro --last cho do':
                ('one', {'name': 'hello bro', 'last': 'cho do'}),
        }
        for k, values in test_map.items():
            self.assertEquals(argsin.find_arguments(k), values)

if __name__ == '__main__':
    unittest.main()