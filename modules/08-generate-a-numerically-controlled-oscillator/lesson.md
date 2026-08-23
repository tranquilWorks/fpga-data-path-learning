# Lesson: Generate a Numerically Controlled Oscillator

## Guiding question

What inputs, observable effects, and failure modes matter when you generate a Numerically Controlled Oscillator?

## Mental model

An NCO is a phase clock, not a stored waveform that advances by time. Its accumulator is a circular register containing `B=12` phase bits. Each sample adds tuning word `K`; modular overflow is the intended wrap from one turn to the next. A table observes the accumulator's `P` most-significant bits and maps that coarse phase to a normalized sine/cosine pair.

For this lesson,

\[
\phi[n]=(\phi_0+nK)\bmod 4096,\qquad
f_\text{out}=\frac{K}{4096}f_s,\qquad
a[n]=\left\lfloor\frac{\phi[n]}{2^{12-P}}\right\rfloor.
\]

Sample zero exposes `phi0`; the first update is visible at sample one. The explicit `f_s=100 MHz` assumption makes one tuning code equal `24.4140625 kHz`. It is a conversion assumption, not achieved FPGA timing.

## Connection to P07

P07 showed that adding modeled lanes changes capacity only when the scheduling policy can use them. P08 separates two numeric resources in the same way. All 12 accumulator bits determine frequency resolution, while `P` lookup bits determine phase-table size and truncation error. A smaller lookup can be a valid resource/fidelity trade; shortening `K` before it reaches the accumulator changes the requested behavior.

## Learning cycle

Read the phase recurrence, visualize the baseline, move one lever, inspect the changed view, and then read the mechanism-first explanation. Reset before the second lever so tuning and lookup precision remain independent.

## One prediction before the baseline

At `K=411` and `P=8`, predict whether the accumulator adds 411 or 400 codes each sample. Then inspect the baseline once. Make no second prediction; later prompts ask you to observe and explain.

## Baseline

With `phi0=0`, the first phase codes are `0, 411, 822, 1233, ...`; modulo wrap is expected. The model counts exactly 411 wraps across 4096 next-state transitions, including the terminal transition from stored sample 4095 to unrecorded sample 4096. The 4096 stored states expose 410 adjacent wrap discontinuities and one complete accumulator period because `gcd(411,4096)=1`.

The output frequency is `411*100/4096 = 10.0341796875 MHz`. The 8-bit lookup has 256 phase entries and a `1.40625 degree` address step. Healthy phase truncation discards the current phase code's low four bits only while forming the address. It does not alter `K`, the 12-bit phase recurrence, or frequency.

The baseline views make four different quantities visible: accumulator phase code, normalized sine/cosine output, lookup phase error in degrees, and a coherent complex-output spectrum in dBc. Keep them distinct: a phase staircase is not a frequency error, and a modeled spectral spur is not measured converter SFDR. Finite modeled SFDR is reported only when a spur exceeds the declared `-240 dBc` numerical floor; `Inf` means no spur was resolved above that floor, not infinite physical performance.

## Lever 1: tuning word

Hold `P=8` and `phi0=0`. Sweep `K=[0,1,64,128,256,411,512,1024,2047]`.

Mechanism first: each tuning code adds one phase-accumulator LSB per sample, so the requested and observed coherent-record carrier moves linearly by `24.4140625 kHz/code`. Across 4096 modeled next-state transitions the wrap count equals `K`; the last transition lands on unrecorded sample 4096, so it is distinct from discontinuities visible between stored states. The phase sequence period is `4096/gcd(4096,K)` samples, with the special DC period defined as one sample. The lookup remains 256 entries; moving `K` does not allocate a different phase table.

The `K=0` limit holds phase and produces DC. `K=1` is the minimum positive frequency. `K=1024` is quarter-rate and advances 90 degrees/sample. `K=2047` remains one tuning code below Nyquist. These are discrete-time model limits, not analog output guarantees.

## Lever 2: lookup phase-address bits

Reset to odd `K=411` and `phi0=0`. Sweep `P=3..12`.

Mechanism first: the table contains `2^P` phase entries. The address discards `12-P` low accumulator bits, so maximum phase error is

\[
\left(2^{12-P}-1\right)\frac{360^\circ}{4096}.
\]

Because odd `K=411` visits every accumulator code in the record, every discarded remainder appears once and the RMS error has an independent closed form. Each additional address bit doubles table entries and reduces phase and waveform error. At `P=12`, lookup phase equals accumulator phase exactly and modeled truncation error is zero.

Throughout this sweep, the phase accumulator, `K`, requested frequency, wrap count, sample clock, initial phase, and record size remain unchanged. Lookup entry count is a transparent teaching-model quantity, not inferred BRAM or area.

## Deliberately broken case

Keep `K=411`, `P=8`, and `phi0=0`, but incorrectly truncate `K` by the lookup factor before accumulation:

\[
K_\text{broken}=\left\lfloor\frac{411}{16}\right\rfloor16=400.
\]

The violated boundary is: accumulate the full tuning word; truncate phase only for lookup. Clearing `K`'s low four bits removes 11 frequency-resolution steps. The actual tone becomes `9.765625 MHz`, the error is `-268.5546875 kHz`, the 4096-transition wrap count becomes 400, and `gcd(400,4096)=16` shortens the phase sequence to 256 samples.

The fault is inert when `K` is exactly divisible by the lookup factor, at DC, or when `P=12` discards no phase bits. Those recovery limits isolate the missing low tuning bits as the cause; they do not make premature truncation a safe architecture.

## Common mistakes

- Truncating the tuning word before accumulation instead of truncating phase only at the lookup boundary.
- Calling lookup phase stair-steps a frequency error even though healthy `K` and average phase advance are unchanged.
- Confusing accumulator width, which sets tuning resolution, with lookup address width, which sets modeled phase granularity and table entries.
- Forgetting the modulo recurrence or treating wrap as overflow corruption.
- Measuring a real sine at Nyquist from an unlucky starting phase and concluding that the NCO has no output; this lesson keeps a sine/cosine pair and uses the complex record for frequency observation.
- Treating the assumed 100 MHz clock as achieved timing.
- Treating floating lookup entries as amplitude quantization, ROM contents, BRAM usage, or synthesized area.
- Calling the deterministic record spectrum DAC SFDR, jitter, phase noise, or bench evidence.

## Completion standard

Run `run_checks.m`, answer `checks.md` one prompt at a time, identify which bits belong to tuning versus lookup precision, explain the DC, quarter-rate, and full-address limits, diagnose the exact `411 -> 400` fault, and give the requested two-sentence teach-back without explaining MATLAB syntax.
