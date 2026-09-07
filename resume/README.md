# resume

LaTeX resume. `resume.tex` is currently a placeholder skeleton — replace it with your own.

## Build

From this directory:

```bash
make
```

Output: `resume.pdf` (aux files are kept out of the way in `build/`, which is gitignored).

| command | what it does |
|---|---|
| `make` | one-shot build → `resume.pdf` |
| `make watch` | rebuild automatically on every save |
| `make view` | build, then open the PDF in Preview |
| `make clean` | delete aux files, keep the PDF |
| `make distclean` | delete everything generated, including the PDF |

## Environment

TeX Live 2026 (full scheme, ~9.7 GB) is already installed system-wide at `/usr/local/texlive/2026`, with binaries symlinked into `/Library/TeX/texbin`. An interactive shell picks that up automatically via `/etc/paths.d/TeX`.

The Makefile injects that path into every recipe rather than relying on the inherited `PATH`, because (a) macOS ships GNU Make 3.81, whose `export PATH := ...` doesn't reliably reach recipe sub-shells, and (b) `latexmk` itself shells out to `pdflatex`, so the sub-shell needs it too. Net effect: `make` works from a terminal, an editor task, a script, or an agent alike.

Available and verified: `moderncv`, `europecv`, `geometry`, `enumitem`, `titlesec`, `fontawesome5`, `hyperref`, `xcolor`, `tabularx`, `multirow`. Anything else in CTAN is installable with `sudo tlmgr install <pkg>`.

## Engine

Defaults to **pdflatex** (`$pdf_mode = 1` in `.latexmkrc`). If you switch to system fonts via `fontspec`, change it to `$pdf_mode = 5` for xelatex.

## Editor

VS Code: `⌘⇧P` → *Run Task* → **LaTeX: build resume** or **LaTeX: watch resume**.
