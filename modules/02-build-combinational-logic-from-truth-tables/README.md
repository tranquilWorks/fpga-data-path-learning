# P02 — Build Combinational Logic from Truth Tables

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths  
**Phase 1:** Digital logic  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you build Combinational Logic from Truth Tables?

## Computational mental model

Three current input bits form a zero-based LUT address:

\[
\text{address}=4A+2B+C.
\]

That address selects exactly one truth-table output. The baseline is a 2-of-3 voter,

\[
Y=(A\land B)\lor(A\land C)\lor(B\land C),
\]

whose output vector for addresses `000` through `111` is `[0 0 0 1 0 1 1 1]`. The exhaustive table and the independently written equation must agree on all eight rows.

## Connection to P01

P01 showed words moving through a pipeline and a FIFO whose occupancy retained history. P02 looks inside one current word and makes a decision from its present bits. This combinational model has no stored history; P03 introduces registers explicitly.

## Learner flow

1. Read the address convention and make one prediction for input `011`.
2. Visualize the exhaustive 2-of-3 baseline.
3. Change only required-HIGH threshold `k`; observe that the mapping changes.
4. Reset to `k=2`, change only input-HIGH probability `p`; observe that row frequency changes while the mapping does not.
5. Explain each change from the truth table and equations.
6. Flip LUT address `6` (`110`) and locate the single mismatch.
7. Run deterministic checks and give the teach-back in `checks.md`.

## Run the module

From the repository root, use MATLAB:

```matlab
launch_lesson("P02")
run_module_checks("P02")
```

Or enter the module folder and run `experiment.m` one `%%` section at a time. Open `interactive.m` to use the bounded controls.

## Levers and observables

- `requiredHigh` (`k=1..3`) changes the logic function from OR to majority to AND.
- `inputHighProbability` (`p=0..1`) weights how often each row occurs, assuming independent inputs with the same `p`; it does not change the truth table.
- `selectedAddress` (`0..7`) highlights one binary input row.
- `faultAddress` (`-1` disabled, `0..7` enabled) flips one LUT entry for diagnosis.
- Views show binary output versus unitless input address and output-HIGH probability versus unitless `p`.
- Metrics report asserted rows out of eight, current specified/LUT outputs, mismatch count, and weighted mismatch probability.

## Artifact and dependency contract

- `model.m` owns deterministic fixed-size calculations and input validation.
- `experiment.m` owns the baseline, two independent sweeps, plots, metrics, and broken case.
- `interactive.m` owns the `uifigure` controls and immediate feedback.
- `lesson.m`, `lesson.md`, and `walkthrough.md` own the concept-first learning sequence.
- `checks.md` and `run_checks.m` own interpretation and executable invariants.
- Dependency: P01. The implementation uses base MATLAB only, with no random data, toolbox solver, external file, network, or hardware dependency.

## Scope and limitations

The probability view assumes independent, identically distributed input bits. Correlated inputs require different row weights. Asserted-row fraction equals runtime output frequency only for uniformly distributed rows. The model is a static Boolean/LUT abstraction: it does not model gate propagation delay, hazards, metastability, FPGA resource mapping, clocks, voltage, or physical faults. “Combinational” means no stored logical state, not physically instantaneous behavior.
