# Curriculum readiness audit

**Track:** FPGA, Converter Interfaces, and High-Speed Data Paths

## Baseline conclusion

The repository has 24 uniquely identified modules in a six-phase, prerequisite-ordered sequence. P01 is the complete reference slice; P02-P24 are explicit non-runnable batch scaffolds. The learner flow is read → visualize → move one lever → visualize the delta → read/explain, followed by a broken case, checks, and teach-back.

Static structure and CLI behavior are verified in CI. MATLAB was not available during the 2026-08-11 baseline audit, so numerical execution, UI behavior, and instructional efficacy remain named validation gaps rather than implied evidence.

## Coverage and compounding order

### Phase 1: Digital logic

- **P01 — Watch a Pipeline and FIFO Absorb Bursts:** How do bursts, service rate, and FIFO depth determine loss and latency?
- **P02 — Build Combinational Logic from Truth Tables:** What inputs, observable effects, and failure modes matter when you build Combinational Logic from Truth Tables?
- **P03 — Store State with Registers:** What inputs, observable effects, and failure modes matter when you store State with Registers?
- **P04 — Control Behavior with a Finite-State Machine:** What inputs, observable effects, and failure modes matter when you control Behavior with a Finite-State Machine?

### Phase 2: Numeric hardware

- **P05 — Quantize Arithmetic into Fixed Point:** What inputs, observable effects, and failure modes matter when you quantize Arithmetic into Fixed Point?
- **P06 — Pipeline a Multiply-Accumulate:** What inputs, observable effects, and failure modes matter when you pipeline a Multiply-Accumulate?
- **P07 — Trade Resources for Throughput:** What inputs, observable effects, and failure modes matter when you trade Resources for Throughput?
- **P08 — Generate a Numerically Controlled Oscillator:** What inputs, observable effects, and failure modes matter when you generate a Numerically Controlled Oscillator?

### Phase 3: Streaming architectures

- **P09 — Handshake with Valid and Ready:** What inputs, observable effects, and failure modes matter when you handshake with Valid and Ready?
- **P10 — Apply Backpressure Without Losing Data:** What inputs, observable effects, and failure modes matter when you apply Backpressure Without Losing Data?
- **P11 — Frame Packets Across a Stream:** What inputs, observable effects, and failure modes matter when you frame Packets Across a Stream?
- **P12 — Size a FIFO from Burst and Service Rates:** What inputs, observable effects, and failure modes matter when you size a FIFO from Burst and Service Rates?

### Phase 4: Clocking and timing

- **P13 — Cross a Clock Domain Safely:** What inputs, observable effects, and failure modes matter when you cross a Clock Domain Safely?
- **P14 — Make Metastability Risk Concrete:** What inputs, observable effects, and failure modes matter when you make Metastability Risk Concrete?
- **P15 — Read a Timing Constraint as a Physical Requirement:** What inputs, observable effects, and failure modes matter when you read a Timing Constraint as a Physical Requirement?
- **P16 — Measure End-to-End Pipeline Latency:** What inputs, observable effects, and failure modes matter when you measure End-to-End Pipeline Latency?

### Phase 5: Host and converter interfaces

- **P17 — Control Registers with AXI-Lite:** What inputs, observable effects, and failure modes matter when you control Registers with AXI-Lite?
- **P18 — Move Samples with AXI-Stream:** What inputs, observable effects, and failure modes matter when you move Samples with AXI-Stream?
- **P19 — Trace a DMA Transfer over PCIe:** What inputs, observable effects, and failure modes matter when you trace a DMA Transfer over PCIe?
- **P20 — Frame Converter Data with JESD Concepts:** What inputs, observable effects, and failure modes matter when you frame Converter Data with JESD Concepts?

### Phase 6: Coherent signal systems

- **P21 — Build a Digital Downconverter:** What inputs, observable effects, and failure modes matter when you build a Digital Downconverter?
- **P22 — Distribute a Trigger Across Channels:** What inputs, observable effects, and failure modes matter when you distribute a Trigger Across Channels?
- **P23 — Preserve Multi-Channel Phase Coherence:** What inputs, observable effects, and failure modes matter when you preserve Multi-Channel Phase Coherence?
- **P24 — Debug a Host-FPGA-Converter Chain:** What inputs, observable effects, and failure modes matter when you debug a Host-FPGA-Converter Chain?

## Batch readiness gates

A scaffold may become `implemented` only when it has a deterministic model, a sectioned experiment, two independent parameter sweeps, one deliberately broken case, interactive controls, interpretation-focused tutor text, numerical checks, focused static tests, and evidence that says exactly what did and did not run.
