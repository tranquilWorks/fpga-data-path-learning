%% P11 - Frame Packets Across a Stream
% Run one section at a time. P10 established that a stalled valid/ready
% source holds the payload still owed. P11 adds LAST: a one-bit sideband
% that belongs to that same beat and closes a packet only when transferred.
% Each sweep resets the other lever so framing and timing stay separable.
figureNames = {'P11 baseline packet framing', ...
    'P11 packet-length sweep','P11 consumer-stall sweep', ...
    'P11 broken LAST advance'};
for figureIndex = 1:numel(figureNames)
    delete(findall(groot,'Type','figure','Name',figureNames{figureIndex}));
end
clear model;
clc;

%% Read the boundary rule, then make one prediction
% Guiding question: What inputs, observable effects, and failure modes
% matter when you frame Packets Across a Stream?
%
% A beat transfers on an edge only when valid && ready. LAST=1 on that
% accepted beat closes the current packet; the next accepted beat begins
% the next packet. Predict only this: if the consumer stalls on the first
% packet's LAST beat, does the packet close when LAST is first offered or
% when that held beat is finally accepted?

%% Establish the deterministic baseline before changing a lever
baseline = model(4,3,false);
expectedTransferCycles = [1 2 3 7 8 9 10 11 12 13 14 15].';
assert(isequal(find(baseline.applied.transfer),expectedTransferCycles) && ...
    isequal(baseline.applied.acceptedBeatOrdinals,(1:12).') && ...
    baseline.applied.dataCompleted && ...
    baseline.applied.completionCycle == 15, ...
    'P11:BaselineTransfers', ...
    'The baseline must deliver all 12 payload beats around the stall.');
assert(isequal(baseline.applied.observedBoundaryBeatOrdinals,[4 8 12].') && ...
    isequal(baseline.applied.completedPacketLengths,[4 4 4].') && ...
    baseline.applied.observedPacketCount == 3 && ...
    baseline.applied.framingValid && ...
    baseline.applied.payloadHoldViolationCount == 0 && ...
    baseline.applied.lastHoldViolationCount == 0, ...
    'P11:BaselineFraming', ...
    'The receiver must close exactly three healthy four-beat packets.');
fprintf(['Baseline: packet length=%d beats, packets=%d, ready low=%d ' ...
    'cycles, accepted=%d beats, completion=%d cycles, rate=%0.6g ' ...
    'beats/cycle.\n'],baseline.packetLength, ...
    baseline.applied.observedPacketCount,baseline.consumerStallCycles, ...
    baseline.applied.acceptedBeatCount,baseline.applied.completionCycle, ...
    baseline.applied.activeWindowTransferRate);
fprintf('%s; %s.\n',baseline.transferEquationText,baseline.boundaryRuleText);

%% Baseline view 1 - valid, ready, and accepted transfer edges
baselineFigure = figure('Name',figureNames{1},'NumberTitle','off');
visibleCycles = 1:18;
subplot(2,2,1);
stairs(baseline.cycle(visibleCycles), ...
    double(baseline.applied.sourceValid(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','valid');
hold on;
stairs(baseline.cycle(visibleCycles), ...
    2+double(baseline.applied.sourceReady(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','ready');
stairs(baseline.cycle(visibleCycles), ...
    4+double(baseline.applied.transfer(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','transfer');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Handshake state [binary, vertically offset]');
title('No transfer occurs while ready is low');
set(gca,'YTick',[0.5 2.5 4.5], ...
    'YTickLabel',{'valid','ready','transfer'});
ylim([-0.2 5.2]);
xlim([1 18]);
drawnow;

%% Baseline view 2 - the exact payload beat held through backpressure
figure(baselineFigure);
subplot(2,2,2);
stairs(baseline.cycle(visibleCycles), ...
    baseline.applied.sourceBeatOrdinal(visibleCycles), ...
    'LineWidth',1.3,'DisplayName','offered beat');
hold on;
acceptedCycles = find(baseline.applied.transfer);
scatter(acceptedCycles, ...
    baseline.applied.acceptedBeatOrdinalByCycle(acceptedCycles), ...
    42,'filled','DisplayName','accepted beat');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Payload identity [beat ordinal from one]');
title('Beat four waits unchanged on cycles 4 through 7');
legend('Location','best');
xlim([1 18]);
ylim([0 13]);
drawnow;

%% Baseline view 3 - LAST stays attached to the held payload beat
figure(baselineFigure);
subplot(2,2,3);
stairs(baseline.cycle(visibleCycles), ...
    double(baseline.applied.sourceLast(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','source LAST');
hold on;
stairs(baseline.cycle(visibleCycles), ...
    2+double(baseline.applied.sourceExpectedLast(visibleCycles)), '--', ...
    'LineWidth',1.3,'DisplayName','LAST owned by payload');
stairs(baseline.cycle(visibleCycles), ...
    4+double(baseline.applied.sourceReady(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','ready');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Boundary state [binary, vertically offset]');
title('LAST for beat four remains high until cycle 7 acceptance');
set(gca,'YTick',[0.5 2.5 4.5], ...
    'YTickLabel',{'source LAST','expected LAST','ready'});
ylim([-0.2 5.2]);
xlim([1 18]);
drawnow;

%% Baseline view 4 - accepted beat identity becomes receiver packets
figure(baselineFigure);
subplot(2,2,4);
stairs(baseline.beatOrdinal,baseline.expectedPacketIndexByBeat, ...
    'LineWidth',1.3,'DisplayName','receiver packet');
hold on;
scatter(baseline.expectedBoundaryBeatOrdinals, ...
    baseline.expectedPacketIndexByBeat( ...
        baseline.expectedBoundaryBeatOrdinals), ...
    54,'filled','DisplayName','accepted LAST');
hold off;
grid on;
xlabel('Accepted payload [beat ordinal from one]');
ylabel('Receiver packet identity [packet index from one]');
title('Accepted LAST markers close three four-beat packets');
legend('Location','best');
xlim([1 12]);
ylim([0 4]);
sgtitle('P11 baseline: four-beat packets and a three-cycle stall');
drawnow;

%% Read the baseline mechanism before moving a lever
% LAST is not a pulse interpreted merely because it appears on a clock.
% It is metadata on one valid payload beat. Cycles 4-6 accept nothing, so
% beat four remains the current offer and LAST remains one. The accepting
% edge at cycle 7 both transfers payload word 1233 and closes packet one.

%% Sweep 1 - packet length with readiness and payloads held fixed
% Lever 1 changes only which of the same 12 payload beats carry LAST. The
% three ready-low cycles, transfer edges, payload values, and allocation
% remain fixed.
packetLengthSweep = [2 3 4 6];
lengthPacketCounts = zeros(size(packetLengthSweep));
lengthBoundaryDensity = zeros(size(packetLengthSweep));
lengthCompletionCycles = zeros(size(packetLengthSweep));
lengthAcceptedBeats = zeros(size(packetLengthSweep));
for sweepIndex = 1:numel(packetLengthSweep)
    current = model(packetLengthSweep(sweepIndex),3,false);
    assert(isequal(current.consumerReady,baseline.consumerReady) && ...
        isequal(current.payloadWords,baseline.payloadWords) && ...
        isequal(find(current.applied.transfer),expectedTransferCycles) && ...
        current.applied.dataCompleted && current.applied.framingValid && ...
        current.applied.boundaryMismatchCount == 0 && ...
        current.recordCycleCount == baseline.recordCycleCount, ...
        'P11:PacketLengthSweepIsolation', ...
        ['Packet-length sweep must preserve readiness, payloads, transfer ' ...
        'timing, integrity, and allocation.']);
    lengthPacketCounts(sweepIndex) = current.applied.observedPacketCount;
    lengthBoundaryDensity(sweepIndex) = current.applied.boundaryDensity;
    lengthCompletionCycles(sweepIndex) = current.applied.completionCycle;
    lengthAcceptedBeats(sweepIndex) = current.applied.acceptedBeatCount;
end
assert(isequal(lengthPacketCounts,[6 4 3 2]) && ...
    isequal(lengthBoundaryDensity,1./packetLengthSweep) && ...
    all(lengthCompletionCycles == 15) && ...
    all(lengthAcceptedBeats == 12), ...
    'P11:PacketLengthSweep', ...
    'Packet length must change only boundary grouping in this fixed trace.');

lengthFigure = figure('Name',figureNames{2},'NumberTitle','off');
subplot(2,2,1);
plot(packetLengthSweep,lengthPacketCounts,'-o','LineWidth',1.3);
grid on;
xlabel('Packet length [beats/packet]');
ylabel('Completed packets [packets]');
title('The same 12 beats form fewer, longer packets');
drawnow;

%% Sweep 1 changed view - boundary density
figure(lengthFigure);
subplot(2,2,2);
plot(packetLengthSweep,lengthBoundaryDensity,'-o','LineWidth',1.3);
grid on;
xlabel('Packet length [beats/packet]');
ylabel('Accepted LAST density [boundaries/beat]');
title('Boundary density is one divided by packet length');
drawnow;

%% Sweep 1 invariant view - timing stays fixed
figure(lengthFigure);
subplot(2,2,3);
plot(packetLengthSweep,lengthCompletionCycles,'-o','LineWidth',1.3);
grid on;
xlabel('Packet length [beats/packet]');
ylabel('Final transfer edge [clock cycle]');
title('Sideband placement does not add transfer cycles');
ylim([14 16]);
drawnow;

%% Sweep 1 invariant view - payload count stays fixed
figure(lengthFigure);
subplot(2,2,4);
bar(packetLengthSweep,lengthAcceptedBeats);
grid on;
xlabel('Packet length [beats/packet]');
ylabel('Accepted payloads [beats]');
title('Every grouping delivers the same 12 payload beats');
ylim([0 13]);
sgtitle('Sweep 1: move framing boundaries at fixed readiness');
drawnow;

%% Read the first changed-view mechanism
% Packet length L places LAST on accepted beat ordinals L, 2L, and so on.
% For the fixed 12-beat record, packet count is 12/L and boundary density
% is 1/L boundaries/beat. LAST rides beside payload, so regrouping the same
% beats does not alter the valid/ready transfer schedule.

%% Sweep 2 - consumer stall duration with four-beat packets fixed
% Reset packet length to four. Lever 2 changes only ready-low cycles from
% cycle 4 onward. Expected LAST locations and payload values stay fixed.
consumerStallSweep = 0:6;
stallCompletionCycles = zeros(size(consumerStallSweep));
stallTransferRates = zeros(size(consumerStallSweep));
stallPacketCounts = zeros(size(consumerStallSweep));
stallBoundaryMismatches = zeros(size(consumerStallSweep));
for sweepIndex = 1:numel(consumerStallSweep)
    current = model(4,consumerStallSweep(sweepIndex),false);
    assert(current.packetLength == 4 && ...
        isequal(current.payloadWords,baseline.payloadWords) && ...
        isequal(current.expectedBoundaryBeatOrdinals,[4 8 12].') && ...
        isequal(current.applied.observedBoundaryBeatOrdinals,[4 8 12].') && ...
        current.applied.acceptedBeatCount == 12 && ...
        current.applied.dataCompleted && current.applied.framingValid && ...
        current.applied.payloadHoldViolationCount == 0 && ...
        current.applied.lastHoldViolationCount == 0, ...
        'P11:ConsumerStallSweepIsolation', ...
        ['Consumer-stall sweep must preserve packet length, payloads, ' ...
        'boundaries, whole-beat holds, and delivery.']);
    stallCompletionCycles(sweepIndex) = current.applied.completionCycle;
    stallTransferRates(sweepIndex) = ...
        current.applied.activeWindowTransferRate;
    stallPacketCounts(sweepIndex) = current.applied.observedPacketCount;
    stallBoundaryMismatches(sweepIndex) = ...
        current.applied.boundaryMismatchCount;
end
assert(isequal(stallCompletionCycles,12:18) && ...
    isequal(stallTransferRates,12./(12:18)) && ...
    all(stallPacketCounts == 3) && ...
    all(stallBoundaryMismatches == 0), ...
    'P11:ConsumerStallSweep', ...
    'Stalls must move timing without moving accepted packet boundaries.');

stallFigure = figure('Name',figureNames{3},'NumberTitle','off');
subplot(2,2,1);
plot(consumerStallSweep,stallCompletionCycles,'-o','LineWidth',1.3);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Final transfer edge [clock cycle]');
title('Each unavailable edge moves completion by one cycle');
drawnow;

%% Sweep 2 changed view - active-window transfer rate
figure(stallFigure);
subplot(2,2,2);
plot(consumerStallSweep,stallTransferRates,'-o','LineWidth',1.3);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Accepted payload rate [beats/cycle]');
title('Backpressure lowers the finite-window transfer rate');
drawnow;

%% Sweep 2 invariant view - packet count
figure(stallFigure);
subplot(2,2,3);
bar(consumerStallSweep,stallPacketCounts);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Completed packets [packets]');
title('Healthy stalls do not merge or split packets');
ylim([0 4]);
drawnow;

%% Sweep 2 invariant view - accepted boundary errors
figure(stallFigure);
subplot(2,2,4);
bar(consumerStallSweep,stallBoundaryMismatches);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Boundary mismatches [accepted beats]');
title('Held metadata keeps every accepted boundary correct');
ylim([0 1]);
sgtitle('Sweep 2: move consumer availability at fixed framing');
drawnow;

%% Read the second changed-view mechanism
% Ready controls when a beat is accepted, not which payload-LAST tuple is
% accepted. A stall of S cycles changes completion from 12 to 12+S cycles
% and rate from one to 12/(12+S) beats/cycle. Packet lengths stay four
% because the source advances both payload and LAST only on transfer.

%% Deliberately broken case - advance LAST while payload is stalled
% The broken source keeps payload beat four stable but advances only its
% boundary counter on every valid clock. This is a metadata/data ownership
% bug: the receiver still gets all payloads in order but sees wrong frames.
healthy = model(4,3,false);
broken = model(4,3,true);
assert(isequaln(broken.reference,healthy.applied) && ...
    broken.faultActive && broken.frameFaultVisible && ...
    broken.applied.markerAdvanceWhileStalledCount == 3 && ...
    broken.applied.payloadHoldViolationCount == 0 && ...
    broken.applied.lastHoldViolationCount == 1 && ...
    broken.applied.dataCompleted, ...
    'P11:BrokenLastAdvance', ...
    'Broken mode must drift LAST while preserving the healthy payload path.');
assert(isequal(broken.applied.observedBoundaryBeatOrdinals,[5 9].') && ...
    isequal(broken.applied.completedPacketLengths,[5 4].') && ...
    broken.applied.trailingBeatCount == 3 && ...
    broken.applied.boundaryMismatchCount == 5 && ...
    ~broken.applied.framingValid, ...
    'P11:BrokenFramingSymptom', ...
    'The broken receiver must see 5, 4, then 3 unterminated beats.');
fprintf(['Broken: accepted=%d beats, lost=%d, duplicated=%d, ' ...
    'boundary mismatches=%d, completed packets=%d, trailing=%d beats.\n'], ...
    broken.applied.acceptedBeatCount,broken.applied.lostBeatCount, ...
    broken.applied.duplicateBeatCount, ...
    broken.applied.boundaryMismatchCount, ...
    broken.applied.observedPacketCount,broken.applied.trailingBeatCount);

brokenFigure = figure('Name',figureNames{4},'NumberTitle','off');
subplot(2,2,1);
stairs(healthy.cycle(visibleCycles), ...
    double(healthy.applied.sourceLast(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','healthy LAST');
hold on;
stairs(broken.cycle(visibleCycles), ...
    2+double(broken.applied.sourceLast(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','broken LAST');
stairs(broken.cycle(visibleCycles), ...
    4+double(broken.applied.sourceReady(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','ready');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Sideband state [binary, vertically offset]');
title('Broken LAST changes while beat four is still owed');
set(gca,'YTick',[0.5 2.5 4.5], ...
    'YTickLabel',{'healthy LAST','broken LAST','ready'});
ylim([-0.2 5.2]);
xlim([1 18]);
drawnow;

%% Broken changed view - expected and observed accepted boundaries
figure(brokenFigure);
subplot(2,2,2);
stem((1:12).',double(broken.applied.acceptedExpectedLast), ...
    'LineWidth',1.3,'DisplayName','expected LAST');
hold on;
stem((1:12).',2+double(broken.applied.acceptedLast), ...
    'LineWidth',1.3,'DisplayName','observed LAST');
hold off;
grid on;
xlabel('Accepted payload [beat ordinal from one]');
ylabel('Boundary state [binary, vertically offset]');
title('Accepted boundaries move from beats 4, 8, 12 to 5, 9');
set(gca,'YTick',[0.5 2.5], ...
    'YTickLabel',{'expected LAST','observed LAST'});
ylim([-0.2 3.2]);
xlim([1 12]);
drawnow;

%% Broken changed view - receiver segment lengths
figure(brokenFigure);
subplot(2,2,3);
receiverSegmentLengths = ...
    [broken.applied.completedPacketLengths;broken.applied.trailingBeatCount];
bar(1:numel(receiverSegmentLengths),receiverSegmentLengths);
grid on;
xlabel('Receiver segment [segment index from one]');
ylabel('Observed length [beats/segment]');
title('Receiver sees 5, 4, then an unterminated 3-beat tail');
ylim([0 6]);
drawnow;

%% Broken invariant view - payload order is deceptively intact
figure(brokenFigure);
subplot(2,2,4);
plot((1:12).',broken.applied.acceptedBeatOrdinals,'-o', ...
    'LineWidth',1.3,'DisplayName','received identity');
hold on;
plot((1:12).',(1:12).','--','LineWidth',1.1, ...
    'DisplayName','expected identity');
hold off;
grid on;
xlabel('Transfer order [accepted beat index from one]');
ylabel('Payload identity [beat ordinal from one]');
title('Payload checks alone miss the packet-boundary corruption');
legend('Location','best');
xlim([1 12]);
ylim([1 12]);
sgtitle('Deliberately broken case: LAST advances without payload');
drawnow;

%% Read the broken-case mechanism and its diagnostic limit
% During cycles 4-6, no transfer occurs. The healthy source leaves its LAST
% state attached to beat four. The broken boundary counter advances three
% times, so accepted LAST moves to payload beats 5 and 9; beat 12 no longer
% closes anything. All 12 payload words remain ordered, proving that payload
% conservation alone cannot prove framing integrity.
%
% If the erroneous drift equals a whole packet length, accepted boundaries
% can realign even though LAST changed illegally during the stall. Inspect
% both the LAST hold violation and receiver framing; a plausible output is
% not proof that the interface contract was obeyed.

%% Finish with deterministic checks and a two-sentence teach-back
% Run run_checks. Then answer: (1) which signals form one transferable beat,
% and (2) how can every payload arrive in order while packet framing fails?
% Explain the valid/ready/LAST mechanism, not the MATLAB plotting syntax.
