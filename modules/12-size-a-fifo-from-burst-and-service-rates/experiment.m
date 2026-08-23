%% P12 - Size a FIFO from Burst and Service Rates
% Read -> visualize baseline -> move one lever -> visualize the delta ->
% read the mechanism. Reset before the second lever, then run one broken
% registered-versus-fall-through sizing case.
clear model interactive;
figureNames = {'P12 registered FIFO baseline', ...
    'P12 burst-duration sweep','P12 service-rate sweep', ...
    'P12 broken fall-through sizing'};
for figureIndex = 1:numel(figureNames)
    delete(findall(groot,'Type','figure','Name',figureNames{figureIndex}));
end

%% Read - turn P11's finite packet burst into a storage requirement
% P11 attached LAST to the final accepted beat. P12 now counts a finite
% aggregate burst in words and asks how many registered FIFO entries are
% needed while a slower downstream service removes stored words.
disp(['Mental model: required depth is the largest lossless occupancy of ' ...
    'an unbounded reference queue, never the peak of an already-clipped FIFO.']);
disp(['Prediction: can 16 words hold an eight-cycle burst at 3 words/cycle ' ...
    'when registered service removes 1 stored word/cycle?']);

%% Visualize the deterministic baseline - compute before plotting
baseline = model(8,3,1,17,false);
expectedOccupancy = [3 5 7 9 11 13 15 17 ...
    16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0 ...
    zeros(1,15)].';
assert(isequal(baseline.reference.occupancyAfter,expectedOccupancy) && ...
    baseline.burstWordCount == 24 && ...
    baseline.requiredDepthWords == 17 && ...
    baseline.reference.peakCycle == 8 && ...
    baseline.reference.drainCompleteCycle == 25 && ...
    baseline.applied.notAcceptedWordCount == 0, ...
    'P12:ExperimentBaseline', ...
    'Baseline sizing, occupancy, drain, or admission changed.');
baselineFigure = figure('Name',figureNames{1},'NumberTitle','off');

%% Baseline view 1 - reveal offered and serviced words per clock
figure(baselineFigure);
subplot(2,2,1);
stairs(baseline.cycle,baseline.arrivalWords,'LineWidth',1.3, ...
    'DisplayName','offered arrivals');
hold on;
stairs(baseline.cycle,baseline.serviceCapacityWords,'--', ...
    'LineWidth',1.3,'DisplayName','service capacity');
stairs(baseline.cycle,baseline.reference.departedWords,':', ...
    'LineWidth',1.5,'DisplayName','actual departures');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Flow [words/cycle]');
title('Eight burst cycles offer three while service removes one');
legend('Location','best');
xlim([1 28]);
drawnow;

%% Baseline view 2 - reveal the cumulative gap
figure(baselineFigure);
subplot(2,2,2);
stairs(baseline.cycle,baseline.reference.cumulativeArrivals, ...
    'LineWidth',1.3,'DisplayName','cumulative arrivals');
hold on;
stairs(baseline.cycle,baseline.reference.cumulativeDepartures, ...
    'LineWidth',1.3,'DisplayName','cumulative departures');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Cumulative work [words]');
title('Their vertical gap is registered FIFO occupancy');
legend('Location','best');
xlim([1 28]);
drawnow;

%% Baseline view 3 - reveal occupancy and selected depth
figure(baselineFigure);
subplot(2,2,3);
stairs(baseline.cycle,baseline.reference.occupancyAfter, ...
    'LineWidth',1.3,'DisplayName','lossless reference occupancy');
hold on;
yline(baseline.appliedDepthWords,'--','selected depth = 17 words', ...
    'LineWidth',1.2);
scatter(baseline.reference.peakCycle,baseline.requiredDepthWords,52, ...
    'filled','DisplayName','required peak');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('FIFO occupancy after edge [words]');
title('The peak on cycle eight sets required depth');
legend('Location','best');
xlim([1 28]);
ylim([0 19]);
drawnow;

%% Baseline view 4 - reveal headroom and capacity result
figure(baselineFigure);
subplot(2,2,4);
stairs(baseline.cycle,baseline.applied.headroomAfter, ...
    'LineWidth',1.3,'DisplayName','headroom after edge');
hold on;
stairs(baseline.cycle,baseline.applied.cumulativeNotAccepted, ...
    '--','LineWidth',1.3,'DisplayName','not accepted');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Capacity accounting [words]');
title('Exact depth reaches zero headroom without refusing work');
legend('Location','best');
xlim([1 28]);
sgtitle('P12 baseline: exact registered depth is 17 words');
fprintf(['Baseline: offered=%d words, required=%d words, peak cycle=%d, ' ...
    'drain cycle=%d, not accepted=%d words.\n'], ...
    baseline.burstWordCount,baseline.requiredDepthWords, ...
    baseline.reference.peakCycle, ...
    baseline.reference.drainCompleteCycle, ...
    baseline.applied.notAcceptedWordCount);
