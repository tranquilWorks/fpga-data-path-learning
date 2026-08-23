# P11 lesson: Frame Packets Across a Stream

## Guiding question

What inputs, observable effects, and failure modes matter when you frame Packets Across a Stream?

## Compounds on P10

P10 established a valid/ready ownership rule: the producer owns `valid` and payload, the consumer
owns `ready`, and the producer holds a valid payload while the consumer is not ready. P11 extends
that same obligation to packet metadata. The end-of-packet bit `last` belongs to one payload beat;
it is not an independent timing pulse.

The 12 payload values are the deterministic 12-bit phase-code labels inherited from P10. They make
identity and order visible without implying that the stream is a free-running NCO or continuously
sampled converter data.

## The framing mechanism

Observe signals immediately before edge `n`:

\[
\begin{aligned}
\text{transfer}[n] &= \text{valid}[n]\land\text{ready}[n],\\
\text{packetEnd}[n] &= \text{transfer}[n]\land\text{last}[n].
\end{aligned}
\]

In plain signal notation these are `transfer[n] = valid[n] && ready[n]` and
`packetEnd[n] = transfer[n] && last[n]`; the equations describe accepted edges, not MATLAB
assignment order.

After reset or an accepted `last`, the next accepted beat begins a packet. An accepted `last` closes
it. If `valid[n] && ~ready[n]`, then valid, payload, and `last` remain stable until an accepting edge.
This is the whole-beat hold rule. The receiver never interprets an unaccepted boundary.

## Learning cycle

### Read and make one prediction

Use four-beat packets and a consumer that lowers ready on cycles 4–6. Predict only this: when payload
beat four first offers `last=1` on cycle 4, does packet one close then, or on cycle 7 when the held
beat is accepted?

### Visualize the baseline

Run the baseline section, then reveal one view at a time:

1. `valid`, `ready`, and `transfer` on clock-cycle axes.
2. Offered and accepted payload beat identity.
3. `last` held beside beat four through the stall.
4. Receiver packet assignment and accepted boundary beats.

Make no second prediction. Report the transitions first. No transfer occurs on cycles 4–6. On cycle
7, beat four/code 1233 and `last=1` transfer together, closing packet one. Boundaries on payload beats
`[4, 8, 12]` produce three packets of four beats, and completion is cycle 15.

### Lever 1 and changed view

Sweep packet length across `[2, 3, 4, 6]` beats while the three-cycle stall, 12 payload words, and
24-cycle allocation remain fixed. Packet count becomes `[6, 4, 3, 2]`; boundary density becomes
`[1/2, 1/3, 1/4, 1/6]` boundaries/beat. Transfer edges and completion remain unchanged.

Mechanism first: packet length selects which accepted payload beats carry `last`. Because this
one-bit sideband travels alongside a payload beat in the model, changing its healthy placement does
not insert or remove a transfer.

### Lever 2 and changed view

Reset packet length to four and sweep consumer ready-low duration from zero to six cycles. Completion
moves from cycles 12–18 and active-window rate becomes `12/(12+stall)` beats/cycle. The receiver still
gets boundary beats `[4, 8, 12]`, lengths `[4, 4, 4]`, and zero payload or boundary errors.

Mechanism first: ready changes when a whole payload-metadata tuple transfers. A healthy source moves
payload and `last` together, so backpressure stretches time without changing packet membership.

### Deliberately broken case

Enable “advance LAST state while ready is low” in the baseline. Payload beat four remains correctly
held, but the broken boundary counter advances on cycles 4–6 despite no transfer. The receiver gets
all payload beat ordinals `[1:12]` in order, yet accepted `last` moves to beats `[5, 9]`. It closes
packets of five and four beats and retains three unterminated beats. Five accepted beats have the
wrong boundary value.

The source visibly changes `last` after the first stalled cycle while still owing the same payload.
That hold violation locates the fault at the source-side metadata state, not at the receiver or in
payload transport.

### Aliasing limit

With four-beat packets and four stalled cycles, the broken counter advances by exactly one packet.
Accepted boundaries realign at `[4, 8, 12]`, even though `last` changed during the stalled offer. This
limiting case separates three facts:

- selecting the fault;
- activating illegal state advance during a stall;
- observing corrupted packet lengths at the receiver.

Only the first two occur in that whole-packet-drift case. Receiver output alone can miss an internal
protocol violation.

## Tutor prompts

Ask one prompt at a time:

1. Which exact edge accepts the first packet boundary, and what three signals prove it?
2. During cycles 4–6, which fields form the one beat still owed by the source?
3. Why does moving packet length change packet count but not transfer timing in this model?
4. Why does moving consumer stall duration change completion but not accepted boundary ordinals?
5. In the broken case, how can payload order remain perfect while packet lengths are wrong?
6. Why can a four-cycle boundary-state drift hide at accepted packet outputs?

## Correct these misconceptions directly

- “`last=1` ends a packet immediately.” No: the boundary counts only on `valid && ready && last`.
- “Backpressure holds payload but metadata may keep running.” No: all sidebands that describe the
  offered beat must remain attached to it.
- “All payloads arrived in order, so the packet stream is correct.” No: packet boundaries are an
  independent integrity dimension.
- “A correct packet count proves the source obeyed the interface.” No: whole-packet phase drift can
  realign accepted boundaries after an illegal stalled transition.
- “Smaller packets cost extra payload cycles here.” No: this model carries `last` beside payload and
  includes no header, gap, CRC, or partial-beat overhead.
- “This is AXI-Stream verification.” No: P11 teaches generic valid/ready framing. P18 covers
  AXI-Stream context, and protocol compliance requires a separate specification and evidence.
- “This proves FIFO sizing or unbounded progress.” No: P12 covers burst/rate-derived depth. The fixed
  schedule always returns ready; timeout, cancellation, starvation, and liveness are outside it.

## Completion

Run `run_checks`, answer `checks.md` one prompt at a time, and give a two-sentence teach-back. Sentence
one must explain how valid, ready, payload, and `last` move and close packets. Sentence two must name
the broken counter's receiver symptom and explain why ordered payloads alone cannot detect it. Do not
explain MATLAB syntax.
