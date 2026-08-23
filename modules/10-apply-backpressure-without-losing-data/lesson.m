%% P10 - Apply Backpressure Without Losing Data
% Guiding question:
% What inputs, observable effects, and failure modes matter when you apply Backpressure Without Losing Data?
clear model interactive;

%% Read - compose P09 handshakes around finite storage
% P09 required valid && ready on one edge and stable payload while stalled.
% P10 places a registered FIFO between an upstream and downstream instance
% of that rule. Accepted input tokens become occupancy until a downstream
% handshake removes them.
disp(['Mental model: a finite FIFO absorbs a temporary consumer pause, ' ...
    'then lowers source ready before accepting more than it can retain.']);
disp(['Prediction: consumer ready falls on cycle 5 with two free slots. ' ...
    'Does the source stop immediately, or only after those slots fill?']);

%% Visualize the deterministic baseline upstream handshake
baseline = model(3,5,false);
visibleCycles = 1:20;
delete(findall(groot,'Type','figure','Name','P10 lesson baseline'));
baselineFigure = figure('Name','P10 lesson baseline');
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
title('Source pauses only after finite storage fills');
set(gca,'YTick',[0.5 2.5 4.5], ...
    'YTickLabel',{'source valid','FIFO ready','enqueue'});
ylim([-0.2 5.2]);
xlim([1 20]);
drawnow;

%% Baseline view 2 - reveal the downstream handshake
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
title('No output token leaves without consumer ready');
set(gca,'YTick',[0.5 2.5 4.5], ...
    'YTickLabel',{'output valid','consumer ready','dequeue'});
ylim([-0.2 5.2]);
xlim([1 20]);
drawnow;

%% Baseline view 3 - reveal conserved occupancy
figure(baselineFigure);
subplot(2,2,3);
stairs(baseline.cycle(visibleCycles), ...
    baseline.applied.occupancyAfter(visibleCycles),'LineWidth',1.3);
hold on;
yline(baseline.fifoDepth,'--','FIFO depth');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Stored payloads after edge [tokens]');
title('Occupancy rises to three and never crosses capacity');
xlim([1 20]);
ylim([0 4]);
drawnow;

%% Baseline view 4 - reveal both held token identities
figure(baselineFigure);
subplot(2,2,4);
stairs(baseline.cycle(visibleCycles), ...
    baseline.applied.sourceTokenIndex(visibleCycles), ...
    'LineWidth',1.3,'DisplayName','source offer');
hold on;
stairs(baseline.cycle(visibleCycles), ...
    baseline.applied.outputTokenIndex(visibleCycles),'--', ...
    'LineWidth',1.3,'DisplayName','FIFO output');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Payload identity [token index from one]');
title('Token 7 waits upstream while token 4 waits downstream');
legend('Location','best');
xlim([1 20]);
sgtitle('P10 baseline: depth three, consumer ready low on cycles 5-9');
fprintf(['Baseline source stalls=[7 8 9], peak=%d tokens, ' ...
    'completion=%d cycles, delivered=%d, lost=%d.\n'], ...
    baseline.applied.peakOccupancyTokens, ...
    baseline.applied.completionCycle, ...
    baseline.applied.dequeuedTokenCount, ...
    baseline.applied.lostTokenCount);
drawnow;

%% Read the baseline mechanism
% Make no second prediction. Enqueue and dequeue each require their own
% valid && ready overlap. Two free slots absorb cycles 5-6. On cycles 7-9,
% the full FIFO lowers source ready and the producer holds token 7. When
% dequeue and enqueue are both one, occupancy stays flat and one token is
% replaced without a bubble.
disp(baseline.inputEquationText);
disp(baseline.outputEquationText);
disp(baseline.readyEquationText);
disp(baseline.occupancyEquationText);

%% Move lever 1 - consumer stall duration at fixed depth three
stallCases = 0:8;
stallCompletion = zeros(size(stallCases));
stallSourcePause = zeros(size(stallCases));
for caseIndex = 1:numel(stallCases)
    current = model(3,stallCases(caseIndex),false);
    stallCompletion(caseIndex) = current.applied.completionCycle;
    stallSourcePause(caseIndex) = current.applied.sourceStallCycleCount;
