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
        SELECT ?URL ?CODE ?LABEL_EN ?DESCRIPTION_EN ?LABEL_FR ?DESCRIPTION_FR
        WHERE {
            ?URL skos:notation ?CODE .
            OPTIONAL {
                ?URL skos:prefLabel ?lbl_en .
                FILTER(LANG(?lbl_en) = "en")
            }
            OPTIONAL {
                ?URL skos:prefLabel ?lbl_fr .
                FILTER(LANG(?lbl_fr) = "fr")
            }
            OPTIONAL {
                ?URL skos:definition ?def_en .
                FILTER(LANG(?def_en) = "en")
            }
            OPTIONAL {
                ?URL skos:definition ?def_fr .
                FILTER(LANG(?def_fr) = "fr")
            }
            BIND(COALESCE(?lbl_en, ""^^xsd:string) AS ?LABEL_EN)
            BIND(COALESCE(?lbl_fr, ""^^xsd:string) AS ?LABEL_FR)
            BIND(COALESCE(?def_en, ""^^xsd:string) AS ?DESCRIPTION_EN)
            BIND(COALESCE(?def_fr, ""^^xsd:string) AS ?DESCRIPTION_FR)
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
