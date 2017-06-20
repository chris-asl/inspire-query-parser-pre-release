from __future__ import unicode_literals, print_function
from pypeg2 import attr, maybe_some, parse, omit, optional, re, word

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


class FindOp(LeafRule):
    grammar = attr('value', re.compile("find", re.IGNORECASE))


class InspireCategory(LeafRule):
    grammar = attr('value', word)


class Phrase(UnaryRule):
    grammar = attr('op', word)


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


class QueryExpressionTail(UnaryRule):
    pass


class QueryExpression(ListRule):
    grammar = [
        attr('children', [TermExpression, QueryExpressionTail])
    ]


QueryExpressionTail.grammar = [
    attr('op', QueryExpression),
    attr('op', None)
]


class StartRule(UnaryRule):
    grammar = omit(optional(FindOp)), attr('op', QueryExpression)


if __name__ == '__main__':
    print(parse("find author ellis", StartRule))
    print(parse("author:ellis", StartRule))
    # print(parse("author ellis title Boson", StartRule))
