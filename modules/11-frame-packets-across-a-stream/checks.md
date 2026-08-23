# P11 checks: Frame Packets Across a Stream

## Guiding question

What inputs, observable effects, and failure modes matter when you frame Packets Across a Stream?

Run `run_checks` first. It independently checks the exact baseline, transfer and packet-end equations,
whole-beat holds, two isolated sweeps, limiting cases, the deliberately broken case, fault aliasing,
the complete bounded control grid, malformed input rejection, deterministic recovery, and fixed
teaching-model resource bounds.

Then answer one prompt at a time.

## Observation and mechanism checks

1. Which baseline cycles have consumer ready low, and which edge accepts the first packet boundary?
   Explain the difference between offering and transferring `last`.
2. State `transfer[n]` and `packetEnd[n]`. Why are `valid=1` and `last=1` insufficient without ready?
3. Which payload beat, code, and `last` value stay stable on cycles 4–7? Connect the observation to
   P10's producer hold obligation.
4. Why do accepted boundary beats `[4, 8, 12]` reconstruct lengths `[4, 4, 4]`? How does the receiver
   infer the first beat of each packet without a separate start pulse?
5. Name one payload-integrity metric and one framing-integrity metric. Why must both be checked?

## Independent sweep checks

6. In the packet-length sweep, derive packet counts `[6, 4, 3, 2]` and boundary density `1/L` from 12
   fixed beats. What remains fixed so this conclusion is isolated?
7. In the consumer-stall sweep, derive completion `12+stall` cycles and rate
   `12/(12+stall)` beats/cycle. Why do accepted boundary ordinals remain fixed?
8. If packet length and stall duration moved together, which change in packet grouping or timing
   would become causally ambiguous?

## Combined-control and aliasing check

9. With three-beat packets and a one-cycle stall on non-boundary beat four, why can the offered
   `last=0` remain visibly unchanged while the broken marker state advances? Explain why a zero
   `last` hold-violation count does not prevent later boundaries from moving to `[3, 5, 8, 11]`.
10. With four-beat packets and a four-cycle stall, the broken counter advances by a whole packet and
   accepted boundaries realign. Why is the output framing plausible even though the source violated
   the stalled-sideband contract? Distinguish fault selection, activation, and visible corruption.

## Limiting-case checks

11. With two-beat packets and no stall, why are boundaries exactly `[2, 4, 6, 8, 10, 12]` and
    completion cycle 12?
12. With six-beat packets and the longest six-cycle stall, why do both packets remain intact and
    completion move to cycle 18?
13. The full healthy control grid completes within a fixed 24-cycle trace. What resource bound does
    that establish, and what does it not prove about a never-ready consumer, timeout, cancellation,
    starvation, or liveness?

## Broken-case and recovery checks

14. In the baseline fault, why do accepted boundaries move from `[4, 8, 12]` to `[5, 9]`? Relate the
    three illegal boundary-counter advances to the five accepted-boundary mismatches.
15. The receiver closes lengths `[5, 4]` and holds a three-beat unterminated tail, while payload beat
    ordinals remain `[1:12]`. Locate the fault precisely and explain why payload conservation misses it.
16. Why is the broken switch inert when stall duration is zero? Why is an inert selection different
    from a fault whose whole-packet drift hides at the receiver?
17. After malformed calls and unrelated maximum/fault calls, why must the exact baseline return?
    Relate that recovery check to the absence of global, persistent, file, network, timer, or
    asynchronous state.

## Interpretation and transfer check

Connect P10's stable valid/ready payload to P11's stable packet sideband. Distinguish this generic,
finite, single-clock framing model from P12 FIFO sizing, P18 AXI-Stream details, headers, length
fields, CRC/FCS, partial-byte qualifiers, reset, CDC safety, synthesis, measured throughput, and
protocol or liveness evidence.

## Teach-back

In two sentences, answer the guiding question. Sentence one must explain how valid, ready, payload,
and `last` transfer together to close packets. Sentence two must name the exact advanced-boundary
failure symptom and why ordered payload delivery alone cannot prove packet integrity.
