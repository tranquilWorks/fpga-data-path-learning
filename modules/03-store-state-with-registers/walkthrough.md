# Walkthrough: Store State with Registers

1. Read the guiding question and state the convention: `D` is immediately before an edge; `Q` is immediately after it.
2. Before plotting, predict the one-stage `Q` after edge 3; make no second prediction.
3. Run only the baseline section of `experiment.m`. Name the clock-cycle axis, 4-bit code axis, binary controls, and invalid reset-fill state.
4. Explain why reset wins at edge 1, why edges 2 through 16 capture, and what remains stored between edges.
5. Run sweep 1 with enable period fixed at 1. Observe one transition at a time as depth moves from 1 through 4.
6. Explain the changed view: each stage after `Q1` adds one enabled-edge delay because it sees the prior stage's pre-edge value.
7. Reset to one stage, then run sweep 2. Compare enable periods 1 through 4 without changing the clock or data trace.
8. Explain the changed view: disabled edges hold `Q`, so captures fall and wall-clock waiting grows while depth stays fixed.
9. Run the deliberately broken three-stage cascade. Compare healthy `[5 13 2]` with broken `[5 5 5]` at edge 4.
10. State the violated assumption: edge-triggered registers sample pre-edge inputs simultaneously; a just-updated value cannot cross several modeled stages on that edge.
11. Open `interactive.m`; choose depth 2 or greater before enabling the fault. Change only one bounded control, explain the mechanism, then reset before another change.
12. Run `run_checks.m`, answer `checks.md` one prompt at a time, and give the two-sentence teach-back.

Validity is simulator bookkeeping, and the broken update is deliberately computational. Do not infer setup/hold margin, propagation, metastability, synthesis, physical resource use, or measured hardware behavior from these plots.
