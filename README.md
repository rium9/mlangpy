# mlangpy

A collection of tools for parsing, building and manipulating metalanguages.

## Getting started

### Prerequisites

This tool requires Python v3.6+.

### Installation

Currently, mlangpy depends on `ordered-sets` (to be removed) and `lark-parser`.

```
pip install ordered-sets
pip install lark-parser
```

Install mlangpy:

```
pip install mlangpy
```


`mlangpy` relies entirely on [Lark](https://github.com/lark-parser/lark "Lark parser") for its parsing facilities, so it's recommended that you familiarise yourself with the Lark parser. 

## Usages

### Validate Metalanguages 

Currently, mlangpy supports recognition of EBNF ([ISO/IEC 14977](https://www.cl.cam.ac.uk/~mgk25/iso-14977.pdf)) and ABNF ([RFC 5234](https://tools.ietf.org/html/rfc5234)). You can generate parse trees for grammars using `metaparsers.py`:

```
from mlangpy.metaparsers import validate_ABNF, validate_ABNF_faithful, validate_EBNF

v = validate_ABNF('a = %x100-110 ["hi"] \n')
print(v.pretty())

# Notice this parse tree is a lot longer and more awkward to work with.
y = validate_ABNF_faithful('a = %x100-110 ["hi"] \n')
print(y.pretty())

z = validate_EBNF('''
  if clause = "if", Boolean expression, "then" ;
  Boolean expression = 'True' | 'False' ;
''')
print(z.pretty())
```


### Model grammars and grammatical features, independent of syntax

`mlangpy` includes classes for modelling all aspects of a grammars, from (non-)terminal symbols up to entire rules, with
support for defining custom operators and brackets, in `grammar.py`.

#### Class hierarchy
![Feature class diagram](./images/class_diagram.png)

In short,
* A `DefList` contains 0+ `Concat` instances,
* A `Concat` contains 0+ `Feature` instances,
* A `Symbol` is a string/char corresponding to a string literal,
* A `Bracket` surrounds either a `DefList` or a `Concat`,
* An `Operator` is applied to a **single** `Feature`,
* A `BinaryOperator` is applied to **two** `Feature` instances,
* A `TernaryOperator` is applied to **three** `Feature` instances.

Some implicit consequences of these limitations:
* Precedence has to be made explicit for operators (i.e. via bracketing) since
they won't accept `Concat` or `DefList` instances as arguments.

Building a rule:
```
from mlangpy.grammar import NonTerminal, Terminal, Rule, Concat, \
    Optional, Ruleset, Metalanguage

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
print(r)    # /name/ -> [A] dog
```

Inspecting a rule:
```
print(r.left)        # /name/
print(r.right)       # [A] dog (The DefList)
print(r.right[0])    # [A] dog (The first Concat in the DefList)
print(r.right[0][0]) # [A]     (The first Feature in the Concat)
```

Loading rules into a metalanguage instance:
```
ruleset = Ruleset([r])
m = Metalanguage(ruleset)
print(m.ruleset)    # /name/ -> [A] dog
```

Swap to a different syntax:
```
from mlangpy.metalanguages.EBNF import EBNFRule, EBNFNonTerminal

class MyTerminal(Terminal):
    def __init__(self, subject):
        super().__init__(subject, left_bound='"', right_bound='"')

m.syntax[Rule] = EBNFRule
m.syntax[NonTerminal] = EBNFNonTerminal
m.syntax[Terminal] = MyTerminal
m.normalise()

print(m.ruleset)    # name = ["A"] "dog" ;
```
Classes are given for the parts of some standard metalanguages in `mlangpy.metalanguages`.

### Generate grammar models from actual syntax
Writing grammars this way in a Python file is more cumbersome than actually just writing grammars normally.
Using the Lark parser, grammars can be passed as strings and a `Ruleset` or `Metalanguage` object can be generated. 
`metaparsers.py` shows how Lark `Transformer` subclasses can be used to convert serialised grammars to objects we
can work with.

`TODO`