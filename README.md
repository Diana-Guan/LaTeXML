# LaTeX to MathML conversion using LaTeXML

## Purpose
This project tests how LaTeXML converts LaTeX math into:
- XMath
- Content MathML
- XMath + Content MathML

The main goal is to evaluate which representation is most useful for ontology labeling.

## Project Structure
- `test_input/`  
  Small LaTeX test files organized by math category.

- `test_output/XMath/`  
  LaTeXML output with XMath.

- `test_output/ContentML/`  
  LaTeXML output with Content MathML.

- `test_output/XMath_ContentML/`  
  LaTeXML output with both XMath and Content MathML.

- `tools/extract_math.py`  
  Python tool that extracts math from a larger LaTeX file and creates a math-only `.tex` file.

- `extracted_file/`  
  Generated math-only files for LaTeXML conversion.

- `LaTeXML_Comparison_01_08.md`  
  Comparison notes for tests 01 to 08.

- `LaTeXML_Comparison_Q34.md`  
  Comparison notes for the Q34 worked example.

## Current Conclusion
The current comparison suggests that:
- XMath + Content MathML together is the most useful choice for ontology labeling

## How to Run the Extractor
To create a math-only file from a larger LaTeX source:

```bash
cd /Users/guanshengmei/Documents/LaTeXML
python3 tools/extract_math.py Q34_Version3.tex
```
## How to run [LaTeXML](https://github.com/brucemiller/latexml)
Make sure `latexml` and `latexmlpost` are available in your environment.
Example commend:

```bash
latexml --destination=test_output/XMath/01_basic.xml test_input/01_basic.tex
latexmlpost --format=xml --contentmathml --destination=test_output/ContentML/01_basic.xml test_output/XMath/01_basic.xml
latexmlpost --format=xml --contentmathml --keepXMath --destination=test_output/XMath_ContentML/01_basic.xml test_output/XMath/01_basic.xml
