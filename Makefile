pandoc := $(shell command -v pandoc 2> /dev/null)
markdown := pandoc --from markdown --to html --standalone --css "/style.css"

web_files := $(shell find web/ -type f)
site_files := $(patsubst web/%,www/%,$(patsubst %.py,%.html,$(web_files)))

.PHONY: all
all: $(site_files)

.PHONY: clean
clean:
	rm -f www/index.html
	rm -f www/recent_pairings.html

www/%.html: web/%.py hack.db
	mkdir -p $(dir $@)
	python3 $< > tmp
	cp tmp $@

www/%: web/%
	mkdir -p $(dir $@)
	cp $< $@
