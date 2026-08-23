# Walkthrough: Control Behavior with a Finite-State Machine

1. Read the guiding question and state the convention: inputs/current state are pre-edge; next state and Moore outputs are post-edge.
2. Before plotting, predict the state and output after cycle 5 for completion delay 3 and timeout 5. Make no second prediction.
3. Run only the baseline section of `experiment.m`. Name the cycle, unitless state-code, and binary signal axes.
4. Explain why start enters `WAIT`, why completion produces one `DONE` edge, and why the late deadline is ignored after recovery to `IDLE`.
5. Run sweep 1 with timeout fixed at eight cycles. Observe one transition at a time as completion delay moves from one through six.
6. Give the mechanism-first explanation: moving `workDone` changes registered `WAIT` residence and busy duration, not the state set or deadline.
7. Reset completion delay to four, then run sweep 2 for timeout limits one through eight.
8. Explain the changed view: the first event sampled in `WAIT` selects the outcome, and the declared inclusive boundary accepts a cycle-6 completion.
9. Run the deliberately broken equal-delay case. Compare healthy `DONE` with broken `TIMEOUT` at cycle 6.
10. State the violated assumption: completion must win a deadline tie under this controller's approved transition table.
11. Open `interactive.m`; change only one bounded control and explain the mechanism. Set both timing levers equal before enabling the fault.
12. Run `run_checks.m`, answer `checks.md` one prompt at a time, and give the two-sentence teach-back.

The delay pulses are deterministic stimulus and the state encoding is illustrative. Do not infer measured latency, timer circuitry, asynchronous input safety, setup/hold, metastability, synthesis, physical resource use, or hardware behavior from these plots.
