from ..grammar import *

# We don't need to define new classes for Concat, Group or Optional - the syntax is the same.


class ABNFDefList(DefList):

    def __init__(self, terms, separator='/'):
        super().__init__(terms, separator=separator)


class ABNFRule(Rule):

    def __init__(self, left, right, production='=', terminator=''):
        super().__init__(left, right, production=production, terminator=terminator)


class ABNFIncRule(Rule):

    def __init__(self, left, right, production='=/', terminator=''):
        super().__init__(left, right, production=production, terminator=terminator)


class ABNFTerminal(Terminal):

    def __init__(self, subject, left_bound='"', right_bound='"'):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class ABNFNonTerminal(NonTerminal):

    def __init__(self, subject, left_bound='', right_bound=''):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class ABNFRepetition(TernaryOperator):
    """ Model ABNF specific and variable repetition in one - this is possible because specific repetition
        is just a special case of variable repetition.
    """
    def __init__(self, subject, left='', right='', compact=True, operator1_sym='*', operator2_sym=''):
        if not (isinstance(left, int) or left == ''):
            raise GrammarException(f'{self.__class__.__name__} requires an integer or \'\' as its left argument.')
        if not (isinstance(right, int) or right == ''):
            raise GrammarException(f'{self.__class__.__name__} requires an integer or \'\' as its right argument.')
        if not issubclass(subject.__class__, Feature):
            raise GrammarException(f'{self.__class__.__name__} requires a Feature as its subject argument.')
        super().__init__(left, right, subject, operator1_sym, operator2_sym)
        self.compact = compact

    def __str__(self):
        if self.compact and self.left == self.middle:
            return f'{self.left}{self.right}'
        else:
            return super().__str__()


class ABNFChar(Terminal):

    def __init__(self, denom, subject, left_bound='', right_bound='', char_sym='%'):
        self.denom = denom
        self.char_sym = char_sym
        if not isinstance(subject, int):
            raise GrammarException(f'{self.__class__.__name__} must have an integer as the subject.')
        super().__init__(str(subject), left_bound=left_bound, right_bound=right_bound)

    def __str__(self):
        return f'{self.left_bound}{self.char_sym}{self.denom}{self.subject}{self.right_bound}'


class ABNFCharRange(BinaryOperator):

    def __init__(self, left, right, operator_sym='-'):
        if not issubclass(left.__class__, ABNFChar):
            raise GrammarException(f'{self.__class__.__name__} must have an ABNFChar as the left argument.')
        if not issubclass(right.__class__, ABNFChar):
            raise GrammarException(f'{self.__class__.__name__} must have an ABNFChar as the right argument.')
        super().__init__(left, right, operator_sym)

    def __str__(self):
        return f'{self.left}{self.operator_sym}{self.right.subject}'


# Will this being a Sequence cause equality issues?
class ABNFCharConcat(Sequence):
    pass


class ABNFComment(Symbol):

    def __init__(self, subject, left_bound=';', right_bound='\n'):
        super().__init__(subject, left_bound, right_bound)


class ABNF(Metalanguage):

    def __init__(self, ruleset, normalise=False):
        super().__init__(ruleset, syntax_dict={
            Concat: Concat,
            DefList: ABNFDefList,
            Rule: Rule,
            Terminal: ABNFTerminal,
            NonTerminal: ABNFNonTerminal,

            # Auxiliary
            Optional: Optional,
            Group: Group,
            Repetition: ABNFRepetition,
        }, normalise=normalise)