drawnow;

%% Read the baseline mechanism before moving a lever
% Stored words depart first, then their freed slots may accept arrivals.
% New arrivals cannot depart until a later edge. The first three-word batch
% therefore needs storage even if service later matches or exceeds arrival.
disp(baseline.referenceEquationText);
disp(baseline.requiredDepthEquationText);
disp(baseline.constantRateEquationText);
disp(baseline.registeredRuleText);

%% Sweep 1 - move burst duration only at fixed arrival and service rates
burstCycleSweep = [1 2 4 6 8];
burstRequiredDepth = zeros(size(burstCycleSweep));
burstCompletionCycle = zeros(size(burstCycleSweep));
burstWordCount = zeros(size(burstCycleSweep));
for sweepIndex = 1:numel(burstCycleSweep)
    current = model(burstCycleSweep(sweepIndex),3,1,32,false);
    assert(current.arrivalRateWordsPerCycle == 3 && ...
        current.serviceRateWordsPerCycle == 1 && ...
        current.fifoDepthWords == 32 && ...
        ~current.brokenAssumeFallThrough && ...
        current.applied.notAcceptedWordCount == 0, ...
        'P12:ExperimentBurstIsolation', ...
        'Burst sweep must hold arrival rate, service, depth, and fault fixed.');
    burstRequiredDepth(sweepIndex) = current.requiredDepthWords;
    burstCompletionCycle(sweepIndex) = ...
        current.reference.drainCompleteCycle;
    burstWordCount(sweepIndex) = current.burstWordCount;
end
assert(isequal(burstRequiredDepth,[3 5 9 13 17]) && ...
    isequal(burstCompletionCycle,[4 7 13 19 25]) && ...
    isequal(burstWordCount,[3 6 12 18 24]), ...
    'P12:ExperimentBurstSweep', ...
    'Burst-duration sweep results changed.');
burstFigure = figure('Name',figureNames{2},'NumberTitle','off');

%% Sweep 1 changed view - reveal required depth
figure(burstFigure);
subplot(2,1,1);
plot(burstCycleSweep,burstRequiredDepth,'-o','LineWidth',1.3);
grid on;
xlabel('Burst duration [cycles]');
ylabel('Required FIFO depth [words]');
title('Longer positive rate mismatch accumulates more words');
drawnow;

%% Sweep 1 complementary view - reveal total work and drain edge
figure(burstFigure);
subplot(2,1,2);
plot(burstCycleSweep,burstWordCount,'-o','LineWidth',1.3, ...
    'DisplayName','offered words');
hold on;
plot(burstCycleSweep,burstCompletionCycle,'--s','LineWidth',1.3, ...
    'DisplayName','drain cycle');
hold off;
grid on;
xlabel('Burst duration [cycles]');
ylabel('Count [words] or time [clock cycle]');
title('More offered work raises both storage and drain time');
legend('Location','best');
sgtitle('Sweep 1: move burst duration at fixed 3-in/1-out rates');
drawnow;

%% Explain lever 1, then reset to the eight-cycle baseline
% At fixed A=3 and S=1, every burst edge after the first adds two words.
% The exact registered formula is D=A+(B-1)*(A-S), so the first batch costs
% three entries and each additional burst cycle costs two more.
disp(['Lever 1 mechanism: longer burst duration extends the interval over ' ...
    'which arrivals exceed guaranteed service. Reset B to eight now.']);

%% Sweep 2 - move service rate only at fixed eight-cycle burst
serviceRateSweep = 0:4;
serviceRequiredDepth = zeros(size(serviceRateSweep));
serviceCompletionCycle = NaN(size(serviceRateSweep));
serviceTimedOut = false(size(serviceRateSweep));
for sweepIndex = 1:numel(serviceRateSweep)
    current = model(8,3,serviceRateSweep(sweepIndex),32,false);
    assert(current.burstCycles == 8 && ...
        current.arrivalRateWordsPerCycle == 3 && ...
        current.fifoDepthWords == 32 && ...
        ~current.brokenAssumeFallThrough && ...
        isequal(current.arrivalWords, ...
            [3*ones(8,1);zeros(32,1)]) && ...
        current.applied.notAcceptedWordCount == 0, ...
        'P12:ExperimentServiceIsolation', ...
        'Service sweep must hold burst, arrival rate, depth, and fault fixed.');
    serviceRequiredDepth(sweepIndex) = current.requiredDepthWords;
    serviceCompletionCycle(sweepIndex) = ...
        current.reference.drainCompleteCycle;
    serviceTimedOut(sweepIndex) = current.reference.drainTimedOut;
