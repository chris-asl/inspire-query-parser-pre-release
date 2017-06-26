from __future__ import unicode_literals, print_function
from pypeg2 import attr, Keyword, Literal, maybe_some, parse, omit, optional, re, word

import ast
from config import INSPIRE_PARSER_KEYWORDS


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
    regex = re.compile(r"(find|fin|f)\s", re.IGNORECASE)


class Fulltext(Keyword):
    regex = re.compile(r"fulltext", re.IGNORECASE)


class Reference(Keyword):
    regex = re.compile(r"reference", re.IGNORECASE)


class And(object):
    grammar = omit([
        re.compile(r"and\s", re.IGNORECASE),
        Literal('+'),
        Literal('&'),
    ])


class Or(object):
    grammar = omit([
        re.compile(r"or\s", re.IGNORECASE),
        Literal('|'),
    ])


class Not(object):
    grammar = omit([
        re.compile(r"not\s", re.IGNORECASE),
        Literal('-'),
    ])


class Range(object):
    grammar = omit(Literal("->"))
# ########################


# #### Leafs #####
class Qualifier(LeafRule):
    grammar = attr('value', re.compile(r"({0})\b".format("|".join(INSPIRE_PARSER_KEYWORDS))))


class NormalPhrase(LeafRule):
    grammar = attr('value', word)


class NormalPhraseSpanTail(LeafRule):
    grammar = [
        (omit(Range), attr('value', word)),
        attr('value', None)
    ]


class ExactPhrase(LeafRule):
    grammar = omit(Literal('"')), attr('value', word), omit(Literal('"'))


class ExactPhraseSpanTail(LeafRule):
    grammar = [
        (omit(Range), omit(Literal('"')), attr('value', word), omit(Literal('"'))),
        attr('value', None)
    ]


class PartialPhrase(LeafRule):
    grammar = omit(Literal("'")), attr('value', word), omit(Literal("'"))


class RegexPhrase(LeafRule):
    grammar = omit(Literal('/^')), attr('value', word), omit(Literal('$/'))


class Phrase(ListRule):
    grammar = [
        attr('children', (NormalPhrase, NormalPhraseSpanTail)),
        attr('children', (ExactPhrase, ExactPhraseSpanTail)),
        attr('children', PartialPhrase),
        attr('children', RegexPhrase),
    ]


class FulltextOp(UnaryRule):
    grammar = omit(Fulltext), omit(optional(':')), attr('op', NormalPhrase)


class ReferenceOp(UnaryRule):
    grammar = omit(Reference), omit(optional(':')), attr('op', [ExactPhrase, NormalPhrase])
########################


class QueryExpression(ListRule):
    pass


class TermExpressionWithoutColon(BinaryRule):
    grammar = attr('left', Qualifier), attr('right', Phrase)


class TermExpressionWithColon(BinaryRule):
    grammar = attr('left', Qualifier), omit(optional(':')), attr('right', Phrase)


class TermExpression(UnaryRule):
    grammar = attr(
        'op',
        [
            TermExpressionWithoutColon,
            TermExpressionWithColon,
            FulltextOp,
            ReferenceOp,
            Phrase,
        ]
    )


class AndQuery(UnaryRule):
    grammar = omit(And), attr('op', QueryExpression)


class OrQuery(UnaryRule):
    grammar = omit(Or), attr('op', QueryExpression)
# ########################


# #### Main productions ####
class NotQuery(UnaryRule):
    grammar = omit(Not), attr('op', QueryExpression)


class BooleanQuery(UnaryRule):
    grammar = [
        attr('op', AndQuery),
        attr('op', OrQuery)
    ]


class ParenthesizedQuery(UnaryRule):
    grammar = omit(Literal('(')), attr('op', QueryExpression), omit(Literal(')'))


class QueryExpressionTail(UnaryRule):
    pass


QueryExpression.grammar = [
    attr('children', (TermExpression, QueryExpressionTail)),
    attr('children', NotQuery),
    attr('children', ParenthesizedQuery),
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
    print(parse('find author "ellis"', StartRule))
    print(parse('find author ellis->zed', StartRule))
    print(parse('find author "ellis"->"zed"', StartRule))
    print(parse("author:ellis", StartRule))
    print(parse("author ellis and title 'boson'", StartRule))
    print(parse("author ellis and (title boson or (author /^xi$/ and title foo))", StartRule))
    print(parse("fulltext:boson", StartRule))
    print(parse("reference ellis", StartRule))
    print(parse('reference "Ellis"', StartRule))
    print(parse('ellis', StartRule))
    print(parse("'ellis'", StartRule))
