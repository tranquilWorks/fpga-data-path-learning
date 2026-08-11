# P16 checks: Measure End-to-End Pipeline Latency

The implementation batch must add checks that prove all of the following:

- baseline outputs are deterministic and physically or computationally bounded;
- each of two levers changes the intended observable for the stated reason;
- the broken case violates a named assumption and produces a recognizable symptom;
- limiting cases agree with an independent calculation;
- the learner can answer: “What inputs, observable effects, and failure modes matter when you measure End-to-End Pipeline Latency?” without relying on MATLAB syntax.

No executable check is claimed until `run_checks.m` exists and the manifest status is `implemented`.
