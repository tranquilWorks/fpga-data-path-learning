# Walkthrough: Generate a Numerically Controlled Oscillator

1. Read the guiding question and connect to P07: keep tuning precision and lookup resources separate just as P07 kept work, capacity, and useful throughput separate.
2. State the sample convention and recurrence: sample zero is `phi0`; later phase is `mod(phi0+n*K,4096)`; the lookup address is `floor(phi/2^(12-P))`.
3. Before plotting, predict whether the `K=411`, `P=8` baseline adds 411 or 400 phase codes/sample. Make no second prediction.
4. Run only the baseline sections of `experiment.m`. Name the sample-index, microsecond, unsigned phase-code, degree, normalized-amplitude, MHz, and dBc units.
5. Observe `10.0341796875 MHz`, `24.4140625 kHz/code`, 411 wraps across 4096 modeled next-state transitions, 410 visible discontinuities between the stored states, 256 lookup entries, and `1.318359375 degrees` maximum phase error.
6. Run sweep 1 with lookup width fixed at eight bits. Observe DC, the minimum positive tuning step, representative tones, quarter-rate, and the highest setting below Nyquist.
7. Give the mechanism-first explanation: `K` changes phase advance, frequency, wrap count, and period while the lookup retains 256 entries.
8. Reset to odd `K=411`, then run sweep 2 for `P=3..12`.
9. Explain the changed view: each address bit doubles entries and reduces phase/waveform error, while the full accumulator phase and tuned frequency remain fixed; at `P=12`, phase truncation vanishes.
10. Run the deliberately broken `K=411`, `P=8` case. Compare required `K=411` with applied `K=400`, required `10.0341796875 MHz` with actual `9.765625 MHz`, and periods 4096 with 256 samples.
11. State the violated boundary and symptom: low tuning bits were removed before accumulation, moving the carrier by negative eleven resolution steps. Confirm recovery for divisible `K`, DC, and full 12-bit lookup addressing.
12. Open `interactive.m`; change one bounded control at a time. Then run `run_checks.m`, answer `checks.md` one prompt at a time, and give the two-sentence teach-back.

The clock, spectrum, table entries, and sine/cosine values are deterministic teaching-model quantities. SFDR is finite only for a spur above the declared `-240 dBc` numerical floor; `Inf` means no resolved modeled spur above that floor. Do not infer achieved timing, amplitude-quantized ROM contents, FPGA resources, DAC performance, jitter, phase noise, synthesis, converter behavior, or physical validation from these views.
