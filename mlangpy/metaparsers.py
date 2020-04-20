from lark import Lark, Transformer, Discard
from mlangpy.grammar import *
from mlangpy.metalanguages.EBNF import *
from mlangpy.metalanguages.RBNF import *
from mlangpy.metalanguages.BNF import *
from mlangpy.metalanguages.ABNF import *


def validate_BNF(grammar_string):
    l = Lark.open('./lark_grammars/bnf.lark', rel_to=__file__)
    return l.parse(grammar_string)


def validate_ABNF_faithful(grammar_string):
    l = Lark.open('./lark_grammars/abnf_faithful.lark', rel_to=__file__)
    return l.parse(grammar_string)


def validate_ABNF(grammar_string):
    l = Lark.open('./lark_grammars/abnf.lark', rel_to=__file__)
    return l.parse(grammar_string)


def validate_EBNF(grammar_string):
    l = Lark.open('./lark_grammars/ebnf.lark', rel_to=__file__)
    return l.parse(grammar_string)

def validate_EBNF_faithful(grammar_string):
    l = Lark.open('./lark_grammars/ebnf_faithful.lark', rel_to=__file__)
    return l.parse(grammar_string)

def validate_RBNF(grammar_string):
    l = Lark.open('./lark_grammars/rbnf.lark', rel_to=__file__)
    p = l.parse(grammar_string)
    return p


# TODO update for DefinitionLists
class BuildBNF(Transformer):

    def start(self, args):
        return BNF(args[0])

    def syntax(self, args):
        return Ruleset(args)

    def rule(self, args):
        return BNFRule(args[0], args[1])

    def elements(self, args):
        return args[0]

    def alternation(self, args):
        return DefList(args)

    def concatenation(self, args):
        return Concat(args)

    def element(self, args):
        return args[0]

    def non_terminal(self, args):
        return BNFNonTerminal(args[0])

    def terminal(self, args):
        return BNFTerminal(args[0])



class BuildEBNF(Transformer):

    def start(self, args):
        return EBNF(args[0])

    def syntax(self, args):
        return Ruleset(args)

    def lark_grammars__ebnf__syntax_rule(self, args):
        # TODO this doesn't look right!!
        return EBNFRule(EBNFSequence([args[0]]), DefinitionList(args[1]))

    def lark_grammars__ebnf__non_terminal(self, args):
        return EBNFNonTerminal(" ".join(args))

    def lark_grammars__ebnf__def_list(self, args):
        # TODO This method always creates a DefinitionList, regardless of whether there are any alternatives.
        # It's unclear if this is necessary, investigate. Could check the number of args and skip making the
        # DefinitionList.
        return DefinitionList(args)

    def lark_grammars__ebnf__def(self, args):
        return EBNFSequence(args)

    def lark_grammars__ebnf__term(self, args):
        return args[0]

    def lark_grammars__ebnf__factor(self, args):
        return args[0]

    def lark_grammars__ebnf__primary(self, args):
        # why are there sometimes no args?
        if len(args) != 0:
            return args[0]
        else:
            return Terminal("")

    def lark_grammars__ebnf__terminal(self, args):
        return EBNFTerminal(" ".join(args))

    def lark_grammars__ebnf__comment(self, args):
        # just drop comments for now
        raise Discard

    def lark_grammars__ebnf__optional_sequence(self, args):
        return Optional(args[0])

    def lark_grammars__ebnf__grouped_sequence(self, args):
        return Group(args[0])

    def lark_grammars__ebnf__repeated_sequence(self, args):
        return EBNFRepetition(args[0])


