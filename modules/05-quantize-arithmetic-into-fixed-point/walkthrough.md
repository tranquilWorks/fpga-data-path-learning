# Walkthrough: Quantize Arithmetic into Fixed Point

1. Read the guiding question and state the format: one sign bit, `I` integer-magnitude bits, `F` fractional bits, and LSB `Delta = 2^-F`.
2. Before plotting, predict the baseline nearest-rounded output for input `0.31` with an LSB of `0.125`. Make no second prediction.
3. Run only the baseline section of `experiment.m`. Name both unitless amplitude axes, the sample index, and the unitless error axis.
4. Identify the discrete nearest-code mapping, the half-LSB error bound, and the asymmetric two's-complement endpoints.
5. Run sweep 1 with integer-magnitude bits fixed at two. Observe one transition at a time as fractional bits move from zero through eight.
6. Give the mechanism-first explanation: each fractional bit halves LSB spacing and the error bound while adding one word bit; the discrete samples map closer to their inputs and range is sufficient throughout this sweep.
7. Reset fractional bits to three, then run sweep 2 for zero through four integer-magnitude bits.
8. Explain the changed view: endpoint scale expands and overload disappears while LSB spacing and already-in-range outputs remain fixed.
9. Run the deliberately broken wrap case at one integer-magnitude bit and three fractional bits. Compare saturated endpoints with opposite-sign wrapped outputs.
10. State the violated assumption: this datapath specifies saturation, but the broken path discards overflow information modulo the code count.
11. Open `interactive.m`; change only one bounded control and explain the mechanism. The fault control is unavailable when no sample overloads.
12. Run `run_checks.m`, answer `checks.md` one prompt at a time, and give the two-sentence teach-back.

The vector is deterministic and unitless, and word length is a modeled format property. Do not infer measured converter data, spectral noise, coefficient effects, synthesis, physical resources, timing, power, or hardware behavior from these plots.
