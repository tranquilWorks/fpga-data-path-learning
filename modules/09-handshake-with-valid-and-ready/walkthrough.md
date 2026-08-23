# Walkthrough: Handshake with Valid and Ready

1. Read the guiding question and connect to P08: its phase codes are payload labels here, while the handshake decides when each token is accepted.
2. State the edge convention and equation: signals are pre-edge; `transfer[n]=valid[n] && ready[n]` at edge `n`.
3. Before plotting, predict whether valid token 822 transfers at cycle 5 while ready is low. Make no second prediction.
4. Run the baseline sections of `experiment.m` one at a time. Name clock cycles, binary controls, unsigned 12-bit payload codes, token ordinals, waits, and transfers/cycle.
5. Observe transfers `[1,3,8,10,12,14,16,18]`; token 822 is unchanged on cycles 5 through 8 and waits three cycles.
6. Run sweep 1 with ready always high. Observe completion cycles `[8,15,22,29]` as source gap moves from zero through three.
7. Explain the changed view: seven between-token gaps add `7*g` source bubbles but do not change readiness, data, order, or count.
8. Reset source gap to zero, then run sweep 2 for ready-low durations zero through six.
9. Explain why completion and maximum wait each grow by one cycle per added stall while every token remains held and accepted once.
10. Run the deliberately broken zero-gap, three-stall case. Compare healthy transfers `[1,2,3,4,8,9,10,11]` with broken transfers `[1,2,3,4,8]`.
11. Name tokens 1644, 2055, and 2466 as dropped, identify hold violations on cycles 6 through 8, and state the violated `valid && ready` advance rule.
12. Confirm the fault is inert with no stalled-valid edge. Then open `interactive.m`, change one bounded control at a time, run `run_checks.m`, and give the two-sentence teach-back.

The cycle rate, 12-bit hold width, and fixed trace sizes are deterministic model quantities. Do not infer continuous-source buffering, CDC safety, setup/hold behavior, combinational-loop freedom, synthesis, timing, FPGA utilization, bench throughput, HIL, or field behavior from these views.
