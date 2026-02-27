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
CODELISTS = CanadianCorporateRegistries EquityDeservingGroupsESDC ESDCSector FundingState ICNPOsector IRISImpactCategory IRISImpactTheme IrisMetric53 LocalityStatsCan OrgTypeGOC PopulationServed ProvinceTerritory RallyImpactArea SDGImpacts SELI-GLI SELI-GLI-SFI StatsCanSector UnitsOfMeasureList
FORMATS  ?= owl jsonld nt csv html

# We use WIDOCO to build HTML versions of the CodeLists. 
# These variables configure where and how we invoke Widoco
WIDOCO_WORK_DIR = ./work
WIDOCO_OPTIONS  = -rewriteAll -uniteSections -getOntologyMetadata -noPlaceHolderText
# These variables configure a source and version of Widoco to install
WIDOCO_VERSION  = 1.4.25
WIDOCO_JDK      = 11
WIDOCO_BASE_URL = https://github.com/dgarijo/Widoco/releases/download/v$(WIDOCO_VERSION)
WIDOCO_JAR      = widoco-$(WIDOCO_VERSION)-jar-with-dependencies_JDK-$(WIDOCO_JDK).jar
WIDOCO_BIN      = $(WIDOCO_WORK_DIR)/scripts/$(WIDOCO_JAR)
WIDOCO_URL      = $(WIDOCO_BASE_URL)/$(WIDOCO_JAR)
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

%.html: %.ttl $(WIDOCO_BIN)
	@echo "Invoking Widoco to generate HTML docs for $< in $(WIDOCO_WORK_DIR)/$* ..."
	mkdir -p $(WIDOCO_WORK_DIR)/$*                                                          # Ensure the working directory exists
	java -jar $(WIDOCO_BIN) $(WIDOCO_OPTIONS) -outFolder $(WIDOCO_WORK_DIR)/$* -ontFile $<  # Invoke Widoco to generate single-page html page
	mv $(WIDOCO_WORK_DIR)/$*/index-en.html $@                                               # Move it into place
	sed -i 's!resources/!https://ontology.commonapproach.org/resources/!' $@                # Don't rely on local resources

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

# Install Widoco
$(WIDOCO_WORK_DIR)/scripts:
	        mkdir -p $(WIDOCO_WORK_DIR)/scripts

$(WIDOCO_BIN): | $(WIDOCO_WORK_DIR)/scripts
	wget -O $(WIDOCO_BIN) $(WIDOCO_URL)

# Serve the local public folder using a simple Python webserver
serve:
	python -m http.server 8080 --bind 127.0.0.1 &

##
####
