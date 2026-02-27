import pprint
import sys
from rdflib import Graph

file = sys.argv[1]

g = Graph()
g.parse(file)

print(len(g))

#for stmt in g:
#    pprint.pprint(stmt)

for s, p, o in g:
    print(f"subject: {s}")
    print(f"predicat: {p}")
    print(f"object: {o}")
