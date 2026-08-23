# P08 — Generate a Numerically Controlled Oscillator

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths  
**Phase 2:** Numeric hardware  
**Status:** implemented

## Guiding question

What inputs, observable effects, and failure modes matter when you generate a Numerically Controlled Oscillator?

## Computational mental model

Picture a 12-bit clock face with 4096 positions. At every sample, an accumulator advances by an integer tuning word `K` and wraps modulo 4096. The accumulator remembers phase; a lookup table turns the most-significant `P` phase bits into normalized sine and cosine values.

With sample index `n` beginning at zero, initial phase code `phi0`, accumulator width `B=12`, and an explicitly assumed sample clock `f_s=100 MHz`,

\[
\begin{aligned}
\phi[n] &= (\phi_0+nK)\bmod 2^{12},\\
f_\text{out} &= \frac{K}{2^{12}}f_s,\\
a[n] &= \left\lfloor\frac{\phi[n]}{2^{12-P}}\right\rfloor.
\end{aligned}
\]

The accumulator keeps all 12 bits. Phase is truncated only after accumulation to form the lookup address `a[n]`. One tuning-word code therefore represents `100 MHz / 4096 = 24.4140625 kHz` under the teaching clock, independent of `P`.

## Deterministic baseline

The baseline uses `K=411`, `P=8`, and initial phase code zero. It requests `10.0341796875 MHz` and advances `36.123046875 degrees/sample`. The model counts 411 wraps across 4096 next-state transitions, including the terminal transition from stored sample 4095 to unrecorded sample 4096; the 4096 stored states therefore show 410 adjacent wrap discontinuities. Eight address bits select 256 phase entries with `1.40625 degree` steps. Because odd `K=411` visits all 4096 accumulator codes, the record exposes every discarded four-bit phase remainder; the maximum lookup phase error is `1.318359375 degrees`.

The output is a normalized floating-point sine/cosine pair from an explicit base-MATLAB table. No amplitude quantizer, DAC, analog reconstruction filter, clock jitter, HDL, or physical oscillator is modeled.

## Learner flow

1. Read the accumulator and lookup equations, then make one prediction about where the full tuning word is applied.
2. Visualize the baseline accumulator code, quadrature waveform, phase truncation error, and deterministic record spectrum.
3. Hold `P=8` fixed and sweep `K` through DC, the minimum nonzero frequency step, representative tones, quarter-rate, and the highest modeled setting below Nyquist.
4. Explain why output frequency, phase advance, wrap count, and accumulator period change while lookup entries remain fixed.
5. Reset to odd `K=411`, then sweep `P=3..12`.
6. Explain why lookup entries double and phase/waveform error shrinks while full-width phase, tuning resolution, and output frequency stay fixed.
7. At `K=411`, `P=8`, deliberately clear the tuning word's low four bits before accumulation. Diagnose the resulting `K=400` tone, `-268.5546875 kHz` frequency error, and 256-sample accumulator period.
8. Run deterministic checks and give the two-sentence teach-back in `checks.md`.

## Run the module

From the repository root, use MATLAB:

```matlab
launch_lesson("P08")
run_module_checks("P08")
```

Or enter this folder and run `experiment.m` one `%%` section at a time. Open `interactive.m` for bounded controls and linked phase/spectrum views.

## Levers and observables

- `tuningWord` (`0..2047` phase codes/sample) controls phase advance and the modeled frequency from DC to one code below Nyquist.
- `phaseAddressBits` (`3..12` bits) controls `2^P` lookup entries and phase truncation without changing the healthy accumulator recurrence.
- `initialPhaseCode` (`0..4095`) rotates the starting phase without changing tuning, frequency, table size, record allocation, or the full-transition wrap total. It can move one wrap between the stored-state discontinuity count and the terminal transition.
- `brokenIncrementTruncation` clears the same low bits from `K` that a healthy design discards only when forming the lookup address.
- Accumulator and address axes use unsigned phase codes; phase steps and errors use degrees; sample time uses microseconds under the assumed clock.
- Frequency axes use MHz under the assumed 100 MHz sample clock. The record spectrum is normalized to its own modeled carrier in dBc. The model reports finite SFDR only for spurs above its declared `-240 dBc` numerical floor; if none is resolved, it reports `Inf` rather than interpreting floating-point FFT residue as a spur.
- Lookup size is counted in phase entries and paired sine/cosine values. It is not a BRAM, ROM primitive, area, power, or timing report.

## Connection to P07

P07 separated raw operations, resource allocation, and complete useful throughput. P08 applies the same separation to numeric precision: the 12-bit accumulator owns tuning resolution, while `P` lookup-address bits trade modeled table entries for phase fidelity. Reusing fewer lookup entries may be a resource choice, but it must not silently delete the accumulator bits that carry the requested frequency.

## Artifact and dependency contract

- `model.m` owns validated deterministic recurrence, explicit lookup construction, phase/waveform errors, spectrum metrics, fault behavior, and fixed bounds without presentation or external state.
- `experiment.m` owns the baseline, two isolated sweeps, labeled figures and metrics, and the broken increment-truncation case.
- `interactive.m` owns bounded `uifigure` controls with immediate phase and spectrum feedback.
- `lesson.m`, `lesson.md`, and `walkthrough.md` own the concept-first teaching sequence.
- `checks.md` and `run_checks.m` own interpretation prompts and executable invariants.
- Dependency: P07. The implementation prefers base MATLAB and has no random, toolbox, external-file, network, process, asynchronous, or hardware dependency.

## Scope and limitations

This is a deterministic discrete-time teaching model. Its 100 MHz clock is an assumption used for unit conversion, not an achieved or measured clock. The floating-point lookup values do not model amplitude quantization, ROM coding, interpolation, DAC resolution, zero-order hold, analog images, reconstruction filtering, jitter, phase noise, clock-domain crossing, reset synchronization, streaming handshakes, resource sharing, power, synthesis, placement, or timing closure. Modeled SFDR describes one coherent synthetic record above a declared numerical floor, not converter or laboratory performance. MATLAB execution, figures, UI behavior, synthesis, bench, HIL, field, and production behavior require separate retained evidence.
