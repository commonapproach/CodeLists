####
## Usage:
##
## `make alts` - generate all serializations for all CodeLists
## `make ESDCSector` - generate all serializations for a single CodeList
## `make alts FORMAT=jsonld` - generate 1 serialization for all CodeLists
## `make ESDCSector FORMAT=jsonld` - generate 1 serialization for a single CodeList
####

####
## Variables at the top set up a list of CodeLists, and the formats we publish.
CODELISTS = CanadianCorporateRegistries EquityDeservingGroupsESDC ESDCSector FundingState ICNPOsector IRISImpactCategory IRISImpactTheme IrisMetric53 LocalityStatsCan OrgTypeGOC PopulationServed ProvinceTerritory RallyImpactArea SDGImpacts SELI-GLI StatsCanSector UnitsOfMeasureList
FORMATS  ?= owl jsonld nt csv
##
####

####
## These top-level targets are helpers to mass update codelist serializations

alts: $(CODELISTS) ##@ Generate alternate serializations for all codelists

$(CODELISTS):      ##@ Generate alternate serializations for one codelist
        make -s codelist-alts CODELIST=$@

codelist-alts: .checkvar-CODELIST
codelist-alts:
        echo "Generating alternate serializations for $(CODELIST)..."
        touch $(CODELIST).ttl
        for x in $(FORMATS) ; do \
                make $(CODELIST).$$x ; \
        done

check-codelist: .checkvar-CODELIST ##@ Basic parsing sanity check with rdflib.
        echo "Doing basic parse tst on $(CODELIST).ttl..."
        python rdflib-parse.py $(CODELIST).ttl
##
####

####
## These targets are the core of the Makefile, calling riot or python commands
## to generate alternate serialization formats.
%.owl: %.ttl
        riot --output=RDF/XML --base="https://codelist.commonapproach.org/$*#" $< > $@

%.nt: %.ttl
        riot --output=N-Triples $< > $@

%.csv: %.ttl
        python rdflib-csv.py $<

%.jsonld: %.ttl
        riot --output=JSON-LD $< > $@
##
####

####
## Makefile arcana to make the above work nicely
# Check if a variable is set, and fail if not.
# See http://stackoverflow.com/a/7367903/436063
# and https://gist.github.com/brimston3/fc43658bdb6882ed13d942fa584dd2de
.checkvar-%: .checkvar ## .checkvar-VARIABLENAME fails unless VARIABLENAME is set.
        @if [ "${${*}}" = "" ]; then \
                echo "Variable $* not set"; \
                exit 1; \
        fi

.PHONY: .checkvar
.checkvar:
##
####
