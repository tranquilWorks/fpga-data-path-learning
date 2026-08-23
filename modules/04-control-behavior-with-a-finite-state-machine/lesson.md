# Lesson: Control Behavior with a Finite-State Machine

## Guiding question

What inputs, observable effects, and failure modes matter when you control Behavior with a Finite-State Machine?

## Mental model

An FSM is a state register plus a next-state decision and output decode. Draw a boundary at each rising edge: inputs and `stateBefore[n]` are pre-edge facts; `stateAfter[n]` is the post-edge value that the register preserves:

\[
stateAfter[n]=\delta(stateBefore[n],reset[n],start[n],workDone[n],deadlineExpired[n]).
\]

This controller uses `IDLE`, `WAIT`, `DONE`, and `TIMEOUT`. Its Moore outputs depend only on registered post-edge state:

\[
busy=[q=WAIT],\qquad done=[q=DONE],\qquad timeout=[q=TIMEOUT].
\]

## Connection to P03

P03 showed a register storing a code and advancing only at an edge. P04 gives that code behavioral meaning. A P02-style combinational decision maps current state plus current inputs to next state; the P03-style register remembers that choice. State therefore supplies the history that a current-input truth table alone cannot.

## Learning cycle

Read the edge convention, visualize the baseline, move one lever, inspect the changed view, and then read the mechanism-first explanation. Reset before moving the second lever so response timing and timeout policy remain distinct.

## One prediction before the baseline

Reset occurs at cycle 1 and start at cycle 2. With completion delay 3 and timeout limit 5, predict the post-edge state and Moore output at cycle 5. Then inspect the baseline once. Make no second prediction; subsequent prompts ask you to observe and explain.

## Baseline

The trace has 16 rising edges. `start` moves `IDLE` to `WAIT` at cycle 2. `workDone` arrives at cycle 5, so post-edge state becomes `DONE` and the one-cycle `done` output is HIGH. Cycle 6 returns to `IDLE`. The deadline pulse at cycle 7 is late and is ignored because deadline has meaning only while current state is `WAIT`.

The state axis uses numeric plot locations only so MATLAB can draw the trace. The code ordering is not physical distance, and the two modeled encoding bits are not synthesized utilization.

## Lever 1: completion delay

Hold timeout limit at eight cycles and sweep completion delay from one through six. Terminal cycles become `3..8`, and `WAIT`/`busy` lasts `1..6` cycles. Every case succeeds because completion remains earlier than the fixed deadline.

Mechanism first: moving `workDone` changes how many edges the registered state remains `WAIT`. It does not change the state set, start pulse, timeout limit, or transition priority.

## Lever 2: timeout limit

Reset completion delay to four cycles and sweep timeout limit from one through eight. Limits one, two, and three produce `TIMEOUT`; limits four through eight produce `DONE`. Terminal cycles are `[3 4 5 6 6 6 6 6]`.

Mechanism first: the first meaningful event sampled while in `WAIT` selects the terminal state. At limit four, completion and expiration coincide. The declared healthy policy checks completion first, so an on-deadline result succeeds. Another system may choose a different policy, but it must specify and verify it.

## Deliberately broken case

Set completion delay and timeout limit to four, then reverse the transition priority. Both inputs are HIGH at cycle 6. The healthy FSM enters `DONE`; the broken FSM enters `TIMEOUT`. The wrong timeout lasts exactly one terminal edge, and both traces recover to `IDLE` at cycle 7.

The violated assumption is precise: the approved transition table says `workDone` wins a simultaneous deadline event. This is a control-specification fault, not physical fault injection or a timing, metastability, or propagation simulation.

## Common mistakes

- Discussing state without saying whether it is before or after the active edge.
- Treating `workDone` or deadline as globally active; late pulses are ignored outside `WAIT`.
- Assuming numerical state-code order has behavioral meaning.
- Calling `busy` an independent register here; it is a Moore decode of registered `WAIT`.
- Calling completion-at-deadline behavior universal rather than an explicit priority policy.
- Calling synthetic completion delay measured hardware latency or the two-bit encoding measured resource use.
- Inferring asynchronous safety, setup/hold margin, metastability, timing closure, or FPGA behavior from this edge-level model.

## Completion standard

Run `run_checks.m`, answer `checks.md` one prompt at a time, diagnose the priority symptom, and give the requested two-sentence teach-back without explaining MATLAB syntax.
