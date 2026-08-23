# P10 walkthrough: Apply Backpressure Without Losing Data

1. Read the guiding question and P09 prerequisite link. Make one prediction: will the cycle-5 consumer stall stop the source immediately, or only after the depth-three FIFO fills?
2. Reveal the upstream baseline view. Observe enqueues on cycles 1–6, propagated ready low on cycles 7–9, and resumed enqueue on cycle 10. Make no second prediction.
3. Reveal the downstream view. Observe dequeues on cycles 2–4 and 10–18; no dequeue occurs while consumer ready is low.
4. Reveal occupancy alone. It rises from one to three tokens, never exceeds depth, and stays full while neither side can move a token.
5. Reveal token identity. Output token 4/code 1233 remains stable through cycles 5–10; source token 7/code 2466 remains stable through cycles 7–10.
6. Read the baseline mechanism: enqueue and dequeue each require their own valid/ready overlap, and `qAfter=qBefore+enqueue-dequeue` conserves accepted tokens.
7. Move lever 1 only: sweep consumer stall from 0 to 8 cycles at depth 3. Observe completion `13:21`, source-stalled cycles `[0,0,0,1,2,3,4,5,6]`, bounded peak occupancy, and a fixed 12-token delivery count.
8. Read why two free slots absorb two stalled downstream edges. Reset the baseline before moving another lever.
9. Move lever 2 only: sweep FIFO depth from 1 to 6 at a five-cycle stall. Observe source-stalled cycles `[5,4,3,2,1,0]`, peak occupancy equal to depth, completion fixed at cycle 18, and no loss.
10. Read why capacity postpones backpressure but cannot restore consumer service. Do not treat this bounded sweep as P12's FIFO-sizing calculation.
11. Run the deliberately broken producer. Observe drops on cycles 7–9, next-cycle source-hold violations on 8–10, and the delivered sequence jump from token 6 to token 10 while storage stays bounded.
12. Run `interactive`, then `run_checks`. Answer `checks.md` one prompt at a time and give the two-sentence teach-back without relying on MATLAB syntax.
