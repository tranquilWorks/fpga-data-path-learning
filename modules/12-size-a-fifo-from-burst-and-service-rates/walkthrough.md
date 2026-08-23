# P12 walkthrough: Size a FIFO from Burst and Service Rates

1. Read the exact guiding question and connect P11's finite framed beats to P10's registered FIFO.
   Make one prediction only: will 16 words hold the eight-cycle, 3-in/1-out baseline?
2. Reveal cumulative arrivals and departures. Observe their gap grow through the eight burst edges;
   do not infer depth from a clipped finite trace.
3. Reveal unbounded occupancy. Observe `[3,5,7,9,11,13,15,17]` words, peak cycle 8, and drain
   completion on cycle 25.
4. Reveal the selected 17-word depth and headroom. Observe zero headroom at the peak, all 24 words
   admitted, and zero backpressure requests.
5. Read the registered mechanism: stored words depart before admissions for slot accounting, but new
   arrivals cannot depart until a later edge. Derive `D=A+(B-1)*max(A-S,0)`.
6. Move lever 1 only: sweep burst duration `[1,2,4,6,8]` cycles at fixed `A=3`, `S=1`, depth 32,
   and fault off. Observe required depths `[3,5,9,13,17]` words.
7. Explain why each later burst edge adds two words, then reset burst duration to eight.
8. Move lever 2 only: sweep service `[0,1,2,3,4]` words/cycle at the fixed burst. Observe required
   depths `[24,17,10,3,3]` and completion `[no drain,25,13,9,9]`.
9. Explain why matched/faster service leaves a three-word registered staging requirement and why zero
   service returns bounded without draining.
10. Run the deliberately broken fall-through estimator. Observe depth 16 clip occupancy and refuse
    one of the three cycle-eight arrivals while the unbounded reference still peaks at 17.
11. State the exact violated assumption: cycle-one service cannot remove a newly arriving word from
    the declared registered FIFO.
12. Distinguish the symptom from loss: a compliant P10/P11 producer holds and retries the word;
    ignoring ready or lacking backpressure conditionally loses it.
13. Open `interactive`, move one control at a time, then run `run_checks`. Answer `checks.md` one
    prompt at a time and give the two-sentence teach-back without relying on MATLAB syntax.
