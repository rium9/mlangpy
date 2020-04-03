""" A collection of objects for modelling various aspects of formal grammars.

"""

from typing import List
from pathlib import Path
import copy
import textwrap
from ordered_set import OrderedSet


# TODO this may have broken things!!
class Feature:

    def __add__(self, other):
        if not (issubclass(self.__class__, Feature) and issubclass(other.__class__, Feature)):
            raise NotImplemented

        return Sequence([
            self,
            other
        ])


class Symbol(Feature):
    """ An abstract concept of (terminal/non-terminal/variable/etc.) symbol. Should never be instantiated -
    two subclasses are provided, Terminal and NonTerminal, which should be used instead.

    Args:
        subject (str):      The textual content of the symbol.
        left_bound (str):   Mark the left boundary of the symbol - may be empty.
        right_bound (str):  Mark the right boundary of the symbol - may be empty.


    """

    def __init__(self, subject, left_bound='', right_bound=''):
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


class Terminal(Symbol):
    """ Subclass of Symbol that represents terminal symbols in a grammar. Defaults to BNF syntax. """

    def __init__(self, subject, left_bound='', right_bound=''):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class NonTerminal(Symbol):
    """ Subclass of Symbol that represents non-terminal symbols in a grammar. Defaults to BNF syntax. """

    def __init__(self, subject, left_bound='/', right_bound='/'):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class Bracket(Feature):
    """ Abstract representation of a
    """

    def __init__(self, subject, left_bound='', right_bound=''):
        self.subject = subject
        self.left_bound = left_bound
        self.right_bound = right_bound

    def __str__(self):
        return f'{self.left_bound}{self.subject}{self.right_bound}'

    def __eq__(self, other):
        return (issubclass(self.__class__, other.__class__) or issubclass(other.__class__, self.__class__)) and \
               self.subject == other.subject


class Optional(Bracket):

    def __init__(self, subject, left_bound='[', right_bound=']'):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class Group(Bracket):

    def __init__(self, subject, left_bound='(', right_bound=')'):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class Repetition(Bracket):

    def __init__(self, subject, left_bound='{', right_bound='}'):
        super().__init__(subject, left_bound=left_bound, right_bound=right_bound)


class BinaryOperator(Feature):

    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.operator = operator

    def __str__(self):
        return f'{self.left}{self.operator}{self.right}'


class Except(BinaryOperator):

    def __init__(self, left, right, operator='-'):
        super().__init__(left, right, operator)


class Sequence:

    def __init__(self, terms, separator=' '):
        # Sequence can be initialised:
        #   with any object - replaced with a list containing that object
        #   with a sequence object - its terms are copied over
        #   with a list of terms - no changes necessary, this is what we want.
        if not isinstance(terms, list):
            self.terms = [terms]
        elif issubclass(terms.__class__, self.__class__):
            self.terms = terms.terms
        else:
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


class Concat(Sequence):

    def __init__(self, terms, separator=' '):
        super().__init__(terms, separator)


class DefList(Sequence):

    def __init__(self, terms, separator='|'):
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

    def __init__(self, left, right, production='->',  terminator=''):

        # If left isn't a Sequence, make it one (of length 1)
        if not issubclass(left.__class__, Sequence):
            self.left = Sequence([left])
        else: self.left = left

        # If right is a list, use it to instantiate a DefinitionList,
        # If right isn't a list or a DefinitionList, put it in a Sequence on its own and use it to instantiate a DL,
        # If right is a DefinitionList, it's fine the way it is.
        if isinstance(right, list):
            self.right = DefinitionList(right)
        elif not issubclass(right.__class__, DefinitionList):
            self.right = DefinitionList([right])
        else:
            self.right = right

        self.prod = production
        self.terminator = terminator

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
               self.right == other.right

    __hash__ = object.__hash__