end
delete(findall(groot,'Type','figure','Name','P10 lesson stall sweep'));
stallFigure = figure('Name','P10 lesson stall sweep');
subplot(2,1,1);
plot(stallCases,stallCompletion,'-o','LineWidth',1.3);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Final dequeue edge [clock cycle]');
title('Changed view: completion is 13 plus the consumer stall');
drawnow;

%% Lever 1 view 2 - reveal propagated backpressure
figure(stallFigure);
subplot(2,1,2);
plot(stallCases,stallSourcePause,'-o','LineWidth',1.3);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Source valid without FIFO ready [cycles]');
title('Only stall time beyond two free slots reaches the source');
drawnow;

%% Explain lever 1, reset, then move lever 2
% The two available slots absorb the first two blocked output edges. Longer
% stalls pause one stable source token per extra cycle. Reset the stall to
% five and vary only capacity; do not infer a rate-based sizing rule.
depthCases = 1:6;
depthSourcePause = zeros(size(depthCases));
depthCompletion = zeros(size(depthCases));
for caseIndex = 1:numel(depthCases)
    current = model(depthCases(caseIndex),5,false);
    depthSourcePause(caseIndex) = current.applied.sourceStallCycleCount;
    depthCompletion(caseIndex) = current.applied.completionCycle;
end
delete(findall(groot,'Type','figure','Name','P10 lesson depth sweep'));
depthFigure = figure('Name','P10 lesson depth sweep');
subplot(2,1,1);
plot(depthCases,depthSourcePause,'-o','LineWidth',1.3);
grid on;
xlabel('FIFO depth [tokens]');
ylabel('Source valid without FIFO ready [cycles]');
title('Changed view: each slot absorbs one stalled arrival');
drawnow;

%% Lever 2 view 2 - reveal unchanged downstream completion
figure(depthFigure);
subplot(2,1,2);
plot(depthCases,depthCompletion,'-o','LineWidth',1.3);
grid on;
xlabel('FIFO depth [tokens]');
ylabel('Final dequeue edge [clock cycle]');
title('Capacity cannot restore five cycles of consumer service');
drawnow;

%% Explain lever 2, then break the source hold rule
% Every healthy depth conserves and orders all 12 payloads. Greater depth
% changes when ready propagates upstream, not when the consumer returns.
% The deliberately broken producer advances on valid alone during the
% three ready-low source edges and discards tokens 7-9.
healthy = model(3,5,false);
broken = model(3,5,true);
delete(findall(groot,'Type','figure','Name', ...
    'P10 lesson broken backpressure'));
brokenFigure = figure('Name','P10 lesson broken backpressure');
subplot(2,1,1);
stairs(healthy.cycle(1:18),healthy.applied.sourceTokenIndex(1:18), ...
    'LineWidth',1.3,'DisplayName','healthy held offer');
hold on;
stairs(broken.cycle(1:18),broken.applied.sourceTokenIndex(1:18), ...
    '--','LineWidth',1.3,'DisplayName','broken advancing offer');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Source payload identity [token index from one]');
title('Broken symptom: payload changes while FIFO ready is low');
legend('Location','best');
xlim([1 18]);
drawnow;

%% Broken view 2 - reveal the consumer-visible sequence gap
figure(brokenFigure);
subplot(2,1,2);
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
title('Ignoring ready jumps from token 6 to token 10');
legend('Location','best');
fprintf(['Broken drops at cycles [7 8 9], lost tokens [7 8 9], ' ...
    'hold violations=%d, delivered=%d.\n'], ...
    broken.applied.sourceHoldViolationCount, ...
    broken.applied.dequeuedTokenCount);
drawnow;

%% Explore, check, and teach back
% Run experiment.m one section at a time for both complete sweeps and the
% exact broken symptom. Then use the bounded UI, run run_checks, answer
% checks.md one prompt at a time, and give the two-sentence teach-back
% without explaining MATLAB syntax.
interactive;
