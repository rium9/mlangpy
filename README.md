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

`mlangpy` relies entirely on [Lark](https://github.com/lark-parser/lark "Lark parser") for its parsing facilities, so it's recommended that you familiarise yourself with the Lark parser. 
