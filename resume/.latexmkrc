# Build with pdflatex; keep aux files in build/ so the folder stays clean.
$pdf_mode = 1;              # 1 = pdflatex, 4 = lualatex, 5 = xelatex (switch if you use system fonts)
$aux_dir  = 'build';
$out_dir  = 'build';
$pdf_previewer = 'open -a Preview';
$clean_ext = 'synctex.gz run.xml bbl fdb_latexmk fls';
