# LaTeXML Test

This directory contains seperate `.tex` file per test category so I can run LaTeXML on each category independently.

Files:

- `01_basic.tex`
- `02_functions.tex`
- `03_derivatives.tex`
- `04_integrals.tex`
- `05_trig_sub.tex`
- `06_rational.tex`
- `07_series.tex`
- `08_limits.tex`
- `09_ambiguity.tex`
- `10_macros.tex`

Example:

Test commend:
Content MathML
latexml --destination=test_output/03.xml test_input/03.tex
latexmlpost --format=xml --contentmathml --destination=test_output/03_cmml.xml test_output/03.xml
XMath
latexml --destination=test_output/03.xml test_input/03.tex