# TODO update to use OrderedSets or something
class Ruleset:
    """ A class representing a collection of Rule objects.

    Args:
        rules: A list-like object, specifically one that can be passed to OrderedSet.

    Attributes:
        rules (OrderedSet): The set of production rules in the Ruleset.

    """

    def __init__(self, rules):

        if isinstance(rules, list):
            self.rules = OrderedSet(rules)
        else:
            self.rules = rules

    def load_rules(self, rules):
        """ Load in a list of Rule objects.

        Args:
            rules (list of Rules): A list of Rule objects.

        """
        self.rules = rules

    def add_rule(self, rule):
        """ Add a new rule to the ruleset.

        Args:
            rule (Rule): The rule to be added to the Ruleset instance.
        """
        self.rules.append(rule)

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
                ret += r

        return ret

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
            if production != None:
                rule.prod = production
            if alternation != None:
                rule.alt = alternation
            if terminator != None:
                rule.right.ter = terminator

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

    def __add__(self, other) -> 'Ruleset':
        # Addition is only defined for Rulesets and Rules.
        if issubclass(other.__class__, Ruleset):
            return self.__class__(self.rules | other.rules)
        elif issubclass(other.__class__, Rule):
            if self.rule_exists(other):
                return self
            return self.__class__(self.rules | OrderedSet([other]))
        else:
            raise NotImplemented

    def __radd__(self, other):
        # Addition is only defined for Rulesets and Rules
        if issubclass(other.__class__, Ruleset):
            return self.__class__(other.rules | self.rules)
        elif issubclass(other.__class__, Rule):
            return self.__class__(OrderedSet([other]) | self.rules)
        else:
            raise NotImplemented


