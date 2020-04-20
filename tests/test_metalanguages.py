from unittest import TestCase
from mlangpy.grammar import *
from mlangpy.metalanguages import *

class TestMetalanguage(TestCase):

    def setUp(self):
        t = Terminal('a')
        n = NonTerminal('A')

        r = Rule(
            Concat([n]),
            DefList([
                Concat([Optional(Concat([t]))])
            ])
        )
        r2 = Rule(
            Concat([n]),
            DefList([
                Concat([Group(Concat([t]))])
            ])
        )

        ruleset = Ruleset([r, r2])
        self.ml = Metalanguage(ruleset)

    def test_remove_groups1(self):
        r = self.ml.remove_groups_from(self.ml.ruleset[1])
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].left[0], NonTerminal('grp 0'))
        self.assertEqual(r[0].right[0][0], Terminal('a'))