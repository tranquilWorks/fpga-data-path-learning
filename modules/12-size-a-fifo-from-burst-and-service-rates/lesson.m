%% P12 - Size a FIFO from Burst and Service Rates
% Guiding question:
% What inputs, observable effects, and failure modes matter when you size a FIFO from Burst and Service Rates?
clear model interactive;

%% Read - connect P11 packet boundaries to a finite storage interval
% P11 showed that valid, payload, and LAST transfer together. Once a finite
% packet burst is offered to a registered FIFO, depth must cover the largest
% lossless backlog created before downstream service catches up.
disp(['Mental model: first compute an unbounded registered queue. Its ' ...
    'maximum occupancy is the rate-imbalance storage requirement.']);
disp(['Prediction: does a 16-word FIFO hold 24 words offered over eight ' ...
    'cycles when service removes one stored word per cycle?']);

%% Visualize baseline view 1 - cumulative arrivals and departures
baseline = model(8,3,1,17,false);
delete(findall(groot,'Type','figure','Name','P12 lesson baseline'));
baselineFigure = figure('Name','P12 lesson baseline','NumberTitle','off');
subplot(2,1,1);
stairs(baseline.cycle,baseline.reference.cumulativeArrivals, ...
    'LineWidth',1.3,'DisplayName','cumulative arrivals');
hold on;
stairs(baseline.cycle,baseline.reference.cumulativeDepartures, ...
    'LineWidth',1.3,'DisplayName','cumulative departures');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Cumulative work [words]');
title('The vertical arrival-service gap grows during the burst');
legend('Location','best');
xlim([1 28]);
drawnow;

%% Visualize baseline view 2 - reveal the required depth
figure(baselineFigure);
subplot(2,1,2);
stairs(baseline.cycle,baseline.reference.occupancyAfter, ...
    'LineWidth',1.3,'DisplayName','lossless occupancy');
hold on;
yline(baseline.appliedDepthWords,'--','selected depth = 17 words');
scatter(baseline.reference.peakCycle,baseline.requiredDepthWords,52, ...
    'filled','DisplayName','required peak');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('FIFO occupancy after edge [words]');
title('Peak occupancy is 17 words on cycle eight');
legend('Location','best');
xlim([1 28]);
ylim([0 19]);
fprintf(['Baseline: 24 offered, required depth %d words, zero refused, ' ...
    'drain cycle %d.\n'],baseline.requiredDepthWords, ...
    baseline.reference.drainCompleteCycle);
drawnow;

%% Read the registered mechanism
% P10 established a non-fall-through FIFO. Stored words may depart first on
% an edge and free slots for new admissions, but arrivals cannot be served
% until a later edge. For a B-cycle constant burst, arrival A, service S,
% and empty initial state: D=A+(B-1)*max(A-S,0).
disp(baseline.constantRateEquationText);
disp(baseline.registeredRuleText);

%% Move lever 1 only - burst duration
burstCases = [1 2 4 6 8];
burstDepths = zeros(size(burstCases));
for caseIndex = 1:numel(burstCases)
    current = model(burstCases(caseIndex),3,1,32,false);
    burstDepths(caseIndex) = current.requiredDepthWords;
end
assert(isequal(burstDepths,[3 5 9 13 17]), ...
    'P12:LessonBurstSweep','Burst sweep changed.');
delete(findall(groot,'Type','figure','Name', ...
    'P12 lesson burst lever'));
figure('Name','P12 lesson burst lever','NumberTitle','off');
plot(burstCases,burstDepths,'-o','LineWidth',1.3);
grid on;
xlabel('Burst duration [cycles]');
ylabel('Required FIFO depth [words]');
title('Changed view: longer mismatch requires more storage');
drawnow;

%% Read lever 1 mechanism, then reset burst duration to eight
% The first arrival batch needs A=3 slots. Every later burst edge adds
% A-S=2 words while arrival exceeds service. Reset B before moving service.
disp(['Burst mechanism: [3 5 9 13 17] is three initial words plus two ' ...
    'additional words for every later burst edge.']);

%% Move lever 2 only - guaranteed service rate
serviceCases = 0:4;
serviceDepths = zeros(size(serviceCases));
for caseIndex = 1:numel(serviceCases)
    current = model(8,3,serviceCases(caseIndex),32,false);
    serviceDepths(caseIndex) = current.requiredDepthWords;
end
assert(isequal(serviceDepths,[24 17 10 3 3]), ...
    'P12:LessonServiceSweep','Service sweep changed.');
delete(findall(groot,'Type','figure','Name', ...
    'P12 lesson service lever'));
figure('Name','P12 lesson service lever','NumberTitle','off');
plot(serviceCases,serviceDepths,'-o','LineWidth',1.3);
grid on;
xlabel('Guaranteed service rate [words/cycle]');
ylabel('Required FIFO depth [words]');
title('Changed view: service closes backlog, staging remains');
drawnow;

%% Read lever 2 mechanism before the broken case
% With no service the FIFO holds all 24 words and does not drain in the
% bounded trace. At or above three words/cycle, it still stages the first
% three arrivals because a registered FIFO cannot dequeue them immediately.
disp(['Service mechanism: more stored-word departures reduce backlog; ' ...
    'unused service is neither banked nor applied to same-edge arrivals.']);

%% Deliberately broken case - assume fall-through when sizing
healthy = model(8,3,1,17,false);
broken = model(8,3,1,17,true);
assert(broken.fallThroughEstimateWords == 16 && ...
    broken.requiredDepthWords == 17 && ...
    broken.applied.notAcceptedWordCount == 1 && ...
    broken.applied.firstBackpressureCycle == 8, ...
    'P12:LessonBrokenCase','Broken sizing symptom changed.');
delete(findall(groot,'Type','figure','Name', ...
    'P12 lesson broken sizing'));
brokenFigure = figure('Name','P12 lesson broken sizing', ...
    'NumberTitle','off');
subplot(2,1,1);
stairs(healthy.cycle,healthy.reference.occupancyAfter, ...
    'LineWidth',1.3,'DisplayName','required lossless backlog');
hold on;
stairs(broken.cycle,broken.applied.occupancyAfter,'--', ...
    'LineWidth',1.3,'DisplayName','depth-16 clipped occupancy');
yline(16,':','broken estimate');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('FIFO occupancy after edge [words]');
title('The clipped trace looks bounded because one word was not admitted');
legend('Location','best');
xlim([1 28]);
drawnow;

%% Broken view 2 - reveal the admission failure
figure(brokenFigure);
subplot(2,1,2);
bar(1:8,[broken.applied.admittedWords(1:8) ...
    broken.applied.notAcceptedWords(1:8)],'stacked');
grid on;
xlabel('Burst edge [clock cycle]');
ylabel('Offered admission result [words]');
title('Cycle eight needs one held and retried word');
legend({'admitted','not accepted'},'Location','best');
drawnow;

%% Explain, explore, check, and teach back
% The broken estimate serves a new arrival on the same empty edge, which
% contradicts the declared registered FIFO. Full requests backpressure: a
% P11-compliant producer holds payload and LAST. The word is lost only if
% that valid/ready obligation is unavailable or ignored.
disp(broken.backpressureRuleText);
disp(['Run experiment one section at a time for all metrics, then open the ' ...
    'bounded explorer, run run_checks, and give the teach-back.']);
interactive;
