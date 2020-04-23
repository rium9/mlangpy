""" A collection of objects for modelling various aspects of formal grammars.

"""

from typing import List
from pathlib import Path
import copy
import textwrap
from ordered_set import OrderedSet


class GrammarException(Exception):
    pass


# TODO this may have broken things!!
class Feature:

    def __add__(self, other):
        if not (issubclass(self.__class__, Feature) and issubclass(other.__class__, Feature)):
            raise NotImplemented

        return Sequence([
            self,
            other
        ])


class Operator(Feature):

    def __init__(self, subject, operator_sym, prepend=False):
        if not issubclass(subject.__class__, Feature):
            raise GrammarException(f'{self.__class__.__name__} objects require a Feature object as the subject.')
        self.subject = subject
        self.operator_sym = operator_sym
        self.prepend = prepend

    def __str__(self):
        if self.prepend:
            return f'{self.operator_sym}{self.subject}'
        else:
            return f'{self.subject}{self.operator_sym}'

    def __eq__(self, other):
        return (issubclass(self.__class__, other.__class__) or issubclass(other.__class__, self.__class__)) and \
            self.subject == other.subject


class BinaryOperator(Feature):

    def __init__(self, left, right, operator_sym):
        self.left = left
        self.right = right
        self.operator_sym = operator_sym

    def __str__(self):
        return f'{self.left}{self.operator_sym}{self.right}'


class TernaryOperator(Feature):

    def __init__(self, left, middle, right, operator1_sym, operator2_sym):
        self.left = left
        self.middle = middle
        self.right = right

        assert isinstance(operator1_sym, str) and isinstance(operator2_sym, str)
        self.operator1_sym = operator1_sym
        self.operator2_sym = operator2_sym

    def __str__(self):
        return f'{self.left}{self.operator1_sym}{self.middle}{self.operator2_sym}{self.right}'


class Bracket(Feature):
    """
    Abstract representation of a feature that can encompass more than one term.
    """

    def __init__(self, subject, left_bound, right_bound):
        if not issubclass(subject.__class__, Concat) and not issubclass(subject.__class__, DefList):
            raise GrammarException(f'{self.__class__.__name__} objects require a Concat or DefList as the subject.')

        self.subject = subject

        assert isinstance(left_bound, str) and isinstance(right_bound, str)
        self.left_bound = left_bound
        self.right_bound = right_bound

    def __str__(self):
        return f'{self.left_bound}{self.subject}{self.right_bound}'

    def __eq__(self, other):
        return (issubclass(self.__class__, other.__class__) or issubclass(other.__class__, self.__class__)) and \
               self.subject == other.subject

    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.subject)})'

class Symbol(Feature):
    """ An abstract concept of (terminal/non-terminal/variable/etc.) symbol. Should never be instantiated -
    two subclasses are provided, Terminal and NonTerminal, which should be used instead.

    Args:
        subject (str):      The textual content of the symbol.
        left_bound (str):   Mark the left boundary of the symbol - may be empty.
        right_bound (str):  Mark the right boundary of the symbol - may be empty.


    """

    def __init__(self, subject, left_bound='', right_bound=''):
        assert isinstance(left_bound, str) and isinstance(right_bound, str)
        self.subject = subject
        self.left_bound = left_bound
        self.right_bound = right_bound

    def __str__(self):
        """
        Returns:
            Left boundary followed by subject followed by right boundary.

        """
        return f'{self.left_bound}{self.subject}{self.right_bound}'

    def __eq__(self, other):
        """ Equality between symbols relies on the subject of the symbol, as well their position in the class hierarchy
        - a NonTerminal may be equal to a Symbol (child-parent), but a NonTerminal and a Terminal can never be equal
        (siblings). Boundary symbols are inconsequential to equality.

        Args:
            other: The object to be tested for equality.

        Returns:
            True if either is a descendant of the other, and both have the same subjects.
        """
        return (issubclass(self.__class__, other.__class__) or issubclass(other.__class__, self.__class__)) and \
               self.subject == other.subject

    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.subject)})'


class Terminal(Symbol):
    """ Subclass of Symbol that represents terminal symbols in a grammar. Defaults to BNF syntax. """

    def __init__(self, subject, left_bound='', right_bound=''):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class NonTerminal(Symbol):
    """ Subclass of Symbol that represents non-terminal symbols in a grammar. Defaults to BNF syntax. """

    def __init__(self, subject, left_bound='/', right_bound='/'):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class Optional(Bracket):

    def __init__(self, subject, left_bound='[', right_bound=']'):
        if isinstance(subject, list):
            subject = Concat(subject)
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class Group(Bracket):

    def __init__(self, subject, left_bound='(', right_bound=')'):
        if isinstance(subject, list):
            subject = Concat(subject)
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class Repetition(Bracket):

    def __init__(self, subject, left_bound='{', right_bound='}'):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class Except(BinaryOperator):

    def __init__(self, left, right, operator='-'):
        super().__init__(left, right, operator)