end
assert(isequal(serviceRequiredDepth,[24 17 10 3 3]) && ...
    isequaln(serviceCompletionCycle,[NaN 25 13 9 9]) && ...
    isequal(serviceTimedOut,[true false false false false]), ...
    'P12:ExperimentServiceSweep', ...
    'Service-rate sweep results changed.');
serviceFigure = figure('Name',figureNames{3},'NumberTitle','off');

%% Sweep 2 changed view - reveal required depth
figure(serviceFigure);
subplot(2,1,1);
plot(serviceRateSweep,serviceRequiredDepth,'-o','LineWidth',1.3);
grid on;
xlabel('Guaranteed service rate [words/cycle]');
ylabel('Required FIFO depth [words]');
title('More service closes the backlog until one staging batch remains');
drawnow;

%% Sweep 2 complementary view - reveal completion and no-drain limit
figure(serviceFigure);
subplot(2,1,2);
plot(serviceRateSweep(2:end),serviceCompletionCycle(2:end), ...
    '-o','LineWidth',1.3,'DisplayName','drain complete');
hold on;
scatter(serviceRateSweep(1),baseline.recordCycleCount,62,'x', ...
    'LineWidth',1.5,'DisplayName','no drain by cycle 40');
hold off;
grid on;
xlabel('Guaranteed service rate [words/cycle]');
ylabel('Drain completion [clock cycle]');
title('Zero service returns a bounded no-drain result');
legend('Location','best');
sgtitle('Sweep 2: move service at fixed eight-cycle, three-word burst');
drawnow;

%% Explain lever 2 before deliberately breaking one assumption
% Greater service removes more stored words before each new admission. Once
% S>=A, the registered FIFO still needs A entries for the first batch; this
% is staging depth, not a claim about a zero-depth fall-through channel.
disp(['Lever 2 mechanism: service reduces stored backlog but unused ' ...
    'capacity is not banked and cannot serve a future arrival.']);

%% Broken case - size a registered FIFO with a fall-through equation
healthy = model(8,3,1,17,false);
broken = model(8,3,1,17,true);
assert(healthy.requiredDepthWords == 17 && ...
    broken.fallThroughEstimateWords == 16 && ...
    broken.appliedDepthWords == 16 && ...
    broken.applied.notAcceptedWordCount == 1 && ...
    isequal(find(broken.applied.notAcceptedWords),8) && ...
    isequaln(broken.reference,healthy.reference) && ...
    broken.faultActive && broken.faultVisible, ...
    'P12:ExperimentBrokenCase', ...
    'Broken fall-through estimate must refuse one cycle-eight word.');
brokenFigure = figure('Name',figureNames{4},'NumberTitle','off');

%% Broken view 1 - compare required backlog with clipped occupancy
figure(brokenFigure);
subplot(2,1,1);
stairs(healthy.cycle,healthy.reference.occupancyAfter, ...
    'LineWidth',1.3,'DisplayName','required lossless backlog');
hold on;
stairs(broken.cycle,broken.applied.occupancyAfter,'--', ...
    'LineWidth',1.3,'DisplayName','broken depth-16 FIFO');
yline(broken.appliedDepthWords,':','broken depth = 16 words', ...
    'LineWidth',1.2);
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('FIFO occupancy after edge [words]');
title('Clipping occupancy at 16 hides the missing admission');
legend('Location','best');
xlim([1 28]);
drawnow;

%% Broken view 2 - reveal the exact source-side symptom
figure(brokenFigure);
subplot(2,1,2);
bar(broken.cycle(1:8), ...
    [broken.applied.admittedWords(1:8) ...
    broken.applied.notAcceptedWords(1:8)],'stacked');
grid on;
xlabel('Burst edge [clock cycle]');
ylabel('Offered admission result [words]');
title('Cycle eight needs one held/retried word');
legend({'admitted','not accepted'},'Location','best');
sgtitle('Broken case: fall-through sizing used for a registered FIFO');
fprintf(['Broken: exact=%d words, estimate=%d words, shortfall=%d word, ' ...
    'first backpressure cycle=%d, conditional loss if ignored=%d word.\n'], ...
    broken.requiredDepthWords,broken.fallThroughEstimateWords, ...
    broken.depthShortfallWords, ...
    broken.applied.firstBackpressureCycle, ...
    broken.applied.conditionalLossIfIgnoredWords);
drawnow;

%% Read the failure mechanism, then explore and check
% The broken equation subtracts service from arrivals on the same empty
% edge, as though the FIFO were fall-through. P10's registered FIFO cannot
% dequeue a newly arriving word. A full result requests backpressure; a
% P11-compliant producer holds payload and LAST. The word is lost only when
% that upstream ready/hold contract is unavailable or ignored.
disp(broken.backpressureRuleText);
disp(['Run interactive, then run_checks. Answer checks.md one prompt at a ' ...
    'time and finish with the two-sentence teach-back.']);
