# Walkthrough: Build Combinational Logic from Truth Tables

1. Read the guiding question and the `address=4A+2B+C` convention.
2. Before plotting, predict the 2-of-3 output for `ABC=011`; make no second prediction.
3. Run only the baseline section of `experiment.m`. Name the unitless address axis and binary output axis.
4. Confirm that all eight rows appear and explain why addresses `3`, `5`, `6`, and `7` assert.
5. Run sweep 1 with `p=0.5`. Observe one transition at a time from OR to majority to AND.
6. Explain the changed view: `k` changes the specified mapping and the asserted-row count becomes `7`, `4`, then `1`.
7. Reset to `k=2`, then run sweep 2. Compare `p=0.2`, `0.5`, and `0.8` without changing `k`.
8. Explain the changed view: row weights and `P(Y=1)` change, but the eight output bits do not.
9. Run the deliberately broken case. Identify address `6` (`110`) before reading the printed mismatch.
10. State the violated assumption: every reachable LUT entry must match its specified truth-table row.
11. Open `interactive.m`; change only one bounded control, explain the mechanism, then reset before another change.
12. Run `run_checks.m`, answer `checks.md` one prompt at a time, and give the two-sentence teach-back.

The probability curve assumes independent inputs sharing one HIGH probability. Do not generalize it to correlated inputs, and do not infer propagation delay, glitches, or hardware timing from this static model.
