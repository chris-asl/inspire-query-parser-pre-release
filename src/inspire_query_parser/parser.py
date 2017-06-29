from __future__ import unicode_literals, print_function
from pypeg2 import attr, Keyword, Literal, parse, omit, optional, re, Symbol, word, K, Enum, contiguous, some, \
    maybe_some

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
    keyword = "find"
    regex = re.compile(
        r"({0})\s".format("|".join([keyword[:i] for i in range(len(keyword) + 1, 0, -1)])),
        re.IGNORECASE)
    grammar = Enum(
        K("find"), K("FIND"),
        *[k for i in range(1, len(keyword) + 1) for k in (K(keyword[:i] + " "), K(keyword[:i].upper() + " "))])


class Fulltext(Keyword):
    regex = re.compile(r"fulltext", re.IGNORECASE)
    grammar = Enum(K("fulltext"), K("FULLTEXT"))


class Reference(Keyword):
    regex = re.compile(r"reference", re.IGNORECASE)
    grammar = Enum(K("reference"))


class And(Keyword):
    regex = re.compile(r"(and|\+|&)", re.IGNORECASE)
    grammar = Enum(K("and"), K("AND"), "+", "&")


class Or(Keyword):
    regex = re.compile(r"(or|\|)", re.IGNORECASE)
    grammar = Enum(K("or"), K("OR"), "|")


class Not(Keyword):
    regex = re.compile(r"(not|-)", re.IGNORECASE)
    grammar = Enum(K("not"), K("NOT"), "-")


class Range(object):
    grammar = omit(Literal("->"))
# ########################


# #### Leafs #####
class Qualifier(LeafRule):
    grammar = attr('value', re.compile(r"({0})\b".format("|".join(INSPIRE_PARSER_KEYWORDS))))


class Terminal(LeafRule):
    Symbol.check_keywords = True
    Symbol.regex = re.compile(r"(\w+([-/]\w+)*)")
    grammar = attr('value', Symbol), maybe_some([" ", ",", "."])


class TerminalTail(UnaryRule):
    pass


class Terminals(ListRule):
    grammar = contiguous(attr('children', (Terminal, TerminalTail)))


TerminalTail.grammar = attr('op', [Terminals, None])


class NormalPhrase(UnaryRule):
    grammar = attr('op', Terminals)


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
    # TODO refactor to have the list rule after ONE attr('children',[...])
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
        attr('op', QueryExpression),
    ]
# ########################


if __name__ == '__main__':
    # Find keyword combined with other production rules
    # print(parse('find author "ellis"', StartRule))
    # print(parse("FIN author:'ellis'", StartRule))
    # print(parse('f author ellis', StartRule))

    # Invenio like search
    # print(parse("author:ellis", StartRule))

    # Boolean
    # print(parse("author ellis and title 'boson'", StartRule))
    # print(parse("author ellis AND title boson", StartRule))
    # print(parse("author ellis | title 'boson'", StartRule))
    # print(parse("author ellis OR title 'boson'", StartRule))
    # print(parse("author ellis + title 'boson'", StartRule))
    # print(parse("author ellis & title 'boson'", StartRule))

    # Negation
    # print(parse("author ellis and not title 'boson'", StartRule))
    # print(parse("author ellis and not title boson", StartRule))
    # print(parse("-title 'boson'", StartRule))

    # Nested expressions
    # print(parse("author ellis and (title boson or (author /^xi$/ and title foo))", StartRule))

    # Metadata search
    # print(parse("fulltext:boson", StartRule))
    # print(parse("reference ellis", StartRule))
    # print(parse('reference "Ellis"', StartRule))

    # Only phrases
    # print(parse('ellis', StartRule))
    # print(parse("'ellis'", StartRule))

    # Non trivial terminals
    # print(parse("find Higgs boson", StartRule))
    # print(parse("author ellis, j.", StartRule))
    # print(parse("author j., ellis", StartRule))
    print(parse("f title Super Collider Physics", StartRule))
    # print(parse("find title Alternative the Phase-II upgrade of the ATLAS Inner Detector", StartRule))
    # print(parse("find title na61/shine", StartRule))
    print(parse("title foo and author abtrall", StartRule))
    # print(parse("title e-10", StartRule))
    # print(parse("title e,10 and author ellis", StartRule))
