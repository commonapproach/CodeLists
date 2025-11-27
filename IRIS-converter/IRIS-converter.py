import pandas as pd
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, DCTERMS
import urllib.parse
import re

# --- Configuration ---
INPUT_FILE = "IRIS+ 5.3b Catalog of Metrics.csv"
OUTPUT_FILE = "iris_metrics_complete.ttl"

# Parent Themes (Must match CSV headers exactly)
PARENT_THEMES = [
    "Agriculture",
    "Air",
    "Biodiversity and Ecosystems", 
    "Climate",
    "Diversity and Inclusion",
    "Education",
    "Employment",
    "Energy",
    "Financial Services",
    "Health",
    "Infrastructure",
    "Land",
    "Oceans and Coastal Zones",
    "Pollution",
    "Real Estate",
    "Waste",
    "Water"
]

def slugify(text):
    """Creates a URL-safe identifier from text."""
    if not isinstance(text, str):
        return str(text)
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    return text

def convert_iris_unified():
    print(f"Loading {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # Initialize Graph
    g = Graph()
    IRIS = Namespace("https://iris.thegiin.org/metric/")
    CAT = Namespace("https://iris.thegiin.org/category/") # For Sections/Primary Categories
    THEME = Namespace("https://iris.thegiin.org/theme/")   # For Theme/Subtheme
    
    g.bind("iris", IRIS)
    g.bind("cat", CAT)
    g.bind("theme", THEME)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)

    # Define the Scheme
    scheme_uri = URIRef("https://iris.thegiin.org/taxonomy")
    g.add((scheme_uri, RDF.type, SKOS.ConceptScheme))
    g.add((scheme_uri, DCTERMS.title, Literal("GIIN IRIS+ Metrics Complete Taxonomy", lang="en")))

    # --- Map Theme Columns ---
    try:
        start_idx = df.columns.get_loc("Agriculture")
        end_idx = df.columns.get_loc("Social and/or Environmental Focus")
        theme_columns = df.columns[start_idx:end_idx]
    except KeyError as e:
        print(f"Error locating theme columns: {e}")
        return

    # Map Subthemes to Parents
    theme_parent_map = {} 
    current_parent = None
    for col in theme_columns:
        if col in PARENT_THEMES:
            current_parent = col
        elif current_parent:
            theme_parent_map[col] = current_parent

    # --- Process Metrics ---
    print(f"Processing {len(df)} metrics...")
    created_nodes = set()

    for index, row in df.iterrows():
        if pd.isna(row.get('ID')):
            continue

        metric_id = str(row['ID']).strip()
        metric_uri = IRIS[metric_id]
        
        # 1. Basic Metadata
        g.add((metric_uri, RDF.type, SKOS.Concept))
        g.add((metric_uri, SKOS.inScheme, scheme_uri))
        g.add((metric_uri, SKOS.notation, Literal(metric_id)))

        if not pd.isna(row.get('Metric Name')):
            g.add((metric_uri, SKOS.prefLabel, Literal(row['Metric Name'].strip(), lang="en")))
            
        if not pd.isna(row.get('Definition')):
            g.add((metric_uri, SKOS.definition, Literal(row['Definition'].strip(), lang="en")))

        # 2. Primary Impact Category (Thematic)
        if not pd.isna(row.get('Primary Impact Category')):
            cat_name = row['Primary Impact Category'].strip()
            cat_slug = slugify(cat_name)
            cat_uri = CAT[cat_slug]
            g.add((metric_uri, SKOS.broader, cat_uri))
            
            if cat_slug not in created_nodes:
                g.add((cat_uri, RDF.type, SKOS.Concept))
                g.add((cat_uri, SKOS.prefLabel, Literal(cat_name, lang="en")))
                g.add((cat_uri, SKOS.inScheme, scheme_uri))
                created_nodes.add(cat_slug)

        # 3. Section / Subsection Hierarchy (RESTORED LOGIC)
        section_uri = None
        
        # Create Section Node
        if not pd.isna(row.get('Section')):
            sec_name = row['Section'].strip()
            sec_slug = slugify(sec_name)
            section_uri = CAT[sec_slug]
            
            if sec_slug not in created_nodes:
                g.add((section_uri, RDF.type, SKOS.Concept))
                g.add((section_uri, SKOS.prefLabel, Literal(sec_name, lang="en")))
                g.add((section_uri, SKOS.inScheme, scheme_uri))
                created_nodes.add(sec_slug)

        # Create Subsection Node and Link
        if not pd.isna(row.get('Subsection')):
            sub_name = row['Subsection'].strip()
            sub_slug = slugify(sub_name)
            sub_uri = CAT[sub_slug]
            
            # Metric is narrower than Subsection
            g.add((metric_uri, SKOS.broader, sub_uri)) 
            
            if sub_slug not in created_nodes:
                g.add((sub_uri, RDF.type, SKOS.Concept))
                g.add((sub_uri, SKOS.prefLabel, Literal(sub_name, lang="en")))
                g.add((sub_uri, SKOS.inScheme, scheme_uri))
                
                # Subsection is narrower than Section
                if section_uri:
                    g.add((sub_uri, SKOS.broader, section_uri))
                
                created_nodes.add(sub_slug)
        
        # If no subsection, link Metric directly to Section
        elif section_uri:
            g.add((metric_uri, SKOS.broader, section_uri))

        # 4. Themes & Subthemes Hierarchy (NEW LOGIC)
        for col_name in theme_columns:
            if pd.notna(row.get(col_name)):
                theme_slug = slugify(col_name)
                theme_uri = THEME[theme_slug]
                
                # Link Metric -> Theme
                g.add((metric_uri, SKOS.broader, theme_uri))
                
                if theme_slug not in created_nodes:
                    g.add((theme_uri, RDF.type, SKOS.Concept))
                    g.add((theme_uri, SKOS.prefLabel, Literal(col_name, lang="en")))
                    g.add((theme_uri, SKOS.inScheme, scheme_uri))
                    
                    # Link Subtheme -> Parent Theme
                    if col_name in theme_parent_map:
                        parent_name = theme_parent_map[col_name]
                        parent_slug = slugify(parent_name)
                        parent_uri = THEME[parent_slug]
                        
                        g.add((theme_uri, SKOS.broader, parent_uri))
                        
                        # Ensure Parent exists
                        if parent_slug not in created_nodes:
                            g.add((parent_uri, RDF.type, SKOS.Concept))
                            g.add((parent_uri, SKOS.prefLabel, Literal(parent_name, lang="en")))
                            g.add((parent_uri, SKOS.inScheme, scheme_uri))
                            created_nodes.add(parent_slug)
                    
                    created_nodes.add(theme_slug)

    # Serialize
    g.serialize(destination=OUTPUT_FILE, format="turtle")
    print(f"Success! RDF taxonomy saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    convert_iris_unified()