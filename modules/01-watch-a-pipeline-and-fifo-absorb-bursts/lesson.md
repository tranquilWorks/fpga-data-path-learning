# Lesson: Watch a Pipeline and FIFO Absorb Bursts

## Guiding question

How do bursts, service rate, and FIFO depth determine loss and latency?

## Mental model

A streaming datapath is a production line. Bursts fill a FIFO, the service rate drains it, and finite depth turns temporary imbalance into overflow or backpressure.

## What to manipulate

Use `interactive.m`. Change one lever at a time before combining effects.

## First observation

Raise the average arrival rate above the processing rate or increase burst size. Watch occupancy climb and latency grow before any sample is finally dropped.

## Common mistakes

- High clock frequency alone does not guarantee end-to-end throughput.
- A deeper FIFO delays overflow but cannot fix a sustained rate mismatch.
- Average rates can hide burst-driven failure.

## Completion standard

The learner can explain the baseline, identify what each lever changes, diagnose the deliberately broken case, and pass `run_checks.m`.
