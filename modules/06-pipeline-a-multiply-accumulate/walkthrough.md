# Walkthrough: Pipeline a Multiply-Accumulate

1. Read the guiding question and state the numerical contract: signed `W=4`, `I=1` (sign excluded), `F=2` operands produce product and accumulator codes with four fractional bits and an LSB of `1/16`.
2. State the cycle convention: `L` is only the number of product-delay registers, rows are post-edge observations, and the accumulator update has no separately modeled adder-register delay.
3. Before plotting, predict the accumulation edge for token 1 offered before edge 1 with `L=2`. Make no second prediction.
4. Run only the baseline section of `experiment.m`. Name the clock-edge, product-value, binary-valid, and running-result axes and their units.
5. Identify the two-edge shift between offered and accumulated products, the equally shifted valid row, prefix codes `[6,-2,-7,-4,-12,-24,-29,-9]`, and the final value `-0.5625`.
6. Run sweep 1 with input period fixed at one cycle. Observe one transition at a time as product stages move from zero through four.
7. Give the mechanism-first explanation: every stage delays product, valid, and token identity together by one edge and adds modeled storage, while order, event spacing, and final arithmetic remain fixed.
8. Reset to two product stages, then run sweep 2 for input periods one through four cycles per product.
9. Explain the changed view: bubbles increase accumulation-event spacing and completion edge, while first-product latency, ordered products, binary point, and final sum remain fixed.
10. Run the deliberately broken valid-bypass case at `L=2`, period one. Compare the plausible broken valid cadence with the actual product tokens and the healthy running sum.
11. State the violated assumption and symptom: valid/token identity did not receive the product delay, so two empty cycles and six stale associations are counted while tail tokens 7 and 8 are dropped; the result freezes at `-1.5` instead of `-0.5625`.
12. Open `interactive.m`; change only one bounded control and explain the mechanism. Confirm that the fault clears and disables at the direct `L=0` limit, then run `run_checks.m`, answer `checks.md` one prompt at a time, and give the two-sentence teach-back.

The vectors and cycle schedule are deterministic teaching data. Do not infer HDL equivalence, a pipelined accumulator feedback path, achieved initiation rate, timing improvement, synthesis resources, measured converter behavior, or physical validation from these views.
