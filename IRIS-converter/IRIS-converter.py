import pandas as pd
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, DCTERMS
import urllib.parse
import re

# --- Configuration ---
INPUT_FILE = "IRIS+ 5.3b Catalog of Metrics.csv"
OUTPUT_FILE = "iris_metrics_graph.ttl"

def slugify(text):
    """Creates a URL-safe identifier from text (e.g., 'Financial Services' -> 'financial-services')"""
    if not isinstance(text, str):
        return str(text)
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)  # Remove special chars
    text = re.sub(r'[\s-]+', '-', text)       # Replace spaces with hyphens
    return text

def convert_iris_to_skos():
    print(f"Loading {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"Error: {e}")
        return

    # Initialize Graph
    g = Graph()
    IRIS = Namespace("https://iris.thegiin.org/metric/")
    CAT = Namespace("https://iris.thegiin.org/category/")
    
    g.bind("iris", IRIS)
    g.bind("cat", CAT)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)

    # Define the Scheme
    scheme_uri = URIRef("https://iris.thegiin.org/taxonomy")
    g.add((scheme_uri, RDF.type, SKOS.ConceptScheme))
    g.add((scheme_uri, DCTERMS.title, Literal("GIIN IRIS+ Metrics 5.3b", lang="en")))

    print(f"Processing {len(df)} metrics...")
    
    # Cache created categories to prevent duplicate triples
    created_cats = set()

    for index, row in df.iterrows():
        if pd.isna(row.get('ID')):
            continue

        # 1. Create Metric Concept
        metric_id = str(row['ID']).strip()
        metric_uri = IRIS[metric_id]
        
        g.add((metric_uri, RDF.type, SKOS.Concept))
        g.add((metric_uri, SKOS.inScheme, scheme_uri))
        g.add((metric_uri, SKOS.notation, Literal(metric_id)))

        # Name
        if not pd.isna(row.get('Metric Name')):
            g.add((metric_uri, SKOS.prefLabel, Literal(row['Metric Name'].strip(), lang="en")))
            
        # Definition
        if not pd.isna(row.get('Definition')):
            g.add((metric_uri, SKOS.definition, Literal(row['Definition'].strip(), lang="en")))

        # Usage Guidance
        if not pd.isna(row.get('Usage Guidance')):
            g.add((metric_uri, SKOS.note, Literal(row['Usage Guidance'].strip(), lang="en")))

        # 2. Handle Primary Impact Category (Thematic Hierarchy)
        if not pd.isna(row.get('Primary Impact Category')):
            cat_name = row['Primary Impact Category'].strip()
            cat_slug = slugify(cat_name)
            cat_uri = CAT[cat_slug]
            
            # Link Metric -> Category
            g.add((metric_uri, SKOS.broader, cat_uri))
            
            # Create Category if new
            if cat_slug not in created_cats:
                g.add((cat_uri, RDF.type, SKOS.Concept))
                g.add((cat_uri, SKOS.prefLabel, Literal(cat_name, lang="en")))
                g.add((cat_uri, SKOS.inScheme, scheme_uri))
                created_cats.add(cat_slug)

        # 3. Handle Section / Subsection (Structural Hierarchy)
        # Logic: Metric -> Subsection -> Section
        
        section_uri = None
        
        # Create Section
        if not pd.isna(row.get('Section')):
            sec_name = row['Section'].strip()
            sec_slug = slugify(sec_name)
            section_uri = CAT[sec_slug]
            
            if sec_slug not in created_cats:
                g.add((section_uri, RDF.type, SKOS.Concept))
                g.add((section_uri, SKOS.prefLabel, Literal(sec_name, lang="en")))
                g.add((section_uri, SKOS.inScheme, scheme_uri))
                created_cats.add(sec_slug)

        # Create Subsection and link to Section
        if not pd.isna(row.get('Subsection')):
            sub_name = row['Subsection'].strip()
            sub_slug = slugify(sub_name)
            sub_uri = CAT[sub_slug]
            
            g.add((metric_uri, SKOS.broader, sub_uri)) # Metric -> Subsection
            
            if sub_slug not in created_cats:
                g.add((sub_uri, RDF.type, SKOS.Concept))
                g.add((sub_uri, SKOS.prefLabel, Literal(sub_name, lang="en")))
                g.add((sub_uri, SKOS.inScheme, scheme_uri))
                
                # Link Subsection -> Section
                if section_uri:
                    g.add((sub_uri, SKOS.broader, section_uri))
                
                created_cats.add(sub_slug)
        
        # If no subsection, link metric directly to section
        elif section_uri:
            g.add((metric_uri, SKOS.broader, section_uri))

    # Save to file
    g.serialize(destination=OUTPUT_FILE, format="turtle")
    print(f"Success! RDF taxonomy saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    convert_iris_to_skos()