class Metalanguage:
    """ The Metalanguage class provides a base for representing various metalanguages.

    Attributes:
        ruleset (Ruleset):  A set of production rules.
        syntax (dict):      A number of syntax settings.
    """

    def __init__(self, ruleset, syntax_dict=None, normalise=True):
        """ Initialise a metalanguage with a ruleset and optionally a syntax dictionary. The syntax dictionary
        may be customised to change the form of specific features, e.g. to comply with a specification such
        as EBNF, ABNF or RBNF.

        Args:
            ruleset (Ruleset):  A Ruleset instance.
            syntax_dict:        A dictionary of syntax settings. Defaults are accessed by passing None.
            normalise:          Set to True to immediately attempt to normalise the Ruleset to correspond to syntax
                                settings.
        """
        self.ruleset = copy.deepcopy(ruleset)
        if not syntax_dict:
            self.syntax = {
                # Essential for all grammars
                Sequence: Sequence,
                DefinitionList: DefinitionList,
                Rule: Rule,
                Terminal: Terminal,
                NonTerminal: NonTerminal,

                # Auxiliary stuff
                Optional: Optional,
                Group: Group,
                Repetition: Repetition
            }
        else:
            self.syntax = syntax_dict

        self.op_count = 0
        self.rep_count = 0
        self.grp_count = 0

        if normalise: self.normalise()

    # TODO Method for automatically creating a lark file for recognising grammars using the current
    #       syntax of the Metalanguage instance. However, on its own the grammar won't be able to be
    #       used to generate a Ruleset instance since a Transformer subclass is needed, with method
    #       names corresponding to the lark file and non-terminal names. For this we need:
    #           a) a 'standard' for lark files, such that e.g. an EBNF grammar is a superset of
    #               a BNF grammar.
    #           b) a metaprogram that can, given information about a lark file, generate a Transformer
    #               subclass for said lark file.
    def build_lark_grammar(self):
        """ Create a lark file that will recognise grammars of the Metalanguage instance's syntax. """

        # Instantiate instances of syntax objects so we can see their notation
        nt = self.syntax[NonTerminal]('')
        t = self.syntax[Terminal]('')
        seq = self.syntax[Sequence]([])
        def_list = self.syntax[DefinitionList]([])

        rule = self.syntax[Rule]([], [])
        if rule.terminator.strip():
            terminator = rule.terminator
        else:
            terminator = '(" "|/' + '\t' + '/)'

        r = f'''
        syntax: syntax_rule+
        syntax_rule: non_terminal _PRODUCTION def_list " " ~ 1

        def_list: def (_ALTERNATE def)
        def: term (_CONCATENATE term)*

        term: non_terminal | terminal
        non_terminal: _NT_LEFT_BOUND WORD (" " WORD)* _NT_RIGHT_BOUND
        terminal: _T_LEFT_BOUND WORD _T_RIGHT_BOUND


        _PRODUCTION:        "{rule.prod}"
        _TERMINATOR:        "{terminator}"
        _ALTERNATE:         "{def_list.alt}"
        _CONCATENATE:       "{seq.separator}"
        _NT_LEFT_BOUND:     "{nt.left_bound}"
        _NT_RIGHT_BOUND:    "{nt.right_bound}"
        _T_LEFT_BOUND:      "{t.left_bound}"
        _T_RIGHT_BOUND:     "{t.right_bound}"

        %import common.WORD
        '''
        return textwrap.dedent(r)

    def export_lark_file(self, filename):
        f = open(filename, 'w')
        f.write(self.build_lark_grammar())

    def normalise(self):
        """ Convert the ruleset so that it complies with self.syntax. """

        # Instantiate an empty rule of the form stored in the syntax dictionary to access production, alternation
        # and termination symbols
        rf = self.syntax[Rule]([], [])

        # Update the form of rules
        self.ruleset.update_rules(production=rf.prod, alternation=rf.right.alt, terminator=rf.terminator)

        # Now, go through each rule (LHS and RHS) and transform features to their
        # corresponding notations in self.syntax

        # TODO implement dunder methods for Ruleset to make nicer iterations
        for rule in self.ruleset:

            # Handle left-hand side
            rule.left = self.syntax[Sequence](rule.left.terms)
            for i in range(0, len(rule.left)):
                for feature in self.syntax:
                    if isinstance(rule.left[i], feature):
                        rule.left[i] = self.syntax[feature](rule.left[i].subject)

            # Handle right-hand side
            for i in range(0, len(rule.right)):
                rule.right[i] = self.syntax[Sequence](rule.right[i].terms)
                for j in range(0, len(rule.right[i])):
                    rule.right[i][j] = self.normalise_term(rule.right[i][j])

    def export_ruleset(self, path):
        serialised_grammar = str(self.ruleset)
        f = open(path, 'w')
        f.write(serialised_grammar)

    def eliminate_optionals(self):

        # TODO implement dunder methods for Ruleset to make nicer iterations
        # Iterate over each rule
        for rule in self.ruleset:
            # Inspect each definition (Sequence) in the DefinitionList
            for definition in rule.right:
                # Check all members of the definition, formulate a new rule if necessary
                for i in range(0, len(definition)):
                    if isinstance(definition[i], Optional):
                        new_nt = NonTerminal(f'op {definition[i]}')

                        # New rule:
                        #   B -> a |
                        new_rule = self.syntax[Rule](
                            self.syntax[Sequence]([new_nt]),
                            self.syntax[DefinitionList]([
                                self.syntax[Sequence]([definition[i].subject]),
                                self.syntax[Sequence]([])
                            ])
                        )

                        # A -> B
                        definition[i] = new_nt

                        # Add new rule if necessary
                        # TODO This can be eliminated by using ordered sets
                        self.ruleset += new_rule

    def eliminate_repetition(self):
        for rule in self.ruleset:
            for definition in rule.right:
                for i in range(0, len(definition)):
                    if isinstance(definition[i], Repetition):
                        pass  # TODO

    def eliminate_groups(self):

        for rule in self.ruleset:
            for definition in rule.right:
                for i in range(0, len(definition)):
                    if issubclass(definition[i].__class__, Group):
                        new_nt = NonTerminal(f'grp {definition[i]}')

                        new_rule = self.syntax[Rule](
                            self.syntax[Sequence]([new_nt]),
                            self.syntax[DefinitionList]([
                                self.syntax[Sequence](definition[i].subject)
                            ])
                        )

                        definition[i] = new_nt
                        self.ruleset += new_rule

    def eliminate_alternation(self):
        # TODO implement dunder methods for Ruleset to make nicer iterations
        new_rules = OrderedSet()
        for rule in self.ruleset:
            for sequence in rule.right:
                new_rules |= {self.syntax[Rule](rule.left, self.syntax[DefinitionList]([sequence]))}

        self.ruleset.rules = new_rules

    def add_rule(self, rule):
        self.ruleset.add_rule(rule)

    def replace_feature(self, term, new_rule: Rule, name: NonTerminal):
        """ Create a new rule intended to replace an existing feature
                A ::= x term y  ->      A ::= x name y
                                        new_rule        (should be equivalent to language represented by term).
        """
        pass

    def remove_optionals_from_term(self, term, recursive=False):
        new_rules = OrderedSet()

        if issubclass(term.__class__, Optional):
            new_nt = NonTerminal(f'op {term.subject}')
            term = new_nt

        return term, new_rules

    def remove_optionals(self, rule):
        for definition in rule.right:
            for i in range(0, len(definition)):
                if issubclass(definition[i].__class__, Optional):

                    # check to see if there's a definition already
                    looking_for = Rule([], [definition[i].subject, []])
                    matching = None
                    for r in self.ruleset:
                        if r == looking_for:
                            matching = r

                    if matching:
                        definition[i] = matching.left[0]
                    else:
                        new_nt = NonTerminal(f'op {self.op_count}')
                        self.op_count += 1

                        new_rule = Rule(
                            new_nt,
                            [definition[i].subject,
                             []]
                        )

                        definition[i] = new_nt
                        self.ruleset += new_rule

    def remove_groups(self, rule):
        new_rules = Ruleset([rule])

        for definition in rule.right:
            for i in range(0, len(definition)):
                if issubclass(definition[i].__class__, Group):

                    # check to see if there's a definition already
                    looking_for = Rule([], [definition[i].subject, []])
                    matching = None
                    for r in new_rules:
                        if r == looking_for:
                            matching = r

                    if matching:
                        definition[i] = matching.left[0]
                    else:
                        new_nt = NonTerminal(f'grp {self.grp_count}')
                        self.grp_count += 1

                        new_rule = Rule(
                            new_nt,
                            [definition[i].subject]
                        )

                        definition[i] = new_nt
                        new_rules += new_rule

        return new_rules

    def test(self, rule):
        rule.right[0] = 'hi'


    def normalise_term(self, term):
        """ Recursively normalise a term and all of its sub-terms so that they abide by self.syntax.

        Args:
             term (Sequence/DefinitionList/Feature): The term to be normalised.
        """
        new_term = term
        for sy in self.syntax:
            if isinstance(term, sy):
                if isinstance(term, Sequence):
                    children = []
                    for t in term.terms:
                        children.append(self.normalise_term(t))

                    new_term = self.syntax[Sequence](children)
                elif isinstance(term, DefinitionList):
                    children = []
                    for t in term.definitions:
                        children.append(self.normalise_term(t))

                    new_term = self.syntax[DefinitionList](children)
                else:
                    new_term = self.syntax[sy](self.normalise_term(term.subject))

        return new_term


