# Checks: Trade Resources for Throughput

What inputs, observable effects, and failure modes matter when you trade Resources for Throughput?

Ask and answer one prompt at a time.

## Observation check

For the two-lane, four-cycle baseline, identify `W`, `R`, `A`, lane latency, lane initiation interval, frame capacity interval, arrival/start/completion edges, packing utilization, scheduled rate, product LSB, and the selected frame's eight valid product codes. Why is the first frame's final result on edge 6?

## Lever-isolation check

What changes when multiplier lanes move from one through eight while the offered interval remains one cycle? After resetting to two lanes, what changes when the offered interval moves from one through eight cycles per frame, and what resource, capacity, product, and identity facts remain fixed?

## Limiting-case check

Explain the one-lane serialization limit, the eight-lane full-replication limit, the two-cycle capacity plateau from four through seven lanes, and the source-limited case where `A` exceeds `G`. At three lanes, why is the raw work rate `3/8` frame-equivalent/cycle while the declared non-preemptive complete-frame capacity is only `1/3` frame/cycle? Why can five or seven lanes consume more modeled resources than four lanes without increasing frame throughput?

## Broken-case check

At three lanes and a two-cycle source interval, why does `floor(8/3)` allocate only six slots? Name the violated `R*G >= W` coverage assumption, identify dropped operations 7 and 8, and explain why full-looking groups plus a claimed 50 Mframe/s do not prove that any complete frame was produced.

## Interpretation and transfer check

Connect P06's product codes, valid/identity alignment, two-cycle lane latency, and one-cycle lane initiation interval to this scheduler. Then distinguish a modeled multiplier lane and pipeline-storage bit from a DSP slice, achieved clock, timing result, power estimate, reduction tree, FIFO, or sustained-overload guarantee.

## Executable check

Run in MATLAB:

```matlab
run_checks
```

All assertions must pass before completion. They cover exact product vectors and schedules, numeric scaling, both independent sweeps, every healthy resource/demand pair, lane exclusivity, one-lane and full-replication limits, non-divisible floor-schedule loss, exact-divisor recovery, malformed inputs, accepted numeric-class equivalence, selected-view isolation, deterministic recovery, and fixed resource bounds.

## Teach-back

In two sentences, answer: “What inputs, observable effects, and failure modes matter when you trade Resources for Throughput?” Sentence one must explain how work per frame, modeled multiplier lanes, source interval, lane latency, and ceiling division determine capacity, queue wait, and visible output timing. Sentence two must name the floor-division coverage failure and connect missing tail-valid bits to incomplete results and an overstated throughput claim without relying on MATLAB syntax.
