from ..grammar import *


class EBNFTerminal(Terminal):

    def __init__(self, subject, left_bound='"', right_bound='"'):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class EBNFDefinitionList(DefinitionList):

    def __init__(self, definitions, alternation='|'):
        super().__init__(definitions, alternation=alternation)


class EBNFNonTerminal(NonTerminal):

    def __init__(self, subject, left_bound='', right_bound=''):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class EBNFSequence(Sequence):

    def __init__(self, terms, separator=', '):
        super().__init__(terms, separator=separator)


class EBNFRule(Rule):

    def __init__(self, left, right, production='=', terminator=';'):
        super().__init__(left, right, production=production, terminator=terminator)


class EBNFRepetition(Repetition):

    def __init__(self, subject, left_bound='{', right_bound='}'):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class EBNFSpecialSequence(Bracket):

    def __init__(self, subject, left_bound='?', right_bound='?'):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class EBNF(Metalanguage):

    def __init__(self, ruleset: Ruleset, normalise=False):
        super().__init__(ruleset, syntax_dict={
                # Core
                Sequence: EBNFSequence,
                DefinitionList: EBNFDefinitionList,
                Rule: EBNFRule,
                Terminal: EBNFTerminal,
                NonTerminal: EBNFNonTerminal,

                # Auxiliary
                Optional: Optional,
                Group: Group,
                Repetition: EBNFRepetition,

                # Additional
                Except: Except
            }, normalise=normalise)