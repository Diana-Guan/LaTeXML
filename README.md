# LaTeX to MathML Conversion Using LaTeXML

## Purpose
This project tests how LaTeXML converts LaTeX math into:

- XMath
- Content MathML
- XMath + Content MathML

The main goal is to evaluate which representation is most useful for ontology labeling.

I also built a math extraction tool for this project. I created it because our original LaTeX files contain custom macros and more complicated packages that do not convert well under LaTeXML. For ontology labeling and downstream parsing, I needed a cleaner math-focused input file, so I built this extractor to isolate the mathematical content into a smaller LaTeX file that is easier for LaTeXML to process.


The extraction tool is located in `tools/extract_math.py`. It takes a larger LaTeX source file, extracts the math content, and generates a math-only `.tex` file for LaTeXML conversion. I also sent this extraction tool Python file to Tobias, and he revised the code to help support his Python parsing workflow as well.

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

## How to Run LaTeXML
Make sure `latexml` and `latexmlpost` are available in your environment.

Example commands:

```bash
latexml --destination=test_output/XMath/01_basic.xml test_input/01_basic.tex
latexmlpost --format=xml --contentmathml --destination=test_output/ContentML/01_basic.xml test_output/XMath/01_basic.xml
latexmlpost --format=xml --contentmathml --keepXMath --destination=test_output/XMath_ContentML/01_basic.xml test_output/XMath/01_basic.xml
```

## Output Types
The LaTeXML workflow in this project is used to compare three output formats:

- `XMath`: useful for preserving LaTeXML’s internal mathematical structure
- `Content MathML`: useful for semantic interpretation
- `XMath + Content MathML`: useful when both structural and semantic information are needed together

