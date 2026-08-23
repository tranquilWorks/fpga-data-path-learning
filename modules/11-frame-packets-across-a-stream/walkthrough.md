# P11 walkthrough: Frame Packets Across a Stream

1. Read the guiding question and P10 prerequisite link. Make one prediction: does the first packet
   close when stalled `last=1` is offered on cycle 4, or when that beat transfers on cycle 7?
2. Reveal the handshake baseline. Observe transfers on cycles `[1, 2, 3, 7:15]` and no transfers
   while consumer ready is low on cycles 4–6. Make no second prediction.
3. Reveal payload identity alone. Observe beat 4/code 1233 held from cycles 4 through 7.
4. Reveal `last` alone. Observe that its asserted value stays attached to beat four until acceptance.
5. Reveal receiver grouping. Observe accepted boundaries on beats `[4, 8, 12]`, three four-beat
   packets, and completion on cycle 15.
6. Read the baseline mechanism: `transfer = valid && ready`, and only `transfer && last` closes a
   packet. Relate the whole-beat hold rule directly to P10.
7. Move lever 1 only: sweep packet length across `[2, 3, 4, 6]` at the fixed three-cycle stall.
   Observe packet counts `[6, 4, 3, 2]`, boundary density `1/L`, and unchanged transfer timing.
8. Read why moving a sideband's healthy placement regroups the same accepted payload beats. Reset
   packet length to four before moving another lever.
9. Move lever 2 only: sweep consumer ready-low duration from zero to six cycles. Observe completion
   `12:18`, falling finite-window rate, and unchanged boundary beats `[4, 8, 12]`.
10. Read why healthy backpressure stretches time without changing which payload owns `last`.
11. Run the deliberately broken source. Observe `last` advance while beat four waits, accepted
    boundaries move to `[5, 9]`, receiver segments become complete lengths `[5, 4]` plus an
    unterminated three-beat tail, and all 12 payloads remain ordered.
12. Inspect the four-cycle aliasing limit: accepted boundaries realign, but the stalled `last` hold
    rule was still violated. Distinguish fault selection, activation, and visible corruption.
13. Run `interactive`, then `run_checks`. Answer `checks.md` one prompt at a time and give the
    two-sentence teach-back without relying on MATLAB syntax.
