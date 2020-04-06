from lark import Lark, Transformer, Discard
from mlangpy.grammar import *
from mlangpy.metalanguages.EBNF import *
from mlangpy.metalanguages.RBNF import *
from mlangpy.metalanguages.BNF import *
#from mlangpy.metalanguages.ABNF import *


def validate_ABNF(grammar_string):
    l = Lark(f'''start: syntax
                %import .lark_grammars.abnf_faithful.syntax
                %ignore " "
                %import common.NEWLINE
                %ignore NEWLINE
            ''', keep_all_tokens=False)
    p = l.parse(grammar_string)
    return p


def validate_EBNF(grammar_string):
    l = Lark(f'''start: syntax
            %import .lark_grammars.ebnf2.syntax
            %import .common.NEWLINE
            %ignore NEWLINE+
            %ignore " "
        ''')
    p = l.parse(grammar_string)
    return p

# TODO update for DefinitionLists
class BuildBNF(Transformer):

    def start(self, args):
        return Metalanguage(args[0])

    def syntax(self, args):
        return Ruleset(args)

    def grammars__bnf__syntax_rule(self, args):
        return Rule(Sequence([args[0]]), args[1])

    def grammars__bnf__non_terminal(self, args):
        return NonTerminal(" ".join(args))

    def grammars__bnf__def_list(self, args):
        return DefinitionList(args)

    def grammars__bnf__def(self, args):
        return Sequence(args)

    def grammars__bnf__term(self, args):
        return args[0]

    def grammars__bnf__terminal(self, args):
        return Terminal(" ".join(args))


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
    pass


class BuildRBNF(Transformer):

    def start(self, args):
        return RBNF(args[0])

    def syntax(self, args):
        return Ruleset(args)

    def lark_grammars__rbnf__syntax_rule(self, args):
        return RBNFRule(RBNFSequence([args[0]]), args[1])

    def lark_grammars__rbnf__def_list(self, args):
        return DefinitionList(args)

    def lark_grammars__rbnf__def(self, args):
        return RBNFSequence(args)

    def lark_grammars__rbnf__term(self, args):
        return args[0]

    def lark_grammars__rbnf__terminal(self, args):
        return args[0]

    def lark_grammars__rbnf__object(self, args):
        return RBNFObject("_".join(args))

    def lark_grammars__rbnf__non_terminal(self, args):
        return args[0]

    def lark_grammars__rbnf__message(self, args):
        return RBNFMessage(" ".join(args))

    def lark_grammars__rbnf__construct(self, args):
        return RBNFConstruct(" ".join(args))

    def lark_grammars__rbnf__grouped_sequence(self, args):
        return Group(args[0])

    def lark_grammars__rbnf__optional_sequence(self, args):
        return Optional(args[0])

    def lark_grammars__rbnf__repeated_sequence(self, args):
        return RBNFRepetition(args[0])


def parse_BNF(filename: Path) -> Metalanguage:
    l = Lark(f'''start: syntax
        %import .grammars.bnf.syntax
        %import .common.NEWLINE
        %ignore NEWLINE+
        %ignore " "
    ''')

    grammar = open(filename).read()
    parsed = l.parse(grammar)
    return BuildBNF(visit_tokens=False).transform(parsed)


def parse_EBNF(filename) -> EBNF:
    # TODO come up with smart way of converting path (./grammars/bnf.lark) to importable form (.grammars.bnf)
    l = Lark('''start: syntax
        %import .lark_grammars.ebnf2.syntax
        %import .common.NEWLINE
        %ignore NEWLINE
        %ignore " "
    ''', keep_all_tokens=False)

    grammar = open(filename).read()
    parsed = l.parse(grammar)
    print(parsed.pretty())
    return BuildEBNF(visit_tokens=False).transform(parsed)


def parse_ABNF(filename: Path):
    l = Lark('''start: syntax
            %import .lark_grammars.abnf.syntax
            %import .common.NEWLINE
            %ignore NEWLINE
            %ignore " "
        ''')

    grammar = open(filename).read()
    parsed = l.parse(grammar)
    print(parsed.pretty())


def parse_RBNF(filename) -> RBNF:
    l = Lark('''start: syntax
        %import .lark_grammars.rbnf.syntax
        %import .common.NEWLINE
        %ignore NEWLINE+
        %ignore " "
    ''')

    grammar = open(filename).read()
    parsed = l.parse(grammar)
    print(parsed.pretty())
    return BuildRBNF(visit_tokens=False).transform(parsed)


if __name__ == '__main__':
    # parse_BNF('./sample_grammars/bnf_if.txt')

    #ebnf = parse_EBNF('../sample_grammars/ebnfs/testing.txt')

    f = open('../sample_grammars/ebnfs/ebnf_self_define_no_comments.txt').read()
    print(validate_EBNF(f).pretty())





