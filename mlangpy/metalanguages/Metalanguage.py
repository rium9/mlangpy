from mlangpy.grammar import *


class Metalanguage:
    """ The Metalanguage class provides a base for representing various metalanguages.

    Attributes:
        ruleset (Ruleset):  A set of production rules.
        syntax (dict):      A number of syntax settings.
    """

    def __init__(self, ruleset, syntax_dict=None, normalise=False):
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
                Concat: Concat,
                DefList: DefList,
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
        self.ruleset.update_rules(production=rf.prod, alternation=rf.right.separator, terminator=rf.terminator)

        # Now, go through each rule (LHS and RHS) and transform features to their
        # corresponding notations in self.syntax

        for rule in self.ruleset:

            # Handle left-hand side
            rule.left = self.syntax[Concat](rule.left.terms)
            for i in range(0, len(rule.left)):
                for feature in self.syntax:
                    if isinstance(rule.left[i], feature):
                        rule.left[i] = self.syntax[feature](rule.left[i].subject)

            # Handle right-hand side
            for i in range(0, len(rule.right)):
                rule.right[i] = self.syntax[Concat](rule.right[i].terms)
                for j in range(0, len(rule.right[i])):
                    rule.right[i][j] = self.normalise_term(rule.right[i][j])

    def normalise2(self):
        rf = self.syntax[Rule]([], [])
        self.ruleset.update_rules(production=rf.prod, alternation=rf.right.separator, terminator=rf.terminator)

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
                    matching = self.ruleset.find_rules(looking_for)

                    if matching:
                        definition[i] = matching[0].left[0]
                    else:
                        new_nt = self.syntax[NonTerminal](f'op {self.op_count}')
                        self.op_count += 1

                        new_rule = self.syntax[Rule](
                            new_nt,
                            [definition[i].subject,
                             []]
                        )

                        definition[i] = new_nt
                        self.ruleset += new_rule

    def remove_groups_from(self, rule):
        new_rules = []

        for concat in rule.right:
            for i in range(0, len(concat)):
                if issubclass(concat[i].__class__, Group):

                    # check to see if there's a definition already
                    looking_for = DefList([concat[i].subject])
                    matching = self.ruleset.find_rules_for(looking_for)

                    if matching:
                        concat[i] = matching[0].left[0]
                    else:
                        new_nt = self.syntax[NonTerminal](f'grp {self.grp_count}')
                        self.rep_count += 1

                        new_rule = self.syntax[Rule](
                            new_nt,
                            [concat[i].subject]
                        )

                        new_rules.append(new_rule)

        return new_rules

    def remove_repetitions(self, rule):

        for definition in rule.right:
            for i in range(0, len(definition)):
                if issubclass(definition[i].__class__, Repetition):

                    # check to see if there's a definition already
                    looking_for = Rule([], [definition[i].subject, []])
                    matching = self.ruleset.find_rules(looking_for)

                    if matching:
                        definition[i] = matching[0].left[0]
                        continue

                    new_nt = self.syntax[NonTerminal](f'rep {self.rep_count}')
                    self.rep_count += 1

                    new_rule = self.syntax[Rule](
                        new_nt,
                        [[definition[i].subject, new_nt], []]
                    )

                    definition[i] = new_nt
                    self.ruleset += new_rule

    def test(self, rule):
        rule.right[0] = 'hi'

    def normalise_term(self, term):

        new_term = term
        for sy in self.syntax:
            if issubclass(term.__class__, sy):
                if issubclass(term.__class__, Concat) or issubclass(term.__class__, DefList):
                    children = []
                    for t in term.terms:
                        children.append(self.normalise_term(t))

                    new_term = self.syntax[sy](children)

                else:
                    new_term = self.syntax[sy](self.normalise_term(term.subject))

        return new_term