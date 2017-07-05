from __future__ import unicode_literals, print_function

from pypeg2 import attr, Keyword, Literal, parse, omit, optional, re, Symbol, word, K, Enum, contiguous, maybe_some

from . import ast
from .config import INSPIRE_PARSER_KEYWORDS


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


class ExactAuthor(Keyword):
    regex = re.compile(r"exactauthor", re.IGNORECASE)
    grammar = Enum(K("exactauthor"), K("EXACTAURTHOR"))


class AuthorCount(Keyword):
    regex = re.compile(r"authorcount", re.IGNORECASE)
    grammar = Enum(K("authorcount"), K("AUTHORCOUNT"))


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
    Symbol.regex = re.compile(r"(\w+([-/.]\w+)*)")
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
    grammar = attr('children', [
        (NormalPhrase, NormalPhraseSpanTail),
        (ExactPhrase, ExactPhraseSpanTail),
        PartialPhrase,
        RegexPhrase,
    ])


class ExactAuthorOp(UnaryRule):
    grammar = omit(ExactAuthor), omit(optional(':')), attr('op', NormalPhrase)


class AuthorCountOp(UnaryRule):
    grammar = omit(AuthorCount), omit(optional(':')), attr('op', re.compile("\d+"))


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
            AuthorCountOp,
            ExactAuthorOp,
            FulltextOp,
            ReferenceOp,
            TermExpressionWithColon,
            TermExpressionWithoutColon,
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
    grammar = attr('op', [
        AndQuery,
        OrQuery,
    ])


class ParenthesizedQuery(UnaryRule):
    grammar = omit(Literal('(')), attr('op', QueryExpression), omit(Literal(')'))


class QueryExpressionTail(UnaryRule):
    pass


QueryExpression.grammar = attr('children', [
    (TermExpression, QueryExpressionTail),
    NotQuery,
    ParenthesizedQuery,
])


QueryExpressionTail.grammar = attr('op', [
    BooleanQuery,
    None
])


class StartRule(UnaryRule):
    grammar = [
        (omit(Find), attr('op', QueryExpression)),
        attr('op', QueryExpression),
    ]
