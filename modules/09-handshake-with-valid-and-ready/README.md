# P09 — Handshake with Valid and Ready

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths  
**Phase 3:** Streaming architectures  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you handshake with Valid and Ready?

## Computational mental model

A producer owns `valid` and `data`; a consumer owns `ready`. Immediately before rising edge `n`, both sides expose their signals. Exactly one token transfers at that edge only when both sides agree:

\[
\text{transfer}[n]=\text{valid}[n]\land\text{ready}[n].
\]

`valid=1` alone means “this payload is offered,” and `ready=1` alone means “the consumer could accept.” Neither statement by itself moves data. If `valid=1` while `ready=0`, the producer must keep `valid`, the payload, and its token identity stable until an accepting edge. Once a transfer occurs, either side may change its own signal for the next cycle.

The eight payloads are the first eight 12-bit phase codes from P08's `K=411` recurrence: `[0, 411, 822, 1233, 1644, 2055, 2466, 2877]`. Here they are finite, recognizable token labels. This lesson does not claim that a free-running NCO clock pauses; a continuously sampled source would need an architecture that preserves every sample when downstream service stops.

## Deterministic baseline

The baseline inserts one source bubble between successive accepted tokens and deasserts `ready` for cycles 5 through 7. Transfers occur at cycles `[1, 3, 8, 10, 12, 14, 16, 18]`. Token 822 is offered continuously from cycle 5 through cycle 8 and waits three cycles; it is captured only at cycle 8. All eight payloads arrive once, in order. Across the active 18-cycle window there are eight transfers, three stalled-valid cycles, and seven source bubbles, for `8/18` transfers per cycle through completion.

## Learner flow

1. Read the ownership and transfer rules, then predict whether token 822 transfers at cycle 5 when `valid=1` and `ready=0`.
2. Visualize the baseline signals, held payload, cumulative transfers, and per-token wait.
3. Hold the consumer always ready and sweep source gap from zero through three cycles.
4. Explain why source bubbles move the completion edge without changing payload values or order.
5. Reset to a continuously valid source, then sweep the ready-low interval from zero through six cycles.
6. Explain why each additional consumer stall adds one stalled-valid cycle and one completion cycle while the producer holds one token.
7. Deliberately let the producer advance without `ready` during a three-cycle stall. Diagnose three dropped tokens and three hold-rule violations.
8. Run deterministic checks and give the two-sentence teach-back in `checks.md`.

## Run the module

From the repository root, use MATLAB:

```matlab
launch_lesson("P09")
run_module_checks("P09")
```

Or enter this folder and run `experiment.m` one `%%` section at a time. Open `interactive.m` for bounded controls and linked signal/payload views.

## Levers and observables

- `sourceGapCycles` (`0..3` cycles) inserts idle producer cycles only after a successful transfer. It changes offered-token spacing and completion rate, not consumer readiness or payload identity.
- `readyStallCycles` (`0..6` cycles) deasserts consumer `ready` beginning at cycle 5. It changes stalled-valid time, token wait, and completion cycle, not the source's ordered payload list.
- `brokenAdvanceWithoutReady` consumes the producer's local token on every stalled offer even though no transfer occurred. The healthy reference remains alongside the broken trace.
- Cycle and wait axes use clock cycles. `valid`, `ready`, `transfer`, drop, and violation signals are binary. Payloads are unsigned 12-bit phase codes used as labels. Rate is modeled transfers per cycle through the final healthy transfer.
- The fixed record is 35 cycles and eight tokens. The maximum healthy control combination completes on cycle 35, so every loop and trace has a declared bound.

## Connection to P08

P08 made the sample value and phase recurrence visible. P09 adds a separate ownership question: when does one already-produced payload become accepted by another block? The handshake does not alter a payload's numeric meaning; it controls whether that exact token crossed the interface on a particular edge.

## Artifact and dependency contract

- `model.m` owns validated deterministic signal recurrence, token accounting, reference/fault paths, and fixed bounds without presentation or external state.
- `experiment.m` owns the baseline, two isolated sweeps, labeled figures and metrics, and the broken advance-without-ready case.
- `interactive.m` owns bounded `uifigure` controls and immediate signal/payload feedback.
- `lesson.m`, `lesson.md`, and `walkthrough.md` own the concept-first sequence.
- `checks.md` and `run_checks.m` own interpretation prompts and executable invariants.
- Dependency: P08. The implementation prefers base MATLAB and has no random, toolbox, external-file, network, process, asynchronous, or hardware dependency.

## Scope and limitations

This is a deterministic, single-clock, edge-sampled teaching model. It assumes signal timing is clean before each edge and omits reset, clock-domain crossing, metastability, combinational ready paths, skid buffers, FIFO depth, packet boundaries, continuously generated sample loss, arbitration, deadlock across connected blocks, HDL, synthesis, placement, routing, and timing closure. The 12-bit payload hold width and fixed trace sizes are model quantities, not measured FPGA registers, utilization, throughput, or timing. MATLAB execution, figure rendering, UI behavior, protocol integration, bench, HIL, field, and production behavior require separate retained evidence.
