# P12 lesson: Size a FIFO from Burst and Service Rates

## Guiding question

What inputs, observable effects, and failure modes matter when you size a FIFO from Burst and Service Rates?

## Compounds on P11

P11 established that a packet boundary belongs to an accepted payload beat: `valid`, payload, and
`last` remain one offer until `ready` accepts them. P12 zooms out from beat identity and treats a
finite set of correctly offered packet words as an aggregate burst. It asks whether registered FIFO
storage can retain the backlog while downstream service catches up.

P01 made burst growth, latency, and eventual overflow visible with a long modulated trace. P12 makes
a narrower design guarantee: for one finite constant-rate burst, compute the exact required entries
before selecting a depth.

## Registered FIFO sizing mechanism

Signals and counts are interpreted immediately before and after each clock edge. With an empty,
non-fall-through FIFO:

\[
\begin{aligned}
d[n] &= \min(S,qBefore[n]),\\
qAfter[n] &= a[n] + \max(0,qBefore[n]-S),\\
D_{required} &= \max_n qAfter[n].
\end{aligned}
\]

The finite FIFO performs the same stored-word departure, then admits at most the slots now free:

\[
admitted[n]=\min\!\left(a[n],D-(qBefore[n]-d[n])\right).
\]

This ordering is the P10 registered contract. A full FIFO may remove stored words and replace them on
one edge, but it cannot remove a word that arrives on that edge.

For a `B`-cycle burst at `A` words/cycle with constant service `S`, empty initial occupancy, and a
burst beginning on cycle 1:

\[
D_{required}=A+(B-1)\max(A-S,0).
\]

The inputs that make this statement meaningful are burst duration, ingress rate, guaranteed service
capacity and phase, initial occupancy, FIFO timing convention, word width, and any design margin. P12
holds phase, initial occupancy, width, and margin fixed so two rate levers remain observable.

## Learning cycle

### Read and make one prediction

The baseline offers 3 words/cycle for 8 cycles, services 1 previously stored word/cycle, and begins
empty. Predict only whether 16 registered entries are sufficient. Do not make another prediction
before revealing the baseline.

### Visualize the baseline

Reveal cumulative arrivals and departures first. Their gap is `[3,5,7,9,11,13,15,17]` words on the
eight burst edges. Reveal occupancy second: it peaks at 17 words on cycle 8, then drains to zero on
cycle 25. A selected 17-word FIFO admits all 24 offered words with zero margin and no capacity
refusal.

Mechanism first: cycle-one service cannot consume the first arrivals because the FIFO was empty
immediately before that edge. The first batch therefore consumes `A=3` entries; each later burst edge
adds `A-S=2` entries.

### Lever 1 and changed view

Sweep burst duration across `[1,2,4,6,8]` cycles while ingress remains 3 words/cycle, service remains
1 word/cycle, configured capacity remains 32 words, and the fault remains off. Required depths are
`[3,5,9,13,17]` words and drain edges are `[4,7,13,19,25]`.

Mechanism first: longer duration extends the interval over which arrival exceeds removal. Reset burst
duration to eight before moving service so duration and service do not become causally ambiguous.

### Lever 2 and changed view

Sweep service across `[0,1,2,3,4]` words/cycle while the eight-cycle, three-word/cycle arrival trace,
configured capacity, and fault state remain fixed. Required depths become `[24,17,10,3,3]` words.
Drain completion is `[no drain,25,13,9,9]` cycles.

Mechanism first: service removes stored words before each admission. Zero service retains the entire
finite burst and returns a bounded no-drain result. At service greater than or equal to arrival, the
FIFO still stages the first three-word batch because it is registered; faster unused capacity cannot
be banked for a future edge.

### Deliberately broken case

Enable “assume new arrivals are fall-through serviceable.” The broken formula
`D=B*max(A-S,0)` returns 16 words. It silently changes the architecture: it lets cycle-one service
consume one of the three arrivals even though no word was stored before the edge.

The correct unbounded reference still peaks at 17. The finite depth-16 path clips at 16, admits only
two of the three cycle-eight words, and requests one word of upstream backpressure. A clipped
occupancy plot alone looks safely bounded; the admission and conservation metrics expose the missing
word.

If ready can propagate, the producer holds and retries that word with its payload and `last`, as P10
and P11 require. If the source is unthrottleable or advances anyway, that one word is conditionally
lost. FIFO-full and data-loss are therefore different claims.

## Tutor prompts

Ask one prompt at a time:

1. Which two cumulative curves create the occupancy gap, and on which edge is it largest?
2. Why does the first three-word batch need storage before one-word/cycle service can help?
3. Which values stay fixed when burst duration moves?
4. Why does increasing service stop reducing depth at three words?
5. What does the zero-service result prove, and what timeout claim does it not prove?
6. Why can the broken finite occupancy appear bounded even though one word was not admitted?
7. When does full cause backpressure, and when can it become actual loss?

## Correct these misconceptions directly

- “Peak of a depth-limited trace proves the selected depth.” No: clipping guarantees that peak never
  exceeds depth. Size from an unbounded reference first.
- “Arrival minus service can always be taken on the same edge.” No: P10's registered FIFO services
  only previously stored words.
- “A matched service rate means zero FIFO entries.” No: this registered model needs one ingress batch
  for staging; a fall-through channel is a different architecture.
- “Unused service before or during an empty interval is credit.” No: service capacity is not stored.
- “Full means the word was lost.” No: full requests ready-low hold/retry. Loss requires an
  unthrottleable or noncompliant source.
- “`last` tells the FIFO how quickly to drain.” No: `last` marks packet membership; the downstream
  service schedule sets removal.
- “Seventeen words means seventeen bytes or one BRAM.” No: width, primitive geometry, ports, flags,
  and implementation margin are outside this count model.
- “The 40-cycle loop proves liveness.” No: it proves bounded execution. A zero-service case explicitly
  returns without drain; timeout, cancellation, fairness, and recovery policy are system decisions.

## Completion

Run `run_checks`, answer `checks.md` one prompt at a time, and give a two-sentence teach-back. Sentence
one must name the maximum unbounded registered backlog and the inputs needed to compute it. Sentence
two must explain the 17-versus-16 broken case and distinguish backpressure from conditional loss.
