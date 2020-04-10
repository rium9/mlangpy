from mlangpy.grammar import NonTerminal, Terminal, Rule, Concat, \
    Optional, Ruleset, DefList
from mlangpy.metalanguages import EBNFRule, EBNFNonTerminal, Metalanguage

if __name__ == '__main__':
    # ==================Building a rule================
    n = NonTerminal('name')
    t1 = Terminal('A')
    t2 = Terminal('dog')
    o = Optional(Concat([t1]))

    r = Rule(
        n,
        Concat([
            o, t2
        ])
    )
    print(r)  # /name/ -> [A] dog

    # ================Inspecting a rule===============
    print(r.left)  # /name/
    print(r.right)  # [A] dog (The DefList)
    print(r.right[0])  # [A] dog (The first Concat in the DefList)
    print(r.right[0][0])  # [A]     (The first Feature in the Concat)

    # ===Loading rules into a metalanguage instance===
    ruleset = Ruleset([r])
    m = Metalanguage(ruleset)
    print(m.ruleset)  # /name/ -> [A] dog

    r2 = Rule(
        NonTerminal('x'),
        [Concat(t1), Concat(t2)]
    )
    print(r2)  # /x/ -> A | dog
    m.ruleset += r2
    print(m.ruleset)  # /name/ -> [A] dog
    # /x/ -> A | dog

    class MyTerminal(Terminal):
        def __init__(self, subject):
            super().__init__(subject, left_bound='"', right_bound='"')

    m.syntax[Rule] = EBNFRule
    m.syntax[NonTerminal] = EBNFNonTerminal
    m.syntax[Terminal] = MyTerminal
    m.normalise()
    print(m.ruleset)