class Sequence:
    """ Abstract representation of a sequence of Features. """

    def __init__(self, terms, separator=' '):
        # Sequence can be initialised:
        #   with any object - replaced with a list containing that object
        #   with a sequence object - its terms are copied over
        #   with a list of terms - no changes necessary, this is what we want.

        if not isinstance(terms, list):
            raise GrammarException(f'{self.__class__.__name__} can only be instantiated with a list of terms.')

        self.terms = terms
        self.separator = separator

    def __str__(self):
        return self.separator.join([str(term) for term in self.terms])

    def __eq__(self, other):
        """ Two sequences are equal if all of their terms are equal. """
        if not (issubclass(other.__class__, self.__class__) or issubclass(self.__class__, other.__class__)):
            return False

        if len(self.terms) != len(other.terms):
            return False

        try:
            for i in range(0, len(self.terms)):
                if self.terms[i] != other.terms[i]:
                    return False

            return True

        except IndexError:
            return False

    def __getitem__(self, index):
        return self.terms[index]

    def __setitem__(self, index, value):
        self.terms[index] = value

    def __len__(self):
        return len(self.terms)

    def __add__(self, other):
        if issubclass(other.__class__, self.__class__):
            return self.__class__(self.terms + other.terms)
        return self.__class__(self.terms + [other])

    def __radd__(self, other):
        if issubclass(other.__class__, self.__class__):
            return self.__class__(other.terms + self.terms)
        return self.__class__([other] + self.terms)

    def __iadd__(self, other):
        if issubclass(other.__class__, Sequence):
            self.terms += other.terms
        else:
            self.terms.append(other)

        return self

    def __repr__(self):
        r = f'{self.__class__.__name__}'
        terms = ', '.join([repr(term) for term in self.terms])
        return f'{r}({terms})'

class Concat(Sequence):

    def __init__(self, terms, separator=' '):
        if not isinstance(terms, list):
            #if not issubclass(terms.__class__, Feature):
            #    raise GrammarException(f'{self.__class__.__name__} objects may only contain Feature or DefList objects.')
            self.terms = [terms]
        elif issubclass(terms.__class__, self.__class__):
            self.terms = terms.terms
        else:
            #for term in terms:
            #    if not issubclass(term.__class__, Feature):
            #        raise GrammarException(
            #            f'Lists used to instantiate {self.__class__.__name__} objects must only contain Feature or DefList objects.'
            #        )

            self.terms = terms

        self.separator = separator


class DefList(Sequence):

    def __init__(self, terms, separator='|'):
        for term in terms:
            if not issubclass(term.__class__, Concat):
                raise GrammarException(f'{self.__class__.__name__} requires that all terms be Concat instances.')
        super().__init__(terms, separator=separator)

    def __str__(self):
        """ Override Sequence __str__ to ensure nice spacing. """
        return f' {self.separator} '.join(str(term) for term in self.terms)


class DefinitionList:
    """ Represents a sequence of definitions A | B | ... | M.

    Args:
        definitions (:obj:`list` of Sequence): A list of Sequence objects.
            Any non-Sequence objects will be put into their own Sequence instance.

        alternation (str): Symbol to use for alternation in string representation.

    Attributes:
        definitions: A list of Sequences corresponding to individual definitions (A, B, ... M).
        alternation: The syntax to be used for string representations of the DefinitionList instance.
    """

    def __init__(self, definitions, alternation='|'):
        defs = []

        # All definitions must be of type Sequence - convert non-Sequences to Sequences of length 1
        for definition in definitions:
            if not issubclass(definition.__class__, Sequence):
                defs.append(Sequence(definition))
            else:
                defs.append(definition)

        # Sanity check
        for d in defs:
            assert issubclass(d.__class__, Sequence)

        self.definitions = defs
        self.alt = alternation

    def __str__(self):
        return f' {self.alt} '.join([str(sequence) for sequence in self.definitions])

    def __eq__(self, other):
        """ Two DefinitionLists are considered equal if they both contain the same elements.

        Returns:
            True if one is a descendant class of the other, and the elements of each are equal.

        """
        if not (issubclass(self.__class__, other.__class__) or issubclass(other.__class__, self.__class__)):
            return False

        if len(self.definitions) != len(other.definitions):
            return False

        try:
            for i in range(0, len(self.definitions)):
                if self.definitions[i] != other.definitions[i]:
                    return False

            return True

        except IndexError:
            return False

    def __getitem__(self, index: int):
        return self.definitions[index]

    def __setitem__(self, index: int, value):
        self.definitions[index] = value

    def __len__(self):
        return len(self.definitions)


