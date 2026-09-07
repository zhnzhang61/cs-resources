# LaTeX lives at /Library/TeX/texbin (TeX Live 2026, installed system-wide).
# An interactive shell already has it on PATH via /etc/paths.d/TeX. But macOS
# ships GNU Make 3.81, whose `export PATH := ...` doesn't reliably reach recipe
# sub-shells — and latexmk itself shells out to pdflatex — so inject PATH into
# every recipe explicitly. This makes the build work from any context: your
# terminal, an editor, a script, or an agent.
TEXBIN := /Library/TeX/texbin
TEX    := PATH="$(TEXBIN):$$PATH"

MAIN := resume

.PHONY: all watch view clean distclean

# One-shot build -> build/$(MAIN).pdf, then copy the PDF up to resume/ for easy sharing.
all:
	$(TEX) latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex
	@cp build/$(MAIN).pdf $(MAIN).pdf
	@echo "==> $(MAIN).pdf updated"

# Rebuild automatically on every save.
watch:
	$(TEX) latexmk -pdf -pvc -interaction=nonstopmode $(MAIN).tex

view: all
	open $(MAIN).pdf

# Remove aux files, keep the PDF.
clean:
	$(TEX) latexmk -c $(MAIN).tex

# Remove everything generated, including the PDF.
distclean:
	$(TEX) latexmk -C $(MAIN).tex
	rm -rf build $(MAIN).pdf