class BuildABNF(Transformer):
    """ Generate a metalanguages.ABNF.ABNF instance from a parse tree built using abnf.lark. """

    def start(self, args):
        return ABNF(args[0])

    def syntax(self, args):
        return Ruleset(args)

    def rule(self, args):
        return ABNFRule(args[0], args[1])

    def inc_rule(self, args):
        return ABNFIncRule(args[0], args[1])

    def rulename(self, args):
        return ABNFNonTerminal(args[0])

    def elements(self, args):
        return args[0]

    def alternation(self, args):
        return ABNFDefList(args)

    def concatenation(self, args):
        return Concat(args)

    def repetition(self, args):
        return args[0]

    def element(self, args):
        return args[0]

    def char_val(self, args):
        return ABNFTerminal(args[0])

    def num_val(self, args):
        return args[0]

    def hex_val(self, args):
        return args[0]

    def hex_single(self, args):
        return ABNFChar('h', args[0])

    def hex_range(self, args):
        return ABNFCharRange(ABNFChar('h', args[0]), ABNFChar('h', args[1]))

    def c_nl(self, args):
        raise Discard

    def repetition(self, args):
        if len(args) != 2:
            return args[0]

        rep_type_tree = args[0].children[0]
        if rep_type_tree.data == 'specific':
            return ABNFRepetition(args[1], left=int(rep_type_tree.children[0]), right=int(rep_type_tree.children[0]))
        elif rep_type_tree.data == 'variable':
            if len(rep_type_tree.children) == 3:
                return ABNFRepetition(args[1], left=int(rep_type_tree.children[0]), right=int(rep_type_tree.children[2]))
            elif len(rep_type_tree.children) == 1:
                return ABNFRepetition(args[1])
            else:
                if rep_type_tree.children[0].type == 'DEC_NUM':
                    return ABNFRepetition(args[1], left=int(rep_type_tree.children[0]))
                else:
                    return ABNFRepetition(args[1], right=int(rep_type_tree.children[1]))
        else:
            raise NotImplementedError()

    def group(self, args):
        return Group(args[0])

    def option(self, args):
        return Optional(args[0])


class BuildRBNF(Transformer):

    def start(self, args):
        return RBNF(args[0])

    def syntax(self, args):
        return Ruleset(args)

    def rule(self, args):
        return RBNFRule(args[0], args[1])

    def rulename(self, args):
        return args[0]

    def message(self, args):
        return RBNFMessage(args[0])

    def elements(self, args):
        return args[0]

    def alternation(self, args):
        return DefList(args)

    def concatenation(self, args):
        return Concat(args)

    def element(self, args):
        return args[0]

    def object(self, args):
        return RBNFObject(args[0])

    def construct(self, args):
        return RBNFConstruct(args[0])

    def option(self, args):
        return Optional(args[0])

    def group(self, args):
        return Group(args[0])

    def repetition(self, args):
        return RBNFRepetition(args[0])


def parse_BNF(grammar_string) -> Metalanguage:
    parsed = validate_BNF(grammar_string)
    return BuildBNF(visit_tokens=False).transform(parsed)


def parse_EBNF(grammar_string) -> EBNF:
    parsed = validate_EBNF(grammar_string)
    return BuildEBNF(visit_tokens=False).transform(parsed)


def parse_ABNF(grammar_string):
    parsed = validate_ABNF(grammar_string)
    return BuildABNF().transform(parsed)


def parse_RBNF(grammar_string) -> RBNF:
    parsed = validate_RBNF(grammar_string)
    return BuildRBNF().transform(parsed)


if __name__ == '__main__':
    # parse_BNF('./sample_grammars/bnf_if.txt')

    #ebnf = parse_EBNF('../sample_grammars/ebnfs/testing.txt')

    abnf = parse_ABNF('''
        comment =  ";" *(WSP / VCHAR) CRLF
        repeat = ;hi
            1*2DIGIT / (*DIGIT "*" *DIGIT)
        char-val =  DQUOTE *(%x20-21 / %x23-7E) DQUOTE
        repeat =/ "hi"
    ''')
    print(validate_BNF(open('../sample_grammars/bnfs/if.txt').read()).pretty())
    bnf = parse_BNF(open('../sample_grammars/bnfs/if.txt').read())
    print(bnf.ruleset)
    bnf.syntax[Terminal] = RBNFObject
    bnf.normalise()
    rbnf = parse_RBNF(open('../sample_grammars/rbnfs/pathmessage.txt').read())
    print(rbnf.ruleset)
    rbnf.syntax[RBNFObject] = EBNFTerminal
    rbnf.syntax[Repetition] = Operator
    rbnf.normalise()
    print(rbnf.ruleset)

    #b = validate_ABNF_faithful(open('../sample_grammars/abnfs/core_abnf.txt').read())
    #print(b.pretty())

    c = validate_EBNF(open('../sample_grammars/ebnfs/ebnf_self_define.txt').read())
    print(c.pretty())