# Checks: Build Combinational Logic from Truth Tables

Ask and answer one prompt at a time.

## Observation check

Why do addresses `3`, `5`, `6`, and `7` assert in the 2-of-3 baseline? Answer from their bits, not from the shape of the plot.

## Lever-isolation check

What changes when `k` moves from `2` to `3`, and what stays fixed? After resetting `k`, what changes when `p` moves from `0.5` to `0.2`, and what stays fixed?

## Limiting-case check

Explain why `k=1` produces OR with seven asserted rows, why `k=3` produces AND with one asserted row, and why majority gives `P(Y=1)=0` at `p=0` and `1` at `p=1`.

## Broken-case check

With LUT address `6` flipped, name the exact mismatched input and violated assumption. Why could three hand-picked passing examples still give false confidence?

## Interpretation and transfer check

Why is an asserted-row fraction not generally a runtime probability? Give one datapath decision that could use a small truth table, and say which input meanings and polarities would have to be documented.

## Executable check

Run in MATLAB:

```matlab
run_checks
```

All assertions must pass before completion. They cover exhaustive rows, the independent Boolean equation, limiting cases, both sweeps, malformed inputs, the flipped LUT row, fixed resource bounds, deterministic recovery, and call isolation.

## Teach-back

In two sentences, answer: “What inputs, observable effects, and failure modes matter when you build Combinational Logic from Truth Tables?” Sentence one must explain how current input bits select an output. Sentence two must explain how exhaustive comparison exposes an incorrect row and distinguish mapping changes from row-frequency changes.
