# LaTeXML Ontology Comparison: Q34 Version 3

## Purpose
This report compares XMath, Content MathML, and XMath + Content MathML for `Q34_Version3_mathonly`. The goal is to evaluate which representation is most useful for ontology labeling on a full worked Calculus 2 solution rather than on short isolated expressions.

## Recommendation
Use XMath + Content MathML together.

For Q34, however, the main bottleneck is not only the representation choice. The bigger issue is extraction quality. The `mathonly` source still contains explanatory prose inside some array and aligned environments, and that noise degrades all three outputs.

## Key Failure Patterns
- Explanatory prose inside math arrays is tokenized as multiplied single-letter identifiers.
- Some split equations produce `absent` placeholders in branch outputs.
- Some matrix rows contain `missing-subexpression` errors.
- Exponentiation is still represented as ambiguous `superscript`.
- Inverse sine is represented as superscripted `sin^{-1}` rather than a normalized inverse-trig operator.

## Q34 Version 3: Mathonly
- Scope note: this comparison is based on `Q34_Version3_mathonly`, not the original styled source.
- Files compared:
  - `test_output/XMath/Q34_Version3_mathonly.xml`
  - `test_output/ContentML/Q34_Version3_mathonly.xml`
  - `test_output/XMath_ContentML/Q34_Version3_mathonly.xml`
- XMath success: core calculus objects are often recognizable. Integrals keep `INTOP`, differentials keep `DIFFOP`, trig functions keep `TRIGFUNCTION`, and many roots, fractions, equalities, and substitution formulas remain structurally visible.
- XMath failure pattern: when prose survives inside math environments, XMath turns words into products of letters such as `R * e * w * r * i * t * e` or `S * u * b * s * t * i * t * u * t * e`. This makes many derivation rows unsuitable for direct labeling.
- ContentML success: compact standalone formulas still convert into useful operator trees. The main integral, trig-substitution equations, root identities, absolute-value formulas, and several final equalities are still labelable at the local operator level.
- ContentML failure pattern: explanatory rows become noisy matrices with multiplied letters, `formulae-sequence` wrappers, `missing-subexpression` nodes, or list-like payloads. This makes many intermediate derivation steps unreliable for ontology labeling.
- Combined success: the combined representation is the most informative. XMath helps identify which noisy expressions were intended to contain integrals, differentials, or trig functions, while Content MathML provides a cleaner tree for the formulas that were extracted well.
- Combined failure pattern: the combined representation does not solve extraction noise. If the source expression still mixes prose and math, the output remains noisy in both layers.
- Decision: use XMath + Content MathML for Q34 as well, but treat extraction quality as a prerequisite. The representation choice matters, but source cleanliness matters more for long worked solutions.

## Final Decision
- Preferred representation: XMath + Content MathML.
- Why: XMath preserves operator-role information that is still valuable in noisy long-form solutions, and Content MathML preserves cleaner operator trees where extraction succeeds.
- Why not XMath alone: it exposes useful roles, but the noisy prose-to-letter-token behavior is still hard to normalize by itself.
- Why not Content MathML alone: it loses too many local role clues and makes it harder to distinguish malformed extraction from genuine mathematical structure.
- What this means for ontology labeling: final formulas and compact identities from Q34 are usable, but many intermediate explanatory rows should not be labeled directly until the extractor is improved to remove prose from array and aligned environments.