if __name__ == '__main__':
    a = Sequence([NonTerminal('a')])
    gr = Group(
        Sequence([
            DefList([
                Sequence([Terminal('b')]),
                Sequence([Terminal('c')])
            ]),
            Terminal('d')
        ])
    )

    r3 = Rule(
        NonTerminal('a'),
        [Terminal('b'),
         Terminal('c')]
    )
    print('r3:')
    print(r3)

    def1 = Sequence([
        gr,
        Terminal('e')
    ])

    def2 = Sequence([
        Terminal('f'),
        Terminal('g')
    ])

    r = Rule(
        a,
        DefinitionList([def1, def2])
    )

    r1 = Rule(
        Sequence('a'),
        DefList([
            Sequence(['b']),
            Optional(gr)
        ])
    )

    rs = Ruleset(OrderedSet([r1]))
    print(rs)
    print('========')
    print(rs)
    print('========')
    m = Metalanguage(rs, normalise=False)
    print('====unmodified grammar====')
    print(m.ruleset)
    print('====eliminating groups====')
    m.eliminate_groups()
    print(m.ruleset)
    print('====eliminating alternation====')
    m.eliminate_alternation()
    print(m.ruleset)
    print('====eliminating optionals====')
    m.eliminate_optionals()
    print(m.ruleset)
    print('====eliminating groups (again)====')
    m.eliminate_groups()
    print(m.ruleset)

    print(r1)
    b = m.remove_optionals(r1)
    print(b)

    x = m.ruleset[2]


    z = Concat([a, gr])
    y = Sequence([a, gr])
    x = DefList([a, gr])
    print(y == z)
    print(z == x)
    print(y == x)
    print(z)

    r4 = Rule(
        Sequence('a'),
        DefList([
            Sequence(['b']),
            Group(Optional(Optional(gr))),
            Optional(Optional(gr))
        ])
    )


    print('======')
    r4 = Rule(
        Sequence('a'),
        [
            Sequence(['b']),
            Group(Optional(Optional(gr))),
            Optional(Optional(gr))
        ]
    )
    m = Metalanguage(Ruleset([r4]))
    print(m.ruleset)