%% P10 - Apply Backpressure Without Losing Data
% Run one section at a time. P09's transfer rule appears on both sides of a
% registered FIFO. The FIFO lowers source ready only when it cannot store a
% new token on the current edge. Each sweep resets the other lever so the
% downstream stall and FIFO capacity remain independent.
figureNames = {'P10 baseline backpressure', ...
    'P10 consumer-stall sweep','P10 FIFO-depth sweep', ...
    'P10 broken ignored backpressure'};
for figureIndex = 1:numel(figureNames)
    delete(findall(groot,'Type','figure','Name',figureNames{figureIndex}));
end
clear model;
clc;

%% Read the two handshakes, then establish the deterministic baseline
% Before plotting, predict whether the producer stops immediately when the
% consumer lowers ready at cycle 5. Inspect the baseline once. Make no
% second prediction; later sections ask for observations and mechanisms.
baseline = model(3,5,false);
expectedEnqueueCycles = [1 2 3 4 5 6 10 11 12 13 14 15].';
expectedDequeueCycles = [2 3 4 10 11 12 13 14 15 16 17 18].';
assert(isequal(find(baseline.applied.enqueue),expectedEnqueueCycles) && ...
    isequal(find(baseline.applied.dequeue),expectedDequeueCycles) && ...
    isequal(baseline.applied.dequeuedTokenIndices,(1:12).') && ...
    baseline.applied.completed && baseline.applied.completionCycle == 18, ...
    'P10:BaselineTransfers', ...
    'The baseline must buffer and deliver all 12 ordered tokens.');
assert(isequal(find(baseline.applied.sourcePaused),[7 8 9].') && ...
    baseline.applied.peakOccupancyTokens == 3 && ...
    baseline.applied.maximumSourceWaitCycles == 3 && ...
    baseline.applied.maximumFifoResidenceCycles == 6 && ...
    baseline.applied.lostTokenCount == 0 && ...
    baseline.applied.finalConservationResidual == 0, ...
    'P10:BaselineBackpressure', ...
    'The full FIFO must pause rather than discard the source token.');
fprintf(['Baseline: enqueue edges [%s], dequeue edges [%s], peak=%d ' ...
    'tokens, source stalls=%d cycles, completion=%d cycles, rate=%0.6g ' ...
    'transfers/cycle through completion.\n'], ...
    sprintf('%d ',expectedEnqueueCycles), ...
    sprintf('%d ',expectedDequeueCycles), ...
    baseline.applied.peakOccupancyTokens, ...
    baseline.applied.sourceStallCycleCount, ...
    baseline.applied.completionCycle, ...
    baseline.applied.activeWindowTransferRate);
fprintf('%s; %s.\n',baseline.readyEquationText, ...
    baseline.occupancyEquationText);

%% Baseline view 1 - upstream valid, propagated ready, and enqueue
baselineFigure = figure('Name',figureNames{1},'NumberTitle','off');
visibleCycles = 1:20;
subplot(2,2,1);
stairs(baseline.cycle(visibleCycles), ...
    double(baseline.applied.sourceValid(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','source valid');
hold on;
stairs(baseline.cycle(visibleCycles), ...
    2+double(baseline.applied.sourceReady(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','FIFO ready');
stairs(baseline.cycle(visibleCycles), ...
    4+double(baseline.applied.enqueue(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','enqueue');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Upstream handshake [binary, vertically offset]');
title('Backpressure reaches the producer only when the FIFO fills');
set(gca,'YTick',[0.5 2.5 4.5], ...
    'YTickLabel',{'source valid','FIFO ready','enqueue'});
ylim([-0.2 5.2]);
xlim([1 20]);
drawnow;

%% Baseline view 2 - downstream valid, consumer ready, and dequeue
figure(baselineFigure);
subplot(2,2,2);
stairs(baseline.cycle(visibleCycles), ...
    double(baseline.applied.outputValid(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','output valid');
hold on;
stairs(baseline.cycle(visibleCycles), ...
    2+double(baseline.consumerReady(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','consumer ready');
stairs(baseline.cycle(visibleCycles), ...
    4+double(baseline.applied.dequeue(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','dequeue');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Downstream handshake [binary, vertically offset]');
title('The consumer accepts only output-valid and ready overlap');
set(gca,'YTick',[0.5 2.5 4.5], ...
    'YTickLabel',{'output valid','consumer ready','dequeue'});
ylim([-0.2 5.2]);
xlim([1 20]);
drawnow;

%% Baseline view 3 - FIFO occupancy and capacity
figure(baselineFigure);
subplot(2,2,3);
stairs(baseline.cycle(visibleCycles), ...
    baseline.applied.occupancyAfter(visibleCycles), ...
    'LineWidth',1.3,'DisplayName','occupancy after edge');
hold on;
yline(baseline.fifoDepth,'--','FIFO depth', ...
    'LabelVerticalAlignment','bottom');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Stored payloads after edge [tokens]');
title('The queue fills, then ready propagates low upstream');
xlim([1 20]);
ylim([0 baseline.fifoDepth+1]);
drawnow;

%% Baseline view 4 - held source and output token identities
figure(baselineFigure);
subplot(2,2,4);
stairs(baseline.cycle(visibleCycles), ...
    baseline.applied.sourceTokenIndex(visibleCycles), ...
    'LineWidth',1.3,'DisplayName','source offer');
hold on;
stairs(baseline.cycle(visibleCycles), ...
    baseline.applied.outputTokenIndex(visibleCycles),'--', ...
    'LineWidth',1.3,'DisplayName','FIFO output');
scatter(baseline.cycle(visibleCycles(baseline.applied.dequeue(visibleCycles))), ...
    baseline.applied.dequeuedTokenIndexByCycle( ...
        visibleCycles(baseline.applied.dequeue(visibleCycles))), ...
    38,'filled','DisplayName','consumer accepted');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Payload identity [token index from one]');
title('Both stalled interfaces hold the token still owed');
legend('Location','best');
xlim([1 20]);
sgtitle('P10 baseline: depth three and a five-cycle consumer stall');
drawnow;

%% Sweep 1 - consumer stall duration with FIFO depth fixed at three
% Lever 1 changes only ready-low cycles 5 onward. FIFO depth, payload list,
% registered behavior, and record allocation remain unchanged.
consumerStallSweep = 0:8;
stallCompletionCycles = zeros(size(consumerStallSweep));
stallSourcePauseCycles = zeros(size(consumerStallSweep));
stallPeakOccupancy = zeros(size(consumerStallSweep));
stallDeliveredCounts = zeros(size(consumerStallSweep));
for sweepIndex = 1:numel(consumerStallSweep)
    current = model(3,consumerStallSweep(sweepIndex),false);
    assert(current.fifoDepth == 3 && ...
        isequal(current.tokenCodes,baseline.tokenCodes) && ...
        isequal(current.applied.dequeuedTokenIndices,(1:12).') && ...
        current.applied.lostTokenCount == 0 && ...
        current.applied.finalConservationResidual == 0 && ...
        current.recordCycleCount == baseline.recordCycleCount, ...
        'P10:ConsumerStallSweepIsolation', ...
        ['Consumer-stall sweep must preserve depth, payloads, order, ' ...
        'conservation, and allocation.']);
    stallCompletionCycles(sweepIndex) = ...
        current.applied.completionCycle;
    stallSourcePauseCycles(sweepIndex) = ...
        current.applied.sourceStallCycleCount;
    stallPeakOccupancy(sweepIndex) = ...
        current.applied.peakOccupancyTokens;
    stallDeliveredCounts(sweepIndex) = ...
        current.applied.dequeuedTokenCount;
end
assert(isequal(stallCompletionCycles,13:21) && ...
    isequal(stallSourcePauseCycles,[0 0 0 1 2 3 4 5 6]) && ...
    isequal(stallPeakOccupancy,[1 2 3 3 3 3 3 3 3]) && ...
    all(stallDeliveredCounts == 12), ...
    'P10:ConsumerStallSweep', ...
    'Stall duration must move completion, fill, and backpressure exactly.');

stallFigure = figure('Name',figureNames{2},'NumberTitle','off');
subplot(2,2,1);
plot(consumerStallSweep,stallCompletionCycles,'-o','LineWidth',1.3);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Final dequeue edge [clock cycle]');
title('Consumer delay moves completion one-for-one');
drawnow;

%% Sweep 1 view 2 - propagated source stalls
figure(stallFigure);
subplot(2,2,2);
plot(consumerStallSweep,stallSourcePauseCycles,'-o','LineWidth',1.3);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Source valid without FIFO ready [cycles]');
title('Two free slots absorb the first two stalled edges');
drawnow;

%% Sweep 1 view 3 - bounded peak occupancy
figure(stallFigure);
subplot(2,2,3);
plot(consumerStallSweep,stallPeakOccupancy,'-o','LineWidth',1.3);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Peak FIFO occupancy [tokens]');
title('Occupancy saturates at the fixed three-token depth');
ylim([0 4]);
drawnow;

%% Sweep 1 view 4 - delivered count remains fixed
figure(stallFigure);
subplot(2,2,4);
bar(consumerStallSweep,stallDeliveredCounts);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Delivered payloads [tokens]');
title('Backpressure changes timing, not the 12-token sequence');
ylim([0 13]);
sgtitle('Sweep 1: move consumer availability at fixed FIFO depth');
drawnow;

%% Read the first changed-view mechanism
% At the stall start, one token is already stored. A depth-three FIFO can
% absorb two more arrivals before source ready falls. Any remaining stall
% cycles pause one stable producer offer. Completion is 13+stallCycles;
% no token is created, duplicated, reordered, or lost.

%% Sweep 2 - FIFO depth with the consumer stall fixed at five cycles
% Reset the consumer stall to five. Lever 2 changes only capacity. This is
% a bounded cause-and-effect comparison, not P12's rate-based sizing proof.
fifoDepthSweep = 1:6;
depthSourcePauseCycles = zeros(size(fifoDepthSweep));
depthPeakOccupancy = zeros(size(fifoDepthSweep));
depthCompletionCycles = zeros(size(fifoDepthSweep));
depthDeliveredCounts = zeros(size(fifoDepthSweep));
for sweepIndex = 1:numel(fifoDepthSweep)
    current = model(fifoDepthSweep(sweepIndex),5,false);
    assert(current.consumerStallCycles == 5 && ...
        isequal(current.consumerReady,baseline.consumerReady) && ...
        isequal(current.tokenCodes,baseline.tokenCodes) && ...
        isequal(current.applied.dequeuedTokenIndices,(1:12).') && ...
        current.applied.lostTokenCount == 0 && ...
        current.applied.finalConservationResidual == 0, ...
        'P10:FifoDepthSweepIsolation', ...
        ['FIFO-depth sweep must preserve readiness, payloads, order, ' ...
        'and conservation.']);
    depthSourcePauseCycles(sweepIndex) = ...
        current.applied.sourceStallCycleCount;
    depthPeakOccupancy(sweepIndex) = ...
        current.applied.peakOccupancyTokens;
    depthCompletionCycles(sweepIndex) = ...
        current.applied.completionCycle;
    depthDeliveredCounts(sweepIndex) = ...
        current.applied.dequeuedTokenCount;
end
assert(isequal(depthSourcePauseCycles,[5 4 3 2 1 0]) && ...
    isequal(depthPeakOccupancy,1:6) && ...
    all(depthCompletionCycles == 18) && ...
    all(depthDeliveredCounts == 12), ...
    'P10:FifoDepthSweep', ...
    'Each added slot must postpone source backpressure by one cycle.');

depthFigure = figure('Name',figureNames{3},'NumberTitle','off');
subplot(2,2,1);
plot(fifoDepthSweep,depthSourcePauseCycles,'-o','LineWidth',1.3);
grid on;
xlabel('FIFO depth [tokens]');
ylabel('Source valid without FIFO ready [cycles]');
title('Each extra slot absorbs one more stalled arrival');
drawnow;

%% Sweep 2 view 2 - capacity reached
figure(depthFigure);
subplot(2,2,2);
plot(fifoDepthSweep,depthPeakOccupancy,'-o','LineWidth',1.3);
grid on;
xlabel('FIFO depth [tokens]');
ylabel('Peak FIFO occupancy [tokens]');
title('The five-cycle stall exercises every selected depth');
drawnow;

%% Sweep 2 view 3 - completion cannot outrun the consumer
figure(depthFigure);
subplot(2,2,3);
plot(fifoDepthSweep,depthCompletionCycles,'-o','LineWidth',1.3);
grid on;
xlabel('FIFO depth [tokens]');
ylabel('Final dequeue edge [clock cycle]');
title('More storage does not restore missing consumer service');
drawnow;

%% Sweep 2 view 4 - delivery remains conserved
figure(depthFigure);
subplot(2,2,4);
bar(fifoDepthSweep,depthDeliveredCounts);
grid on;
xlabel('FIFO depth [tokens]');
ylabel('Delivered payloads [tokens]');
title('Every healthy depth preserves all 12 payloads');
ylim([0 13]);
sgtitle('Sweep 2: move finite capacity at fixed consumer availability');
drawnow;

%% Read the second changed-view mechanism
% Capacity delays when backpressure reaches the source. It does not make
% the consumer ready sooner, so all depths complete on cycle 18. A full
% FIFO may dequeue and enqueue together on one edge: the departing token
% creates the slot accepted by the incoming token.

%% Deliberately broken case - producer advances while FIFO ready is low
% The broken producer treats every valid offer as consumed. During cycles
% 7-9 the FIFO is full and cannot accept; token indices 7-9 disappear.
healthy = model(3,5,false);
broken = model(3,5,true);
assert(isequaln(broken.reference,healthy.applied) && ...
    isequal(find(broken.applied.dropAttempt),[7 8 9].') && ...
    isequal(find(broken.applied.sourceHoldViolation),[8 9 10].') && ...
    isequal(find(broken.applied.lostTokenMask),[7 8 9].') && ...
    isequal(broken.applied.dequeuedTokenIndices, ...
        [1 2 3 4 5 6 10 11 12].') && ...
    broken.applied.dropCount == 3 && broken.faultActive && ...
    ~broken.applied.completed, ...
    'P10:BrokenIgnoredBackpressure', ...
    'Ignoring propagated ready must lose exactly token indices 7-9.');

brokenFigure = figure('Name',figureNames{4},'NumberTitle','off');
subplot(2,2,1);
stairs(broken.cycle(1:18),broken.applied.sourceTokenIndex(1:18), ...
    '--','LineWidth',1.3,'DisplayName','broken source offer');
hold on;
stairs(healthy.cycle(1:18),healthy.applied.sourceTokenIndex(1:18), ...
    'LineWidth',1.3,'DisplayName','healthy held offer');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Source payload identity [token index from one]');
title('Broken source changes the offer while FIFO ready is low');
legend('Location','best');
xlim([1 18]);
drawnow;

%% Broken view 2 - storage remains bounded
figure(brokenFigure);
subplot(2,2,2);
stairs(healthy.cycle(1:18),healthy.applied.occupancyAfter(1:18), ...
    'LineWidth',1.3,'DisplayName','healthy occupancy');
hold on;
stairs(broken.cycle(1:18),broken.applied.occupancyAfter(1:18), ...
    '--','LineWidth',1.3,'DisplayName','broken occupancy');
yline(broken.fifoDepth,':','FIFO depth');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Stored payloads after edge [tokens]');
title('The FIFO does not overflow; the producer discards offers');
legend('Location','best');
xlim([1 18]);
ylim([0 broken.fifoDepth+1]);
drawnow;

%% Broken view 3 - accepted sequence exposes the gap
figure(brokenFigure);
subplot(2,2,3);
plot(1:numel(healthy.applied.dequeuedTokenIndices), ...
    healthy.applied.dequeuedTokenIndices,'-o','LineWidth',1.3, ...
    'DisplayName','healthy');
hold on;
plot(1:numel(broken.applied.dequeuedTokenIndices), ...
    broken.applied.dequeuedTokenIndices,'--x','LineWidth',1.3, ...
    'DisplayName','broken');
hold off;
grid on;
xlabel('Consumer transfer ordinal [token index from one]');
ylabel('Delivered payload identity [token index from one]');
title('The consumer jumps from token 6 to token 10');
legend('Location','best');
drawnow;

%% Broken view 4 - exact drop and hold-rule symptoms
figure(brokenFigure);
subplot(2,2,4);
stem(broken.cycle(1:18),double(broken.applied.dropAttempt(1:18)), ...
    'filled','LineWidth',1.1,'DisplayName','drop attempt');
hold on;
stem(broken.cycle(1:18), ...
    2+double(broken.applied.sourceHoldViolation(1:18)), ...
    'LineWidth',1.1,'DisplayName','next-cycle hold violation');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Fault indicators [binary, vertically offset]');
title('Drops at 7-9 cause successor violations at 8-10');
set(gca,'YTick',[0.5 2.5], ...
    'YTickLabel',{'drop attempt','hold violation'});
ylim([-0.2 3.2]);
xlim([1 18]);
sgtitle('Deliberately broken case: producer ignores FIFO backpressure');
drawnow;

%% Mechanism-first explanation, limits, and next step
% A healthy source advances only on sourceValid && sourceReady. The FIFO
% advances its output only on outputValid && consumerReady. The occupancy
% recurrence conserves accepted tokens between those edges. Ignoring ready
% advances past an offer that no storage accepted, so sequence gaps appear
% even though the FIFO itself stays within bounds. Now run run_checks.m and
% answer checks.md one prompt at a time before giving the teach-back.
