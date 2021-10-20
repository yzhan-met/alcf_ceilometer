# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS       ?=
SPHINXBUILD      ?= sphinx-build
IS_COMMIT_TAGGED ?= false
DOCS_DIR          = src
SOURCE_DIR        = _source
BUILD_DIR         = _build
CONF_FILE         = $(DOCS_DIR)/conf.py
INFRAS_AWS        = ../stacks
LAMBDA_AWS        = ../lambdas
README_FILE       = ../README.md
PUBLISH_DST       = alcf_ceilometer
DOCS_REGION       = us-west-2

override ENV = dev
ifeq ($(IS_COMMIT_TAGGED),True)
	override ENV = prod
endif

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCE_DIR)" "$(BUILD_DIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCE_DIR)" "$(BUILD_DIR)" $(SPHINXOPTS) $(O)

clean_build:
	rm -rf $(BUILD_DIR)

clean_source:
	rm -rf $(SOURCE_DIR)

clean: clean_source clean_build

prep_src:
		rsync -rL --include="*/" --include="*.rst" --include="*.md" --include="*.png" --exclude="*" $(DOCS_DIR)/ $(SOURCE_DIR)/ ; \
		cp $(CONF_FILE) $(SOURCE_DIR)/
		
gen_src: clean_source prep_src
	sphinx-apidoc -e --ext-autodoc -f -o $(SOURCE_DIR)/api/infras $(INFRAS_AWS)
	sphinx-apidoc -e --ext-autodoc -f -o $(SOURCE_DIR)/api/lambdas/alcf_ceilometer/function $(LAMBDA_AWS)/alcf_ceilometer/function

gen_html: clean_build
	@$(SPHINXBUILD) $(SOURCE_DIR) $(BUILD_DIR)

gen_all: gen_src gen_html ;

publish:
	aws s3 sync --delete --only-show-errors $(BUILD_DIR) s3://$$(aws ssm get-parameter --name /docs/$(ENV)/bucket_name --output text --query 'Parameter.Value' --region $(DOCS_REGION))/$(PUBLISH_DST)
