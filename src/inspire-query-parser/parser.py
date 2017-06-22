from __future__ import unicode_literals, print_function
from pypeg2 import attr, Keyword, Literal, maybe_some, parse, omit, optional, re, word

import ast


class LeafRule(ast.Leaf):
    def __init__(self):
        pass


class UnaryRule(ast.UnaryOp):
    def __init__(self):
        pass


class BinaryRule(ast.BinaryOp):
    def __init__(self):
        pass


class ListRule(ast.ListOp):
    def __init__(self):
        pass
# ########################


# #### Keywords ####
class Find(Keyword):
    regex = re.compile(r"(find|fin|f)", re.IGNORECASE)


class And(object):
    grammar = omit([
        re.compile(r"and", re.IGNORECASE),
        Literal('+'),
    ])


class Or(object):
    grammar = omit([
        re.compile(r"or", re.IGNORECASE),
        Literal('|'),
    ])
# ########################


# #### Leafs #####
class InspireCategory(LeafRule):
    grammar = attr('value', word)


class Phrase(UnaryRule):
    grammar = attr('op', word)
# ########################


class QueryExpression(ListRule):
    pass


class TermExpressionWithoutColon(BinaryRule):
    grammar = attr('left', InspireCategory), attr('right', Phrase)


class TermExpressionWithColon(BinaryRule):
    grammar = attr('left', InspireCategory), omit(optional(':')), attr('right', Phrase)


class TermExpression(UnaryRule):
    grammar = attr(
        'op',
        [
            TermExpressionWithoutColon,
            TermExpressionWithColon
        ]
    )


class AndQuery(UnaryRule):
    grammar = omit(And), attr('op', QueryExpression)


class OrQuery(UnaryRule):
    grammar = omit(Or), attr('op', QueryExpression)
# ########################


# #### Main productions ####
class BooleanQuery(UnaryRule):
    grammar = [
        attr('op', AndQuery),
        attr('op', OrQuery)
    ]


class QueryExpressionTail(UnaryRule):
    pass


QueryExpression.grammar = [
    attr('children', (TermExpression, QueryExpressionTail))
]


QueryExpressionTail.grammar = [
    attr('op', BooleanQuery),
    attr('op', None)
]


class StartRule(UnaryRule):
    grammar = [
        (omit(Find), attr('op', QueryExpression)),
        attr('op', QueryExpression)
    ]
# ########################


if __name__ == '__main__':
    print(parse("find author ellis", StartRule))
    print(parse("author:ellis", StartRule))
    print(parse("author ellis and title boson", StartRule))
    print(parse("author ellis OR title boson", StartRule))
