from pypeg2 import parse
from inspire_query_parser.parser import StartRule

if __name__ == '__main__':
    # Find keyword combined with other production rules
    print(parse('find author "ellis"', StartRule))
    print(parse("FIN author:'ellis'", StartRule))
    print(parse('f author ellis', StartRule))

    # Invenio like search
    print(parse("author:ellis and title:boson", StartRule))

    # Boolean operator testing
    print(parse("author ellis and title 'boson'", StartRule))
    print(parse("author ellis AND title boson", StartRule))
    print(parse("author ellis | title 'boson'", StartRule))
    print(parse("author ellis OR title 'boson'", StartRule))
    print(parse("author ellis + title 'boson'", StartRule))
    print(parse("author ellis & title 'boson'", StartRule))

    # Negation
    print(parse("author ellis and not title 'boson'", StartRule))
    print(parse("-title 'boson'", StartRule))

    # Nested expressions
    print(parse("author ellis, j. and (title boson or (author /^xi$/ and title foo))", StartRule))

    # Metadata search
    print(parse("fulltext:boson", StartRule))
    print(parse("reference:Ellis", StartRule))
    print(parse('reference "Ellis"', StartRule))

    # Only phrases
    print(parse('ellis', StartRule))
    print(parse("'ellis'", StartRule))

    # # Non trivial terminals
    print(parse("find Higgs boson", StartRule))
    print(parse("author ellis, j.", StartRule))
    print(parse("author j., ellis", StartRule))
    print(parse("f title Super Collider Physics", StartRule))
    print(parse("find title Alternative the Phase-II upgrade of the ATLAS Inner Detector or title foo", StartRule))
    print(parse("find title na61/shine", StartRule))
    print(parse("title foo and author abtrall", StartRule))
    print(parse("title e-10 and -author:ellis", StartRule))
