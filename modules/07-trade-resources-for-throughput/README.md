# P07 — Trade Resources for Throughput

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths  
**Phase 2:** Numeric hardware  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you trade Resources for Throughput?

## Computational mental model

P06 sent one ordered fixed-point product stream through one pipelined path. P07 keeps P06's two-cycle product-pipeline latency and product-code scaling, then asks how six frames of eight independent products share or replicate those pipelines.

Let `R` be the number of multiplier lanes, `A` the offered frame interval in cycles per frame, `W=8` the products in each frame, and `L=2` the lane latency. A lane can accept one product each cycle. A healthy scheduler reserves

\[
G=\left\lceil\frac{W}{R}\right\rceil
\]

issue cycles per frame. For frame `j` and zero-based product `k`,

\[
\begin{aligned}
a_j &= 1+(j-1)A,\\
s_j &= \max(a_j,s_{j-1}+G),\\
i_{j,k} &= s_j+\left\lfloor\frac{k}{R}\right\rfloor,\\
\ell_{j,k} &= 1+(k\bmod R),\\
r_{j,k} &= i_{j,k}+L.
\end{aligned}
\]

Under this declared non-preemptive, frame-at-a-time policy, the complete-frame capacity is `1/G` frames per cycle. The raw lanes accept `R` products per cycle, or `R/8` frame-equivalents of work per cycle, but an idle lane in a partial final group does not accept work from the next frame. Packing utilization converts that raw work rate into the non-preemptive frame capacity. The scheduled rate is then limited by both source spacing and that capacity:

\[
T=\frac{1}{\max(A,G)}\quad\text{frames/cycle}.
\]

## Deterministic baseline

The baseline uses two multiplier lanes and one frame every four cycles. Eight products require `G=4` issue cycles, so the six frames arrive and start on edges `[1,5,9,13,17,21]` and their last product results appear on edges `[6,10,14,18,22,26]`. Every lane slot is useful, no frame waits, and the scheduled rate is `0.25` frame/cycle.

The input codes are circular shifts of P06's `[3,-2,5,1,-4,6,-1,4]`; coefficient codes remain `[2,4,-1,3,2,-2,5,5]`. The exact product-vector checksum codes are `[-9,72,23,-16,69,-6]`. A checksum is only a diagnostic in this module—the modeled datapath output is the eight-product vector plus eight valid bits. No uncounted adder or reduction tree is implied.

## Learner flow

1. Read the capacity equation and make one prediction for the two-lane baseline.
2. Visualize product issues by lane, frame arrival/start/completion edges, and one complete output vector.
3. Hold the offered interval at one cycle and sweep multiplier lanes from one through eight.
4. Explain the ceiling plateaus: four through seven lanes still need two issue cycles, with different numbers of idle final-group slots.
5. Reset to two lanes and sweep the offered interval from one through eight cycles per frame.
6. Explain why demand faster than capacity creates finite-queue wait, while demand slower than capacity leaves lanes supply-limited.
7. At three lanes and a two-cycle source interval, replace ceiling division with floor division. Diagnose missing operations 7 and 8, incomplete output vectors, wrong diagnostic checksums, and the false 50 Mframe/s claim.
8. Run deterministic checks and give the two-sentence teach-back in `checks.md`.

## Run the module

From the repository root, use MATLAB:

```matlab
launch_lesson("P07")
run_module_checks("P07")
```

Or enter this folder and run `experiment.m` one `%%` section at a time. Open `interactive.m` for bounded controls and linked schedule/product views.

## Levers and observables

- `resourceUnits` (`1..8` modeled multiplier lanes) changes `G`, product-pipeline storage, packing utilization, queue wait, latency, and capacity.
- `offeredFrameInterval` (`1..8` cycles/frame) changes demand and queueing without changing lane count, product codes, or capacity.
- `selectedFrame` (`1..6`) changes only the inspected product vector.
- `brokenFloorSchedule` is enabled only when eight does not divide evenly by the lane count. It exposes an under-allocation fault rather than a different multiplication rule.
- Schedule axes use clock edges in cycles, lane indices as modeled multipliers, frame intervals in cycles/frame, and rates in frames/cycle.
- A declared 100 MHz teaching assumption converts normalized rate to Mframes/s. It is not an achieved, constrained, synthesized, or measured clock.
- Product axes use operation index and signed integer product code; scaled product values use the P06 LSB of `1/16`.

## Artifact and dependency contract

- `model.m` owns deterministic product generation, bounded scheduling, queue metrics, coverage validity, and validation without presentation.
- `experiment.m` owns the baseline, two isolated sweeps, labeled plots, and broken floor-division case.
- `interactive.m` owns bounded `uifigure` controls and immediate schedule/product feedback.
- `lesson.m`, `lesson.md`, and `walkthrough.md` own the concept-first sequence.
- `checks.md` and `run_checks.m` own interpretation and executable invariants.
- Dependency: P06. The implementation prefers base MATLAB and has no random, toolbox, external-file, network, process, asynchronous, or hardware dependency.

## Scope and limitations

This is a deterministic cycle-level scheduler for ideal, independent product lanes and a finite lossless input queue. It does not model multiplier internals, mux/control/routing cost, coefficient storage, memory bandwidth, a reduction network, backpressure, FIFO depth, reset protocol, clock-domain crossing, power, or timing closure. Modeled lanes and pipeline-storage bits are not DSP slices, logic cells, registers, or utilization reports. Replicating lanes is not proof that the assumed 100 MHz remains achievable. Checksums help reveal missing products but are not a modeled hardware sum. MATLAB execution, figures, UI behavior, synthesis, bench, HIL, field, and production behavior require separate evidence.
