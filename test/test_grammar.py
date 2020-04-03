from unittest import TestCase
from mlangpy.grammar import *


class TestSymbol(TestCase):

    def setUp(self):
        class TSym(Symbol):
            pass

        class NSym(Symbol):
            def __init__(self, subject):
                super().__init__(subject, left_bound='/', right_bound='/')

        self.TSym = TSym
        self.NSym = NSym

    def test__eq__1(self):
        s = Symbol('a')
        self.assertEqual(s, s)

    def test__eq__2(self):
        s = Symbol('a')
        t = Symbol('b')
        self.assertNotEqual(s, t)

    def test__eq__3(self):
        s = Symbol('a', left_bound='/', right_bound='\\')
        t = Symbol('a', left_bound='#', right_bound='#')
        self.assertEqual(s, t)

    def test__eq__4(self):
        s = Symbol('a', left_bound='/', right_bound='\\')
        t = Symbol('a', left_bound='#', right_bound='#')
        self.assertEqual(t, s)

    def test__eq__5(self):
        # Subclasses can be equal to their supers, but not to their siblings.


        s = Symbol('a')
        t = self.TSym('a')
        self.assertEqual(s, t)

    def test__eq__6(self):
        s = Symbol('a')
        t = self.TSym('a')
        self.assertEqual(t, s)

    def test__eq__7(self):
        t = self.TSym('a')
        n = self.NSym('b')
        self.assertNotEqual(t, n)


class TestSequences(TestCase):

    def test__eq__1(self):
        f = Sequence(['a', 'b'])
        g = Sequence(['a', 'b'])
        self.assertEqual(f, g)

    def test__eq__2(self):
        # Subclasses can be deemed equal, as long as terms are equal
        class GSeq(Sequence):
            def __init__(self, terms):
                super().__init__(terms, separator='/')

        f = Sequence(['a', 'b'])
        g = GSeq(['a', 'b'])
        self.assertEqual(f, g)

    def test__eq__3(self):
        f = Sequence(['a', 'b'])
        g = Sequence(['a', 'c'])
        self.assertNotEqual(f, g)

    def test__eq__4(self):
        f = Sequence([])
        g = Sequence([])
        self.assertEqual(f, g)

    def test__eq__5(self):
        class GSeq(Sequence):
            def __init__(self, terms):
                super().__init__(terms, separator='/')

        f = Sequence(['a', 'b'])
        g = GSeq(['a', 'b'])
        self.assertEqual(g, f)

    def test_addition1(self):
        f = Sequence(['a', 'b'])
        b = 'c'
        self.assertEqual((f + b)[2], 'c')

    def test_addition2(self):
        f = Sequence(['a', 'b'])
        b = 'c'
        self.assertEqual((b + f).terms[0], 'c')

    def test_addition3(self):
        f = Sequence([])
        b = 'c'
        self.assertEqual((f + b).terms[0], 'c')

    def test_addition4(self):
        f = Sequence([])
        g = Sequence([])

        assert issubclass((f + g).__class__, Sequence)
        self.assertEqual((f + g).terms, [])

    def test_addition5(self):
        f = Sequence([])
        g = Sequence(['a'])

        assert issubclass((f + g).__class__, Sequence)
        self.assertEqual((f + g).terms[0], 'a')

    def test_addition6(self):
        f = Sequence(['a', 'b'])
        g = Sequence(['c', 'd'])

        assert issubclass((f + g).__class__, Sequence)
        assert (f + g).terms[0] == 'a'
        assert (f + g).terms[1] == 'b'
        assert (f + g).terms[2] == 'c'
        assert (f + g).terms[3] == 'd'

    def test_addition7(self):
        f = Sequence(['a', 'b'])
        g = Sequence([])

        assert issubclass((f + g).__class__, Sequence)
        assert (f + g).terms[0] == 'a'
        assert (f + g).terms[1] == 'b'
        assert len((f + g).terms) == 2


class TestDefinitionList(TestCase):

    def test_addition1(self):
        pass


class TestRuleset(TestCase):

    def setUp(self):
        # Example rules: Ruleset equality checks are recursive so using real Rules here would be silly
        self.r1 = 'a -> b c | d'
        self.r2 = 'x -> y | z'
        self.r3 = 'y -> t y | '
        self.ruleset = Ruleset(OrderedSet([self.r1, self.r2]))

    def test__eq__1(self):
        self.assertEqual(Ruleset([]), Ruleset([]))

    def test__eq__2(self):
        self.assertEqual(self.ruleset, self.ruleset)

    def test__eq__3(self):
        new_rule = Ruleset(OrderedSet([self.r1, self.r2]))
        self.assertEqual(self.ruleset, new_rule)

    def test__eq__4(self):
        new_rule = Ruleset([self.r1, self.r2])
        self.assertEqual(self.ruleset, new_rule)

    # Test adding Rules to a Ruleset
    # Addition for Rulesets will only work with Rule and Ruleset (subclasses)
    def test_addition1(self):
        with self.assertRaises(TypeError):
            self.ruleset + 1

    def test_addition2(self):
        with self.assertRaises(TypeError):
            object + self.ruleset

    def test_addition3(self):
        r = Rule(['a'], [['b']])
        new_ruleset = Ruleset([]) + r
        assert len(new_ruleset) == 1
        self.assertTrue(new_ruleset.rules[0], Rule)

    def test_addition4(self):
        r = Rule(['a'], [['b']])
        new_ruleset = self.ruleset + r
        assert len(new_ruleset) == 3
        self.assertTrue(isinstance(new_ruleset.rules[2], Rule))

    def test_addition5(self):
        r = Rule(['a'], [['b']])
        new_ruleset = r + self.ruleset
        assert len(new_ruleset) == 3
        self.assertTrue(isinstance(new_ruleset.rules[0], Rule))

    # Test adding Rulesets together
    def test_addition6(self):
        self.assertEqual(self.ruleset, self.ruleset + self.ruleset)

    def test_addition7(self):
        n = Ruleset(['rule'])
        q = self.ruleset + n
        self.assertEqual(q.rules[2], 'rule')

    def test_addition8(self):
        n = Ruleset(['rule'])
        q = n + self.ruleset
        self.assertEqual(q.rules[0], 'rule')

    # Test __iadd__ for Rules
    def test_iaddition1(self):
        r = Rule(['a'], [['b']])
        new_ruleset = copy.deepcopy(self.ruleset)
        new_ruleset += r

        assert isinstance(new_ruleset, Ruleset)
        assert len(new_ruleset.rules) == 3

    def test_iaddition2(self):
        new_ruleset = Ruleset([])
        new_ruleset += Rule(['a'], [['b']])

        assert isinstance(new_ruleset, Ruleset)
        assert len(new_ruleset.rules) == 1


    # Test __iadd__ for Rulesets
    def test_iaddition3(self):
        clone = copy.deepcopy(self.ruleset)
        clone += Ruleset([])

        assert isinstance(clone, Ruleset)
        assert len(clone.rules) == 2

    def test_iaddition4(self):
        clone = copy.deepcopy(self.ruleset)
        clone += Ruleset(['rule'])

        assert isinstance(clone, Ruleset)
        assert len(clone.rules) == 3
        self.assertEqual(clone.rules[2], 'rule')

    def test_iaddition5(self):
        with self.assertRaises(TypeError):
            self.ruleset += 'hi'

    def test_iaddition6(self):
        with self.assertRaises(TypeError):
            self.ruleset += object()

    def test_load_rules(self):
        pass

    def test_add_rule(self):
        pass

    def test_rule_exists(self):
        pass

    def test_update_rules(self):
        pass
