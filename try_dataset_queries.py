#!/usr/bin/env python
import re
import sys

from pypeg2 import parse

from inspire_query_parser.parser import StartRule
from inspire_query_parser.utils.utils import tree_print

unsupported = {"collection", "refersto", "citedby"}

if __name__ == '__main__':
    with open("queries.txt", "r") as input_file:
        queries_read = 0
        for line in input_file:

            try:
                t = parse(line, StartRule)
                # print(tree_print(t))

                queries_read += 1
            except (ValueError, SyntaxError):
                if not unsupported.intersection(set(re.split('[ :]', line))):
                    sys.stderr.write(line)
