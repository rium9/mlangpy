import os
from unittest import TestCase
from mlangpy.metaparsers import *

def parse_all(grammar_directory, parse_method):
    for filename in os.listdir(grammar_directory):
        f = open(os.path.join(grammar_directory, filename)).read()
        print(f'----------{filename}----------')
        print(parse_method(f).pretty())

class TestGrammars(TestCase):

    def setUp(self):
        self.abnfs = '../sample_grammars/abnfs'
        self.ebnfs = '../sample_grammars/ebnfs'
        self.bnfs = '../sample_grammars/bnfs'
        self.rbnfs = '../sample_grammars/rbnfs'

    # Test all sample ABNFs using abnf.lark
    def test_abnf_lark_all(self):
        try:
            parse_all(self.abnfs, validate_ABNF)
        except:
            self.fail()

    # Test individual sample ABNFs using abnf.lark
    def test_abnf_abnf1(self):
        validate_ABNF(open(os.path.join(self.abnfs, 'abnf1.txt')).read())

    def test_abnf_abnf_self_define(self):
        validate_ABNF(open(os.path.join(self.abnfs, 'abnf_self_define.txt')).read())

    def test_abnf_abnf_test(self):
        validate_ABNF(open(os.path.join(self.abnfs, 'abnf_test.txt')).read())

    def test_abnf_abnf_testing(self):
        validate_ABNF(open(os.path.join(self.abnfs, 'abnf_testing.txt')).read())

    def test_abnf_core_abnf(self):
        validate_ABNF(open(os.path.join(self.abnfs, 'core_abnf.txt')).read())

    # Test all sample ABNFs using abnf_faithful.lark
    def test_abnf_faithful_lark_all(self):
        try:
            parse_all(self.abnfs, validate_ABNF_faithful)
        except:
            self.fail()

    # Test individual sample ABNFs using abnf_faithful.lark
    def test_abnf_faithful_abnf1(self):
        validate_ABNF_faithful(open(os.path.join(self.abnfs, 'abnf1.txt')).read())

    def test_abnf_faithful_abnf_self_define(self):
        validate_ABNF_faithful(open(os.path.join(self.abnfs, 'abnf_self_define.txt')).read())

    def test_abnf_faithful_abnf_test(self):
        validate_ABNF_faithful(open(os.path.join(self.abnfs, 'abnf_test.txt')).read())

    def test_abnf_faithful_abnf_testing(self):
        validate_ABNF_faithful(open(os.path.join(self.abnfs, 'abnf_testing.txt')).read())

    def test_abnf_faithful_core_abnf(self):
        validate_ABNF_faithful(open(os.path.join(self.abnfs, 'core_abnf.txt')).read())

    # Test all sample BNFs using bnf.lark
    def test_bnf_lark_all(self):
        try:
            parse_all(self.bnfs, validate_BNF)
        except:
            self.fail()

    # Test individual sample BNFs using bnf.lark
    def test_bnf_if(self):
        validate_BNF(open(os.path.join(self.bnfs, 'if.txt')).read())

    def test_bnf_algol(self):
        validate_BNF(open(os.path.join(self.bnfs, 'algol.txt')).read())

    def test_bnf_ant(self):
        validate_BNF(open(os.path.join(self.bnfs, 'ant.txt')).read())

    def test_bnf_ant2(self):
        validate_BNF(open(os.path.join(self.bnfs, 'ant2.txt')).read())

    # Test all sample RBNFs using rbnf.lark
    def test_rbnf_lark_all(self):
        try:
            parse_all(self.rbnfs, validate_RBNF)
        except:
            self.fail()

    # Test individual sample RBNFs using rbnf.lark
    def test_rbnf_flow_desc1(self):
        validate_RBNF(open(os.path.join(self.rbnfs, 'flow_desc1.txt')).read())

    def test_rbnf_flow_desc2(self):
        validate_RBNF(open(os.path.join(self.rbnfs, 'flow_desc2.txt')).read())

    def test_rbnf_flow_desc3(self):
        validate_RBNF(open(os.path.join(self.rbnfs, 'flow_desc3.txt')).read())

    def test_rbnf_if1(self):
        validate_RBNF(open(os.path.join(self.rbnfs, 'if1.txt')).read())

    def test_rbnf_if2(self):
        validate_RBNF(open(os.path.join(self.rbnfs, 'if2.txt')).read())

    def test_rbnf_notify(self):
        validate_RBNF(open(os.path.join(self.rbnfs, 'notify.txt')).read())

    def test_rbnf_pathmessage(self):
        validate_RBNF(open(os.path.join(self.rbnfs, 'pathmessage.txt')).read())

    def test_rbnf_resvconfmessage(self):
        validate_RBNF(open(os.path.join(self.rbnfs, 'resvconfmessage.txt')).read())

    # Test all sample EBNFs using ebnf.lark
    def test_ebnf_lark_all(self):
        try:
            parse_all(self.ebnfs, validate_EBNF)
        except:
            self.fail()

    # Test individual sample EBNFs using ebnf.lark
    def test_ebnf_ebnf_if(self):
        validate_EBNF(open(os.path.join(self.ebnfs, 'ebnf_if.txt')).read())

    def test_ebnf_ebnf_if2(self):
        validate_EBNF(open(os.path.join(self.ebnfs, 'ebnf_if2.txt')).read())

    def test_ebnf_ebnf_self_define(self):
        validate_EBNF(open(os.path.join(self.ebnfs, 'ebnf_self_define.txt')).read())

    def test_ebnf_ebnf_self_define_no_comments(self):
        validate_EBNF(open(os.path.join(self.ebnfs, 'ebnf_self_define_no_comments.txt')).read())

    def test_ebnf_ebnf_testing(self):
        validate_EBNF(open(os.path.join(self.ebnfs, 'testing.txt')).read())

    # Test all sample EBNFs using ebnf_faithful.lark
    def test_ebnf_faithful_lark_all(self):
        try:
            parse_all(self.ebnfs, validate_EBNF)
        except:
            self.fail()

    # Test individual sample EBNFs using ebnf_faithful.lark
    def test_ebnf_faithful_ebnf_if(self):
        validate_EBNF(open(os.path.join(self.ebnfs, 'ebnf_if.txt')).read())

    def test_ebnf_faithful_ebnf_if2(self):
        validate_EBNF_faithful(open(os.path.join(self.ebnfs, 'ebnf_if2.txt')).read())

    def test_ebnf_faithful_ebnf_self_define(self):
        validate_EBNF_faithful(open(os.path.join(self.ebnfs, 'ebnf_self_define.txt')).read())

    def test_ebnf_faithful_ebnf_self_define_no_comments(self):
        validate_EBNF_faithful(open(os.path.join(self.ebnfs, 'ebnf_self_define_no_comments.txt')).read())

    def test_ebnf_ebnf_testing(self):
        validate_EBNF_faithful(open(os.path.join(self.ebnfs, 'testing.txt')).read())