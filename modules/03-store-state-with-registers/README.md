# P03 — Store State with Registers

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths  
**Phase 1:** Digital logic  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you store State with Registers?

## Computational mental model

Observe `D` immediately before rising edge `n` and `Q` immediately after it. A synchronous reset has priority, an enabled register captures, and a disabled register holds:

\[
Q_1[n] =
\begin{cases}
0, & R[n]=1,\\
D[n], & R[n]=0\;\text{and}\;E[n]=1,\\
Q_1[n-1], & R[n]=0\;\text{and}\;E[n]=0.
\end{cases}
\]

For enabled stage `s>1`, simultaneous edge sampling means

\[
Q_s[n]=Q_{s-1}[n-1].
\]

Every stage therefore remembers one 4-bit code between edges. Each stage after `Q1` adds one enabled-edge delay; disabled edges add wall-clock waiting because no stage advances.

## Connection to P02

P02's truth table produced an output from current input bits with no stored history. That combinational result can drive `D`; P03 decides at which clock edge it becomes remembered `Q`, when it must hold, and how prior stage state advances. This is the transition from a current-input mapping to sequential logic.

## Learner flow

1. Read the pre-edge/post-edge convention and make one prediction for the one-register baseline.
2. Visualize reset, enable, input `D`, stored output `Q`, and output validity across 16 deterministic edges.
3. Change only stage count from 1 through 4; observe additional enabled-edge delay.
4. Reset to one stage, change only enable period from 1 through 4; observe captures become holds without changing clock frequency.
5. Explain both changed views from the register recurrence.
6. Run the deliberately broken cascade and diagnose an output that becomes valid too early.
7. Run deterministic checks and give the teach-back in `checks.md`.

## Run the module

From the repository root, use MATLAB:

```matlab
launch_lesson("P03")
run_module_checks("P03")
```

Or enter this folder and run `experiment.m` one `%%` section at a time. Open `interactive.m` for bounded controls and two linked views.

## Levers and observables

- `stageCount` (`1..4`) changes the number of 4-bit data registers and the additional enabled-edge delay from `Q1` to the last stage.
- `enablePeriod` (`1..4` cycles) changes which edges capture or shift. It does not change the clock frequency or stage count.
- `selectedCycle` (`1..16`) exposes state immediately before and after one edge.
- `brokenCascade` is available for depth 2 or greater and deliberately reuses just-updated stage values on the same edge.
- Views show unsigned 4-bit codes versus clock cycles and the stored code in every stage.
- Metrics report captured and held edges, first valid output cycle, modeled data-storage bits, early-valid cycles, and mismatches against the simultaneous-transfer reference.

`validAfter` is simulator bookkeeping that distinguishes reset-fill bits from an accepted data token. It is not included in `dataStorageBitCount` and is not an FPGA resource measurement.

## Artifact and dependency contract

- `model.m` owns the fixed 16-edge deterministic recurrence, validation, and reference comparison without presentation.
- `experiment.m` owns the baseline, two isolated sweeps, labeled plots, metrics, and broken case.
- `interactive.m` owns bounded `uifigure` controls and immediate timing/state feedback.
- `lesson.m`, `lesson.md`, and `walkthrough.md` own the concept-first learning sequence.
- `checks.md` and `run_checks.m` own interpretation and executable invariants.
- Dependency: P02. The implementation prefers base MATLAB and has no random, toolbox, external-file, network, process, or hardware dependency.

## Scope and limitations

The deliberately broken cascade is an incorrect computational update rule used to reveal the simultaneous pre-edge sampling contract. It is not a simulation of physical values propagating through multiple flip-flops during one edge. The model assumes input, reset, and enable meet hardware setup/hold requirements; it does not model clock waveforms, propagation delay, setup/hold violations, clock skew, metastability, synthesis, routing, power, physical reset structures, or measured FPGA utilization. Output validity is retained model provenance, not a modeled valid-data register. MATLAB execution, figure rendering, UI behavior, and physical behavior require separate evidence.