class Rule:
    """ A representation of a production rule.

    Args:
        left: A Feature or Sequence of Features, corresponding to the left-hand side of a production rule.
        right: A list or DefinitionList containing Sequence instances.
        production: The symbol to be used to indicate production.
        terminator: The symbol to be used to indicate rule termination.

    Attributes:
        left (Sequence): A Sequence object corresponding to the LHS of the rule.

        right (DefinitionList): A DefinitionList object corresponding to the RHS of the rule.

        prod (str): The symbol used to denote the production operator. Defaults to '->'.

        terminator (str): The symbol used to denote the terminator symbol. Defaults to ''.

    """

    def __init__(self, left, right, production='->', terminator=''):

        # If left isn't a Sequence, make it one (of length 1)
        if not issubclass(left.__class__, Sequence):
            self.left = Sequence([left])
        else: self.left = left

        # If right is a list, use it to instantiate a DefinitionList,
        # If right isn't a list or a DefinitionList, put it in a Sequence on its own and use it to instantiate a DL,
        # If right is a DefinitionList, it's fine the way it is.
        if isinstance(right, list):
            self.right = DefList(right)
        elif not issubclass(right.__class__, DefList):
            self.right = DefList([right])
        else:
            self.right = right

        self.prod = production
        self.terminator = terminator

    def is_equivalent_to(self, other):
        return self.right == other.right

    def __str__(self):
        """
        Returns:
            A string representation of the rule using its assigned syntax.
        """
        return f'{self.left} {self.prod} {self.right} {self.terminator}'

    # EXPERIMENTAL consider differently named rules equal
    def __eq__(self, other):
        """ Rules are equal modulo any syntactic differences. """
        return (issubclass(self.__class__, other.__class__) or issubclass(other.__class__, self.__class__)) and \
               self.left == other.left and self.right == other.right

    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.left)}, {repr(self.right)})'

class Ruleset:
    """ A class representing a collection of Rule objects.

    Args:
        rules: A list-like object, specifically one that can be passed to OrderedSet.

    Attributes:
        rules (OrderedSet): The set of production rules in the Ruleset.

    """

    def __init__(self, rules):
        for rule in rules:
            if not issubclass(rule.__class__, Rule):
                raise GrammarException(
                    'A Ruleset requires a list-like object containing only Rule instances as its rules paramater.'
                )

        self.rules = list(rules)

    def find_rules(self, rule):
        """ Returns rules equal to the one provided. See Rule __eq__ for equality check.
        Args:
            rule: The rule to search for.

        Returns:
            A list of matching rules.
        """
        ret = []
        for r in self.rules:
            if r == rule:
                ret.append(r)

        return ret

    def find_rules_for(self, def_list):
        """ Returns rules whose right-hand side is equal to def_list.

        Args:
            def_list: The definition list to find rules for.
        """
        if not issubclass(def_list.__class__, DefList):
            raise GrammarException('The right-hand side of a rule must be a DefList.')

        return [rule for rule in self.rules if rule.right == def_list]

    def rule_exists(self, new_rule):
        """ Returns True if new_rule already exists in the ruleset.

        Args:
            new_rule (Rule): The rule to be checked.
        """
        for rule in self.rules:
            if rule == new_rule:
                return True
        return False

    def update_rules(self, production=None, alternation=None, terminator=None):
        """ Update the production, alternation and terminator syntax for all Rules in the Ruleset. Syntax will not
        be updated unless values are provided for the keyword parameters.

        Args:
            production:     New production operator syntax.
            alternation:    New alternation operator syntax.
            terminator:     New terminator symbol.

        """
        for rule in self.rules:
            if production:
                rule.prod = production
            if alternation:
                rule.right.alt = alternation
            if terminator:
                rule.terminator = terminator

    def __str__(self):
        return '\n'.join(str(rule) for rule in self.rules)

    def __eq__(self, other: 'Ruleset') -> bool:
        """ Two Rulesets are deemed equal if they contain exactly the same Rules.

        Args:
            other: Other Ruleset instance to be evaluated for equality.

        Returns:
            True if Rulesets are equal, False otherwise.
        """
        if len(self.rules) != len(other.rules):
            return False

        for i in range(0, len(self.rules)):
            if self.rules[i] != other.rules[i]:
                return False

        return True

    def __len__(self):
        """ The length of a Ruleset object is the length of its collection of Rules. """
        return len(self.rules)

    def __getitem__(self, index: int):
        return self.rules[index]

    def __setitem__(self, index: int, value):
        self.rules[index] = value

    def __add__(self, other):
        # Addition is only defined for Rulesets and Rules.
        if issubclass(other.__class__, Ruleset):
            return self.__class__(self.rules + other.rules)
        elif issubclass(other.__class__, Rule):
            return self.__class__(self.rules + [other])
        else:
            raise NotImplemented

    def __radd__(self, other):
        # Addition is only defined for Rulesets and Rules
        if issubclass(other.__class__, Ruleset):
            return self.__class__(other.rules + self.rules)
        elif issubclass(other.__class__, Rule):
            return self.__class__([other] + self.rules)
        else:
            raise NotImplemented
