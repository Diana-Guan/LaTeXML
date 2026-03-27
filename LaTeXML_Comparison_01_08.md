# LaTeXML Ontology Comparison

## Purpose
This report compares XMath, Content MathML, and XMath + Content MathML for tests `01` through `08`. The goal is to decide which representation is most useful for ontology labeling, with emphasis on whether mathematical objects and relations can be labeled correctly.

## Recommendation
Use XMath + Content MathML together.

XMath preserves operator-role information that is useful for labeling, especially for integrals, sums, limits, and differentials. Content MathML gives a cleaner structural tree when the parse is correct. Neither one alone is reliable enough across the full test set.

## Key Failure Patterns
- Exponentiation is often represented as ambiguous `superscript` rather than a normalized power operator.
- Unknown function application such as `f(x)` is parsed as multiplication.
- Leibniz derivative notation is parsed as fraction/multiplication instead of a derivative operator.
- Some integrals absorb `dx` into the argument of a trig or function node.
- Limits and summation bounds are encoded as ambiguous subscript/superscript payloads instead of explicit binder structure.

## Test 01: Basic
- XMath success: addition, multiplication, fractions, roots, and grouping are labeled clearly through roles such as `ADDOP`, `MULOP`, `FRACOP`, and `SUPERSCRIPTOP`.
- XMath failure pattern: powers are still represented as superscript structure, not a normalized power relation.
- ContentML success: arithmetic trees are standardized cleanly with `<plus/>`, `<times/>`, `<divide/>`, and `<root/>`.
- ContentML failure pattern: exponentiation remains ambiguous through `<csymbol cd="ambiguous">superscript</csymbol>`.
- Combined success: gives both a clean arithmetic tree and XMath operator-role clues.
- Combined failure pattern: power still needs normalization before ontology labeling.
- Decision: combined output is best; basic algebra is largely usable after power normalization.

## Test 02: Functions
- XMath success: standard trig functions and `\ln` are recognized with useful function roles.
- XMath failure pattern: `f(x)` and `f(g(x))` are parsed as multiplication instead of function application.
- ContentML success: standard functions are standardized well as `<sin/>`, `<cos/>`, `<tan/>`, and `<ln/>`.
- ContentML failure pattern: `f(x)` and `f(g(x))` are also flattened to multiplication; trig powers remain ambiguous superscripts.
- Combined success: makes it easy to separate successful built-in function recognition from failed unknown-function recognition.
- Combined failure pattern: user-defined function application is still not directly labelable.
- Decision: combined output is best, but function-application labels need custom inference.

## Test 03: Derivatives
- XMath success: quotient structure and grouping are preserved clearly.
- XMath failure pattern: Leibniz notation is not recognized as a derivative operator; `d/dx` is treated as a fraction multiplied by an expression.
- ContentML success: the literal quotient structure is standardized consistently.
- ContentML failure pattern: derivative meaning is missing; `dy/dx` and `d^2y/dx^2` remain products and powers of identifiers.
- Combined success: makes the derivative failure pattern easy to inspect.
- Combined failure pattern: derivative semantics still have to be reconstructed by ontology rules.
- Decision: XMath is slightly more informative than ContentML, but the project still needs both if derivative normalization will be added later.

## Test 04: Integrals
- XMath success: integral signs are recognized as `INTOP`, and several cases preserve `DIFFOP` for the differential.
- XMath failure pattern: in expressions like `\int \sin x\,dx` and `\int e^x \cos x\,dx`, `dx` is absorbed into the trig/function argument.
- ContentML success: integrals are standardized with `<int/>`, and many algebraic integrands are structurally usable.
- ContentML failure pattern: the same malformed scope problem appears, especially when `dx` gets pulled into a function argument; bounds are encoded as ambiguous superscript/subscript attachments.
- Combined success: XMath gives `INTOP` and `DIFFOP`, while ContentML gives the overall tree.
- Combined failure pattern: integrand scope and bound semantics still need normalization.
- Decision: combined output is clearly best for integrals.

## Test 05: Trig Substitution Patterns
- XMath success: roots, equalities, multiplication, and trig functions are all preserved with useful local roles.
- XMath failure pattern: trig powers such as `\sin^2\theta` remain superscripted function tokens rather than normalized square-of-function values.
- ContentML success: the structural patterns for roots and substitution equations are clean and usable.
- ContentML failure pattern: trig powers are still ambiguous superscripts, so identity labeling is not direct.
- Combined success: supports both pattern detection and operator-role inspection.
- Combined failure pattern: no higher-level label such as “trig substitution pattern” or “Pythagorean identity” is produced directly.
- Decision: combined output is best; this category is relatively ontology-friendly after trig-power normalization.

## Test 06: Rational Expressions
- XMath success: numerator/denominator structure, products, and parenthesized factors are preserved clearly.
- XMath failure pattern: exponentiation in repeated factors is still only superscript structure.
- ContentML success: denominator patterns such as products of linear factors are clean and easy to traverse.
- ContentML failure pattern: powers remain ambiguous, and no factor-type labels are provided.
- Combined success: supports denominator-pattern labeling better than either representation alone.
- Combined failure pattern: repeated-factor and polynomial-degree labels still need to be inferred.
- Decision: combined output is best, though ContentML alone is already fairly usable for denominator structure.

## Test 07: Series and Summation
- XMath success: summation is recognized as `SUMOP`, and lower/upper attachments are preserved visibly.
- XMath failure pattern: the index bounds are still attached through subscript/superscript structure, not explicit binder semantics.
- ContentML success: the summand tree and equation structure are standardized cleanly.
- ContentML failure pattern: summation bounds are represented through ambiguous subscript/superscript operators rather than a true bound-variable structure.
- Combined success: XMath identifies the summation operator, while ContentML keeps the summand arithmetic readable.
- Combined failure pattern: summation index, lower bound, upper bound, and body still need custom unpacking.
- Decision: combined output is best; neither representation alone is sufficient for summation labeling.

## Test 08: Limits
- XMath success: `lim` is recognized as `LIMITOP`, and the target expression tree is preserved clearly.
- XMath failure pattern: the approach condition `x \to 0` or `x \to \infty` is only stored as a subscript payload, not a named semantic relation.
- ContentML success: the target expressions are standardized reasonably well.
- ContentML failure pattern: the approach relation is weakly encoded, with the arrow appearing as a generic identifier-like payload under ambiguous subscript structure.
- Combined success: XMath makes the limit operator explicit, and ContentML keeps the target expression easy to traverse.
- Combined failure pattern: approach variable and approach value still require custom extraction.
- Decision: combined output is best; ContentML alone is too weak for reliable limit labeling.

## Final Decision
- Preferred representation: XMath + Content MathML.
- Why: XMath preserves operator-role information needed for ontology labeling, while Content MathML provides a cleaner structural tree when the parse succeeds.
- Why not XMath alone: it preserves useful clues but is less standardized and still leaves major ambiguities unresolved.
- Why not Content MathML alone: it loses too much useful operator-role information and is especially weak on derivatives, bounds, and approach conditions.
- What this means for the pipeline: keep both representations and design labeling rules around repeated failure patterns, especially powers, derivatives, function application, differential scope, and binder-like structures.
