# P04 — Control Behavior with a Finite-State Machine

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths  
**Phase 1:** Digital logic  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you control Behavior with a Finite-State Machine?

## Computational mental model

P03 stored an arbitrary code in a register. Here that registered code has one of four meanings: `IDLE`, `WAIT`, `DONE`, or `TIMEOUT`. Immediately before rising edge `n`, the controller observes its current state and the inputs `reset`, `start`, `workDone`, and `deadlineExpired`. Immediately after the edge, it exposes the registered next state and Moore outputs:

\[
q[n]=\delta(q[n-1],x[n]),\qquad
busy[n]=[q[n]=WAIT].
\]

`done[n]` and `timeout[n]` similarly decode `DONE` and `TIMEOUT`. The healthy transition policy gives `workDone` priority when completion and deadline arrive together. That inclusive-boundary policy is a declared design choice, not a universal FSM rule.

## Connection to P03

P03's register recurrence explains why current state persists between edges. P04 adds a P02-style combinational next-state decision in front of that state register. The decision depends on both current state and current inputs, so an event that arrives after the FSM has left `WAIT` is ignored rather than interpreted as a second transaction result.

## Learner flow

1. Read the pre-edge input/post-edge state convention and make one prediction for the baseline.
2. Visualize the fixed 16-edge state trace and the input/output timeline.
3. Change only completion delay from one through six cycles while timeout remains eight.
4. Explain why later completion extends `WAIT` and `busy` without changing the successful outcome.
5. Reset completion delay to four, then change only timeout limit from one through eight cycles.
6. Explain why success occurs exactly when completion delay is no greater than the inclusive timeout limit.
7. Reverse the tie priority and diagnose a wrong `TIMEOUT` pulse where `DONE` was specified.
8. Run deterministic checks and give the teach-back in `checks.md`.

## Run the module

From the repository root, use MATLAB:

```matlab
launch_lesson("P04")
run_module_checks("P04")
```

Or enter this folder and run `experiment.m` one `%%` section at a time. Open `interactive.m` for bounded controls and linked state/signal views.

## Levers and observables

- `completionDelay` (`1..8` cycles after start) moves only the deterministic `workDone` input.
- `timeoutLimit` (`1..8` cycles after start) moves only the deterministic `deadlineExpired` input.
- `selectedCycle` (`1..16`) inspects sampled inputs, state before the edge, registered state after it, transition reason, and decoded outputs without changing the trace.
- `brokenPriority` is enabled in the UI only when the delays match; it lets timeout win the contested edge.
- Views show state code versus clock cycles and binary pre-edge inputs/post-edge outputs.
- Metrics report terminal state/cycle, `WAIT` dwell, terminal pulse counts, ignored late events, reference mismatches, and two modeled state bits.

The state codes and two-bit count describe this teaching model's compact encoding. They are not a synthesis result or measured FPGA utilization.

## Artifact and dependency contract

- `model.m` owns the fixed deterministic transition calculation, validation, healthy reference, and metrics without presentation.
- `experiment.m` owns the baseline, two isolated sweeps, labeled plots, and deliberately broken priority.
- `interactive.m` owns bounded `uifigure` controls and immediate state/signal feedback.
- `lesson.m`, `lesson.md`, and `walkthrough.md` own the concept-first sequence.
- `checks.md` and `run_checks.m` own interpretation and executable invariants.
- Dependency: P03. The implementation prefers base MATLAB and has no random, toolbox, external-file, network, process, or hardware dependency.

## Scope and limitations

Completion and deadline delays are synthetic cycle positions, not measured latency or a physical timer. The model assumes all inputs meet the active clock edge cleanly; it does not model asynchronous input synchronization, setup/hold, propagation delay, clock skew, metastability, reset release, synthesis, routing, power, or device behavior. The wrong priority is a deterministic specification error, not physical fault injection. MATLAB execution, figure rendering, UI behavior, numerical fidelity, and physical behavior require separate evidence.
