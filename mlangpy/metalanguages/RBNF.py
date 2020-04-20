from ..grammar import *
from .Metalanguage import Metalanguage

symbols_mapping = {
    ';': 'SEMICOL',
    '=': 'EQUALS'
}

class RBNFObject(Terminal):

    def __init__(self, subject, left_bound='<', right_bound='>'):
        # TODO implement RBNF naming convention fully:
        #   'Objects are typically named in uppercase. They do not usually use
        #   spaces within the name, favoring underbars ("_").'
        if symbols_mapping.get(subject):
            subject = symbols_mapping.get(subject)
        super().__init__(subject.upper(), left_bound=left_bound, right_bound=right_bound)


class RBNFConstruct(NonTerminal):

    def __init__(self, subject, left_bound='<', right_bound='>'):
        # TODO implement RBNF naming convention fully:
        #   'Constructs are named in lowercase, although capitals are commonly
        #   used to indicate acronyms. Spaces and hyphens are used between words
        #   within names.'
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class RBNFMessage(NonTerminal):

    def __init__(self, subject, left_bound='<', right_bound='>'):
        # TODO implement RBNF naming convention fully:
        #   'Messages are typically named in title case.'
        super().__init__(subject.title(), left_bound, right_bound)


class RBNFRule(Rule):

    def __init__(self, left, right, production='::=', terminator=''):
        super().__init__(left, right, production=production, terminator=terminator)


class RBNFConcat(Concat):

    def __init__(self, terms, separator=' '):
        super().__init__(terms, separator=separator)


class RBNFRepetition(Operator):

    def __init__(self, subject, operator_sym='...'):
        super().__init__(subject, operator_sym=operator_sym)


class RBNF(Metalanguage):

    def __init__(self, ruleset, normalise=False):
        super().__init__(ruleset, syntax_dict={
            # Essential to all grammars
            Concat: RBNFConcat,
            DefList: DefList,
            Rule: RBNFRule,
            RBNFObject: RBNFObject,
            RBNFConstruct: RBNFConstruct,
            RBNFMessage: RBNFMessage,

            # Auxiliary stuff
            Optional: Optional,
            Group: Group,

            # Use anonymous functions to combine notations
            # Here, eliminate ambiguity by explicitly grouping
            Repetition: lambda x: RBNFRepetition(Group(x))
            #Repetition: RBNFRepetition
        }, normalise=normalise)
