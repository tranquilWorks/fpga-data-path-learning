# P12 — Size a FIFO from Burst and Service Rates

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths  
**Phase 3:** Streaming architectures  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you size a FIFO from Burst and Service Rates?

## Computational mental model

P11 made a packet a finite sequence of accepted beats whose payload and `last` metadata stay
together. P12 treats a finite group of those words as an aggregate burst and asks how much registered
storage is needed while downstream service removes previously stored words.

The model starts empty. Immediately before edge `n`, `qBefore[n]` words are stored. Departures happen
before admissions for slot accounting, so same-edge dequeue can free capacity, but the FIFO is not
fall-through: new arrivals cannot depart on their arrival edge.

\[
\begin{aligned}
d[n] &= \min(S,qBefore[n]),\\
qAfter[n] &= qBefore[n]-d[n]+a[n],\\
D_{required} &= \max_n qAfter[n].
\end{aligned}
\]

For an empty FIFO, a constant `B`-cycle burst of `A` words/cycle, and guaranteed service capacity
`S` words/cycle, the registered requirement is

\[
D_{required}=A+(B-1)\max(A-S,0).
\]

Compute this requirement with an unbounded reference queue first. A finite trace clipped at its
installed depth cannot prove that the depth was sufficient.

## Deterministic baseline

The baseline offers three words/cycle for eight cycles, guarantees service of one stored word/cycle,
starts empty, and selects 17 words of capacity in a fixed 40-cycle record.

- Offered burst: `8 * 3 = 24` words.
- Lossless occupancy after burst edges: `[3, 5, 7, 9, 11, 13, 15, 17]` words.
- Required depth: 17 words at cycle 8.
- Selected depth and margin: 17 words and zero words.
- Admission: all 24 words; no backpressure request.
- Drain completion: cycle 25.

The initial three arrivals need storage because cycle-one service sees an empty registered FIFO.
Later burst cycles add `A-S=2` words each.

## Two independent sweeps

1. **Burst duration `[1, 2, 4, 6, 8]` cycles:** arrival stays 3 words/cycle, service stays
   1 word/cycle, selected capacity stays 32 words, and the fault is off. Required depths become
   `[3, 5, 9, 13, 17]` words.
2. **Guaranteed service `[0, 1, 2, 3, 4]` words/cycle:** the eight-cycle, three-word/cycle burst,
   selected capacity, and fault state stay fixed. Required depths become `[24, 17, 10, 3, 3]`
   words; completion is `[no drain, 25, 13, 9, 9]` cycles.

The first lever changes how long positive rate imbalance persists. The second changes how quickly
stored work leaves. Reset one before moving the other.

## Deliberately broken case

The broken estimator uses the fall-through expression

\[
D_{broken}=B\max(A-S,0),
\]

which gives 16 words for the baseline. It incorrectly subtracts service from new arrivals on the
same edge. Applied to the declared registered FIFO, depth 16 admits only two of the three words on
cycle 8. Exactly one word is not accepted.

“Not accepted” is a capacity symptom, not unconditional loss. A P10/P11-compliant producer observes
ready low and holds that word, its payload, and its `last` value until a later acceptance. The word is
lost only if the source is unthrottleable or ignores the valid/ready hold obligation.

## Learning flow

1. Read the registered recurrence and make one prediction about depth 16.
2. Reveal cumulative arrivals/departures, then occupancy/depth and baseline metrics.
3. Move only burst duration, observe the required-depth change, read the mechanism, and reset.
4. Move only service rate, observe the required-depth and drain change, then read the mechanism.
5. Enable the fall-through estimator and locate the exact cycle-eight admission failure.
6. Run `interactive`, `run_checks`, answer `checks.md` one prompt at a time, and give the two-sentence
   teach-back.

## Files

- `model.m` — presentation-free unbounded sizing reference and finite registered capacity accounting.
- `experiment.m` — deterministic baseline, two isolated sweeps, labeled metrics, and one broken case.
- `interactive.m` — bounded burst, arrival, service, depth, observation-edge, and fault controls.
- `lesson.m`, `lesson.md`, and `walkthrough.md` — concept-first learner and tutor sequence.
- `run_checks.m` and `checks.md` — recurrence, limits, malformed inputs, recovery, and teach-back.

## Evidence boundary

P01 supplied qualitative burst/occupancy intuition; P10 supplied registered FIFO timing; P11 supplied
finite framed-burst context. P12 is an exact finite-burst sizing exercise, not a repeat of P01's
sinusoidally modulated queue and not a protocol implementation.

The retained model assumes an empty FIFO, one clock, a burst starting on cycle 1, integer aggregate
word rates, fixed guaranteed service, and no second burst before drain. Depth is measured in modeled
words, not bytes, packets, BRAMs, LUTs, or vendor primitive settings. The model omits arbitrary
service phase, width conversion, payload and `last` storage, reset, CDC, RAM-port timing, almost-full
latency, safety margin policy, synthesis, placement, routing, and measured throughput. Static source
and an independent Python oracle can validate the retained contract without proving MATLAB execution,
figure rendering, UI callbacks, numerical fidelity in MATLAB, bench, HIL, field, or production behavior.
