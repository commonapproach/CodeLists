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

WORK_DIR    = ./work
SCRIPTS_DIR = $(WORK_DIR)/scripts

# We use Apache JENA riot to build OWL, JSON-LD, and N-triples serializations of the CodeLists.
# These variables configure a source and version of Apache-jena to intsall
JENA_VERSION = 5.6.0
JENA_NAME    = apache-jena-$(JENA_VERSION)
JENA_TARBALL = $(WORK_DIR)/$(JENA_NAME).tar.gz
JENA_URL     = https://archive.apache.org/dist/jena/binaries/$(JENA_NAME).tar.gz
JENA_DIR     = $(SCRIPTS_DIR)/$(JENA_NAME)
RIOT_BIN     = $(SCRIPTS_DIR)/$(JENA_NAME)/bin/riot

# We use WIDOCO to build HTML serializations of the CodeLists. 
# These variables configure where and how we invoke Widoco
WIDOCO_OPTIONS  = -rewriteAll -uniteSections -getOntologyMetadata -noPlaceHolderText
# These variables configure a source and version of Widoco to install
WIDOCO_VERSION  = 1.4.25
WIDOCO_JDK      = 11
WIDOCO_BASE_URL = https://github.com/dgarijo/Widoco/releases/download/v$(WIDOCO_VERSION)
WIDOCO_JAR      = widoco-$(WIDOCO_VERSION)-jar-with-dependencies_JDK-$(WIDOCO_JDK).jar
WIDOCO_BIN      = $(SCRIPTS_DIR)/$(WIDOCO_JAR)
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
%.owl: %.ttl $(RIOT_BIN)
	$(RIOT_BIN) --output=RDF/XML --base="https://codelist.commonapproach.org/$*#" $< > $@

%.nt: %.ttl $(RIOT_BIN)
	$(RIOT_BIN) --output=N-Triples $< > $@

%.csv: %.ttl $(RIOT_BIN)
	python rdflib-csv.py $<

%.jsonld: %.ttl $(RIOT_BIN)
	$(RIOT_BIN) --output=JSON-LD $< > $@

%.html: %.ttl $(WIDOCO_BIN)
	@echo "Invoking Widoco to generate HTML docs for $< in $(WORK_DIR)/$* ..."
	mkdir -p $(WORK_DIR)/$*                                                          # Ensure the working directory exists
	java -jar $(WIDOCO_BIN) $(WIDOCO_OPTIONS) -outFolder $(WORK_DIR)/$* -ontFile $<  # Invoke Widoco to generate single-page html page
	mv $(WORK_DIR)/$*/index-en.html $@                                        # Move it into place
	sed -i 's!resources/!https://ontology.commonapproach.org/resources/!' $@         # Don't rely on local resources

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

# The entire WORK_DIR should be transient and easy to reproduce with targets in this Makefile.
clean:
	rm -rf $(WORK_DIR) tmp*

# Install Widoco
$(SCRIPTS_DIR):
	mkdir -p $(WORK_DIR)/scripts

# Install Jena/Riot
$(RIOT_BIN): | $(SCRIPTS_DIR) $(JENA_TARBALL)
	tar xvfz $(JENA_TARBALL) --directory=$(SCRIPTS_DIR) 

$(JENA_TARBALL):
	wget -O $(JENA_TARBALL) $(JENA_URL)

$(WIDOCO_BIN): | $(SCRIPTS_DIR)
	wget -O $(WIDOCO_BIN) $(WIDOCO_URL)

# Serve the local public folder using a simple Python webserver
serve:
	python -m http.server 8080 --bind 127.0.0.1 &

##
####
