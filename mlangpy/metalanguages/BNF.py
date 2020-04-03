from ..grammar import *


class BNFRule(Rule):

    def __init__(self, left, right, production='::=', terminator=''):
        super().__init__(left, right, production=production, terminator=terminator)


class BNFTerminal(Terminal):

    def __init__(self, subject):
        super().__init__(subject, left_bound='', right_bound='')


class BNFNonTerminal(NonTerminal):

    def __init__(self, subject):
        super().__init__(subject, left_bound='<', right_bound='>')