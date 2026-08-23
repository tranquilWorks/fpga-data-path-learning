# Checks: Generate a Numerically Controlled Oscillator

What inputs, observable effects, and failure modes matter when you generate a Numerically Controlled Oscillator?

Ask and answer one prompt at a time.

## Observation check

For the `K=411`, `P=8`, `phi0=0` baseline, identify accumulator width and modulus, sample-zero convention, frequency resolution, requested frequency, phase advance, record length, wrap count, lookup entries and step, maximum phase error, and the first phase and address codes. Explain why 4096 modeled next-state transitions include the terminal transition to unrecorded sample 4096, producing 411 counted wraps but only 410 discontinuities between stored states. Which quantities are assumptions or modeled values rather than measured hardware facts?

## Lever-isolation check

What changes when `K` moves from DC through the highest setting below Nyquist while `P=8` stays fixed? After resetting to `K=411`, what changes when `P` moves from 3 through 12, and which accumulator, frequency, clock, initial-phase, and record facts remain fixed?

## Limiting-case check

Explain `K=0`, the minimum nonzero `K=1`, quarter-rate `K=1024`, a tuning word with a common factor with 4096, and the full-address `P=12` case. Why does an odd tuning word visit every phase code? Why does adding one lookup address bit double modeled table entries without changing frequency resolution? At `K=411`, why can moving `phi0` from 410 to 411 move one wrap from the terminal transition into the stored-state discontinuity count without changing the 411-wrap total or frequency?

## Broken-case check

At `K=411` and `P=8`, why does premature increment truncation apply `K=400`? Name the “accumulate full precision, truncate only for lookup” boundary, calculate the negative eleven-code and `-268.5546875 kHz` error, and explain why the 256-sample broken period and shifted carrier identify tuning loss rather than ordinary lookup phase quantization.

## Interpretation and transfer check

Connect P07's distinction between resources and useful behavior to the accumulator-width versus lookup-width boundary. Explain why `Inf` modeled SFDR means no spur resolved above the declared `-240 dBc` numerical floor, not infinite physical performance. Then distinguish this normalized lookup model and coherent record spectrum from amplitude quantization, BRAM mapping, achieved timing, DAC images, filtering, jitter, phase noise, synthesis, or bench SFDR.

## Executable check

Run in MATLAB:

```matlab
run_checks
```

All assertions must pass before completion. They cover exact baseline recurrence and lookup values, tuning and phase-address sweeps, DC/quarter-rate/full-address limits, the exact broken carrier shift, inert-fault recovery, a representative bounded healthy/fault control grid, malformed inputs, accepted numeric-class equivalence, initial-phase isolation and terminal-wrap partitioning, deterministic recovery, and fixed record/table bounds.

## Teach-back

In two sentences, answer: “What inputs, observable effects, and failure modes matter when you generate a Numerically Controlled Oscillator?” Sentence one must explain how `K`, accumulator width, sample clock, initial phase, and lookup address width determine phase, frequency, table size, and phase error. Sentence two must name premature tuning-word truncation and connect removed low bits to the wrong frequency and period without relying on MATLAB syntax.
