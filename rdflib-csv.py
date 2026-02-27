import csv
import os
import sys
from rdflib import Graph

file = sys.argv[1]
codelist = os.path.splitext(os.path.basename(file))[0]
csvfilename = f"{codelist}.csv"

print("Converting TTL file to CSV using RDFLib...")
print(f"File: {file}")
print(f"Codelist: {codelist}")

g = Graph()
g.parse(file, format="turtle")

qres = g.query(
        """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?URL ?CODE ?LABEL_EN ?DESCRIPTION_EN
        WHERE {
            ?URL skos:prefLabel ?LABEL_EN .
            ?URL skos:notation ?CODE .
            OPTIONAL {
                ?URL skos:definition ?definition .
            }
            BIND(COALESCE(?definition, ""^^xsd:string) AS ?DESCRIPTION_EN)
            FILTER(LANG(?LABEL_EN) = "en")
        }
        ORDER BY ?CODE
        """
)

#@TODO: add some custom logic to special-case the SPARQL query based on the CodeList.
# This one was customized for UnitsOfMeasureList in particular
#qres = g.query(
#        """
#        PREFIX i72: <http://ontology.eil.utoronto.ca/ISO21972/iso21972#>
#        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#        SELECT ?URL ?CODE ?LABEL_EN ?DESCRIPTION_EN
#        WHERE {
#            ?URL rdfs:label ?LABEL_EN .
#            ?URL i72:symbol ?CODE .
#            OPTIONAL {
#                ?URL rdfs:comment ?definition .
#            }
#            BIND(COALESCE(?definition, ""^^xsd:string) AS ?DESCRIPTION_EN)
#            FILTER(LANG(?LABEL_EN) = "en")
#        }
#        ORDER BY ?CODE
#        """
#)

with open(csvfilename, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile, doublequote=False, lineterminator='\n',
            quoting=csv.QUOTE_ALL, escapechar='\\')
    csv_writer.writerow(list(qres.vars))
    for row in qres:
        print(row)
        csv_writer.writerow([str(item) for item in row])

print(f"Conversion complete. Output saved to {csvfilename}.")
