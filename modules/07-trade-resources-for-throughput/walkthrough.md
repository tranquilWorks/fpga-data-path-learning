# Walkthrough: Trade Resources for Throughput

1. Read the guiding question and connect to P06: product codes retain four fractional bits, each multiplier lane has a two-cycle latency and one-cycle initiation interval, and product valid/frame/operation identity must stay associated.
2. State the scheduler contract: eight products need `G=ceil(8/R)` issue cycles; frames start no earlier than arrival or prior start plus `G`; results appear two cycles after issue.
3. Before plotting, predict `G` and the arrival-to-final-result edge difference for `R=2`, `A=4`. Make no second prediction.
4. Run only the baseline section of `experiment.m`. Name the clock-edge, modeled-lane, frame-index, operation-index, signed-product-code, and binary-valid units.
5. Observe arrivals/starts `[1,5,9,13,17,21]`, completions `[6,10,14,18,22,26]`, zero wait, four issue groups per frame, and eight valid products in the selected output vector.
6. Run sweep 1 with the offered interval fixed at one cycle. Observe one transition at a time as modeled multiplier lanes move from one through eight.
7. Give the mechanism-first explanation: lanes add issue slots, ceiling division gives intervals `[8,4,3,2,2,2,2,1]`, and partial final groups create the four-through-seven plateau and changing utilization.
8. Reset to two lanes, then run sweep 2 for offered intervals one through eight cycles per frame.
9. Explain the changed view: intervals below four build finite-queue wait, four balances demand and capacity, and intervals above four make the source limit scheduled throughput without changing compute resources.
10. Run the deliberately broken floor schedule at `R=3`, `A=2`. Compare the healthy three-cycle capacity schedule with the optimistic two-cycle claim.
11. State the violated assumption and symptom: two groups of three cover only six of eight products, so operations 7 and 8 have false valid bits, every output vector is incomplete, and the 50 Mframe/s claim counts unfinished frames.
12. Open `interactive.m`; change only one bounded control and explain the mechanism. Confirm that the fault clears and disables at exact divisors, then run `run_checks.m`, answer `checks.md` one prompt at a time, and give the two-sentence teach-back.

The lane count, pipeline-storage bits, 100 MHz clock, finite queue, and product results are deterministic teaching-model quantities. Do not infer a DSP mapping, reduction network, memory bandwidth, timing closure, power, backpressure, FIFO sufficiency, synthesis, converter behavior, or physical validation from these views.
