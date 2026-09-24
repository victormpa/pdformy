PDFORMY ?= poetry run pdformy
TEMPLATES := $(wildcard tests/templates/*.yaml)
OUT_DIR := build/templates

.PHONY: templates clean-templates

templates:
	mkdir -p $(OUT_DIR)
	@for src in $(TEMPLATES); do \
		out="$(OUT_DIR)/$$(basename $${src%.yaml}.pdf)"; \
		echo "$(PDFORMY) $$src -o $$out"; \
		$(PDFORMY) $$src -o $$out; \
	done

clean-templates:
	rm -rf $(OUT_DIR)
