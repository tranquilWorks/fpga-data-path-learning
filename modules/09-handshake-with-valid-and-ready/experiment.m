%% P09 - Handshake with Valid and Ready
% Run one section at a time. Signals are observed immediately before each
% rising edge. A token transfers only when valid and ready are both high at
% that edge. Each sweep resets the other lever so source supply and consumer
% availability remain independent.
figureNames = {'P09 baseline handshake', ...
    'P09 source-gap sweep','P09 ready-stall sweep', ...
    'P09 broken advance without ready'};
for figureIndex = 1:numel(figureNames)
    delete(findall(groot,'Type','figure','Name',figureNames{figureIndex}));
end
clear model;
clc;

%% Read the transfer and hold rules, then establish the baseline
% Before plotting, predict whether token 822 transfers at cycle 5 when
% valid is high and ready is low. Inspect the baseline once. Make no second
% prediction; later sections ask for observations and mechanisms.
baseline = model(1,3,false);
expectedTransferCycles = [1 3 8 10 12 14 16 18].';
assert(isequal(find(baseline.applied.transfer),expectedTransferCycles) && ...
    isequal(baseline.applied.acceptedDataCodes,baseline.tokenCodes) && ...
    baseline.applied.completed && baseline.applied.completionCycle == 18, ...
    'P09:BaselineTransfers', ...
    'The baseline must accept all eight ordered tokens on the named edges.');
assert(all(baseline.applied.valid(5:8)) && ...
    all(~baseline.ready(5:7)) && baseline.ready(8) && ...
    all(baseline.applied.dataCode(5:8) == 822) && ...
    baseline.applied.maximumWaitCycles == 3 && ...
    baseline.applied.holdViolationCount == 0, ...
    'P09:BaselineHold', ...
    'Token 822 must remain valid and stable until ready returns.');
fprintf(['Baseline: transfers at cycles [%s], completion=%d cycles, ' ...
    'active transfers/stalls/source bubbles=%d/%d/%d, rate=%0.6g ' ...
    'transfers/cycle through completion.\n'], ...
    sprintf('%d ',expectedTransferCycles),baseline.applied.completionCycle, ...
    baseline.applied.activeTransferCount, ...
    baseline.applied.activeStallCycleCount, ...
    baseline.applied.activeSourceBubbleCycleCount, ...
    baseline.applied.activeWindowTransferRate);
fprintf('%s; %s.\n',baseline.equationText,baseline.holdRuleText);

%% Baseline view 1 - valid, ready, and transfer
baselineFigure = figure('Name',figureNames{1},'NumberTitle','off');
visibleCycles = 1:20;
subplot(2,2,1);
stairs(baseline.cycle(visibleCycles), ...
    double(baseline.applied.valid(visibleCycles)),'LineWidth',1.3, ...
    'DisplayName','valid');
hold on;
stairs(baseline.cycle(visibleCycles), ...
    2+double(baseline.ready(visibleCycles)),'LineWidth',1.3, ...
    'DisplayName','ready');
stairs(baseline.cycle(visibleCycles), ...
    4+double(baseline.applied.transfer(visibleCycles)),'LineWidth',1.3, ...
    'DisplayName','transfer');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Handshake signals [binary, vertically offset]');
title('Transfer occurs only where valid and ready overlap');
set(gca,'YTick',[0.5 2.5 4.5], ...
    'YTickLabel',{'valid','ready','transfer'});
ylim([-0.2 5.2]);
xlim([1 20]);
drawnow;

%% Baseline view 2 - held and accepted payload
figure(baselineFigure);
subplot(2,2,2);
stairs(baseline.cycle(visibleCycles), ...
    baseline.applied.dataCode(visibleCycles),'LineWidth',1.3, ...
    'DisplayName','Offered payload');
hold on;
transferMask = baseline.applied.transfer(visibleCycles);
scatter(baseline.cycle(visibleCycles(transferMask)), ...
    baseline.applied.acceptedDataCodeByCycle(visibleCycles(transferMask)), ...
    42,'filled','DisplayName','Accepted at edge');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Payload [unsigned 12-bit phase code]');
title('Token 822 is held from cycle 5 through cycle 8');
legend('Location','best');
xlim([1 20]);
drawnow;

%% Baseline view 3 - cumulative accepted-token count
figure(baselineFigure);
subplot(2,2,3);
stairs(baseline.cycle(visibleCycles), ...
    cumsum(double(baseline.applied.transfer(visibleCycles))), ...
    'LineWidth',1.3);
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Accepted payloads [tokens]');
title('Stalled cycles do not increment the consumer count');
xlim([1 20]);
ylim([0 baseline.tokenCount]);
drawnow;

%% Baseline view 4 - wait per token
figure(baselineFigure);
subplot(2,2,4);
bar(baseline.tokenOrdinal,baseline.applied.waitCycles);
grid on;
xlabel('Payload ordinal [token index from zero]');
ylabel('Offer-to-transfer wait [cycles]');
title('Only the token present during the stall waits');
sgtitle('P09 baseline: one source gap and a three-cycle ready stall');
drawnow;

%% Sweep 1 - source gap with the consumer always ready
% Lever 1 changes only the idle cycles between accepted tokens. Readiness,
% payload identity, order, transfer rule, and fixed record stay unchanged.
sourceGapSweep = 0:3;
gapCompletionCycles = zeros(size(sourceGapSweep));
gapSourceBubbleCycles = zeros(size(sourceGapSweep));
gapTransferRates = zeros(size(sourceGapSweep));
gapAcceptedCounts = zeros(size(sourceGapSweep));
for sweepIndex = 1:numel(sourceGapSweep)
    current = model(sourceGapSweep(sweepIndex),0,false);
    assert(all(current.ready) && current.readyStallCycles == 0 && ...
        isequal(current.tokenCodes,baseline.tokenCodes) && ...
        isequal(current.applied.acceptedDataCodes,current.tokenCodes) && ...
        current.applied.holdViolationCount == 0 && ...
        current.applied.lostTokenCount == 0, ...
        'P09:SourceGapSweepIsolation', ...
        ['Source-gap sweep must preserve always-ready service, payloads, ' ...
        'order, and protocol correctness.']);
    gapCompletionCycles(sweepIndex) = current.applied.completionCycle;
    gapSourceBubbleCycles(sweepIndex) = ...
        current.applied.activeSourceBubbleCycleCount;
    gapTransferRates(sweepIndex) = ...
        current.applied.activeWindowTransferRate;
    gapAcceptedCounts(sweepIndex) = current.applied.acceptedTokenCount;
end
assert(isequal(gapCompletionCycles,[8 15 22 29]) && ...
    isequal(gapSourceBubbleCycles,[0 7 14 21]) && ...
    max(abs(gapTransferRates-8./gapCompletionCycles)) < 1e-12 && ...
    all(gapAcceptedCounts == 8), ...
    'P09:SourceGapSweep', ...
    'Seven between-token gaps must move completion by seven cycles each.');

gapFigure = figure('Name',figureNames{2},'NumberTitle','off');
subplot(2,2,1);
plot(sourceGapSweep,gapCompletionCycles,'-o','LineWidth',1.3);
grid on;
xlabel('Source gap after transfer [cycles]');
ylabel('Final transfer edge [clock cycle]');
title('Seven between-token gaps move completion');
drawnow;

%% Sweep 1 view 2 - source bubbles
figure(gapFigure);
subplot(2,2,2);
plot(sourceGapSweep,gapSourceBubbleCycles,'-o','LineWidth',1.3);
grid on;
xlabel('Source gap after transfer [cycles]');
ylabel('Source bubbles before completion [cycles]');
title('Bubble count is 7 times the gap');
drawnow;

%% Sweep 1 view 3 - completion-window transfer rate
figure(gapFigure);
subplot(2,2,3);
plot(sourceGapSweep,gapTransferRates,'-o','LineWidth',1.3);
grid on;
xlabel('Source gap after transfer [cycles]');
ylabel('Completion-window rate [transfers/cycle]');
title('Ready cannot accept an absent offer');
drawnow;

%% Sweep 1 view 4 - accepted count remains fixed
figure(gapFigure);
subplot(2,2,4);
bar(sourceGapSweep,gapAcceptedCounts);
grid on;
xlabel('Source gap after transfer [cycles]');
ylabel('Accepted payloads [tokens]');
title('Spacing changes; the eight-token sequence does not');
ylim([0 baseline.tokenCount+1]);
sgtitle('Sweep 1: move source spacing while ready stays high');
drawnow;

%% Read the first changed-view mechanism
% A source gap is a cycle with no valid payload. Each of the seven gaps
% between eight tokens occurs g times, so completion is 8+7*g. Ready stays
% high but cannot create transfers in bubbles. Numeric payloads and order
% remain unchanged.

%% Sweep 2 - ready stall with a continuously valid source
% Reset the source gap to zero. Lever 2 changes only the fixed ready-low
% run beginning at cycle 5. The producer must hold the pending token.
readyStallSweep = 0:6;
stallCompletionCycles = zeros(size(readyStallSweep));
stallCycleCounts = zeros(size(readyStallSweep));
stallMaximumWaitCycles = zeros(size(readyStallSweep));
stallTransferRates = zeros(size(readyStallSweep));
for sweepIndex = 1:numel(readyStallSweep)
    current = model(0,readyStallSweep(sweepIndex),false);
    expectedReady = true(current.recordCycleCount,1);
    if readyStallSweep(sweepIndex) > 0
        expectedReady(5:4+readyStallSweep(sweepIndex)) = false;
    end
    assert(current.sourceGapCycles == 0 && ...
        isequal(current.ready,expectedReady) && ...
        isequal(current.applied.acceptedDataCodes,current.tokenCodes) && ...
        current.applied.activeSourceBubbleCycleCount == 0 && ...
        current.applied.holdViolationCount == 0 && ...
        current.applied.lostTokenCount == 0, ...
        'P09:ReadyStallSweepIsolation', ...
        ['Ready-stall sweep must preserve continuous valid supply, ' ...
        'payloads, order, and hold behavior.']);
    stallCompletionCycles(sweepIndex) = current.applied.completionCycle;
    stallCycleCounts(sweepIndex) = current.applied.activeStallCycleCount;
    stallMaximumWaitCycles(sweepIndex) = current.applied.maximumWaitCycles;
    stallTransferRates(sweepIndex) = ...
        current.applied.activeWindowTransferRate;
end
assert(isequal(stallCompletionCycles,8+readyStallSweep) && ...
    isequal(stallCycleCounts,readyStallSweep) && ...
    isequal(stallMaximumWaitCycles,readyStallSweep) && ...
    max(abs(stallTransferRates-8./stallCompletionCycles)) < 1e-12, ...
    'P09:ReadyStallSweep', ...
    'Each ready-low cycle must add one stalled cycle and completion cycle.');

stallFigure = figure('Name',figureNames{3},'NumberTitle','off');
subplot(2,2,1);
plot(readyStallSweep,stallCompletionCycles,'-o','LineWidth',1.3);
grid on;
xlabel('Ready-low duration [cycles]');
ylabel('Final transfer edge [clock cycle]');
title('Completion moves one-for-one with the stall');
drawnow;

%% Sweep 2 view 2 - stalled-valid cycles
figure(stallFigure);
subplot(2,2,2);
plot(readyStallSweep,stallCycleCounts,'-o','LineWidth',1.3);
grid on;
xlabel('Ready-low duration [cycles]');
ylabel('Valid-without-ready [cycles]');
title('The pending payload remains offered');
drawnow;

%% Sweep 2 view 3 - maximum token wait
figure(stallFigure);
subplot(2,2,3);
plot(readyStallSweep,stallMaximumWaitCycles,'-o','LineWidth',1.3);
grid on;
xlabel('Ready-low duration [cycles]');
ylabel('Maximum offer-to-transfer wait [cycles]');
title('Maximum wait equals the complete ready stall');
drawnow;

%% Sweep 2 view 4 - completion-window transfer rate
figure(stallFigure);
subplot(2,2,4);
plot(readyStallSweep,stallTransferRates,'-o','LineWidth',1.3);
grid on;
xlabel('Ready-low duration [cycles]');
ylabel('Completion-window rate [transfers/cycle]');
title('Consumer availability limits completion rate');
sgtitle('Sweep 2: move ready while the source stays continuously valid');
drawnow;

%% Read the second changed-view mechanism
% While ready is low, valid remains high with one stable payload, but the
% AND transfer gate stays low. Each extra stall cycle delays the held token
% and all later tokens once. Returning ready accepts exactly that held token.

%% Deliberately broken case - advance producer state without ready
% With no source gaps and ready low on cycles 5 through 7, the broken source
% treats each offer as consumed. No transfer occurred, so tokens 5, 6, and
% 7 disappear before the consumer can observe them on an accepting edge.
healthy = model(0,3,false);
broken = model(0,3,true);
assert(isequal(healthy.reference.acceptedTokenIndices,(1:8).') && ...
    isequal(find(healthy.reference.transfer),[1 2 3 4 8 9 10 11].') && ...
    healthy.reference.holdViolationCount == 0, ...
    'P09:BrokenReference', ...
    'The healthy reference must retain and accept all eight tokens.');
assert(isequal(broken.applied.acceptedTokenIndices,[1 2 3 4 8].') && ...
    isequal(find(broken.applied.dropEvent),[5 6 7].') && ...
    isequal(find(broken.applied.holdViolation),[6 7 8].') && ...
    broken.applied.lostTokenCount == 3 && broken.faultActive && ...
    ~broken.applied.completed, ...
    'P09:BrokenLoss', ...
    'Advancing without ready must drop exactly three named payload tokens.');

brokenFigure = figure('Name',figureNames{4},'NumberTitle','off');
subplot(2,2,1);
stairs(broken.cycle(1:14),double(broken.ready(1:14)), ...
    'LineWidth',1.3,'DisplayName','ready');
hold on;
stairs(broken.cycle(1:14), ...
    2+double(broken.reference.transfer(1:14)),'LineWidth',1.3, ...
    'DisplayName','healthy transfer');
stairs(broken.cycle(1:14), ...
    4+double(broken.applied.transfer(1:14)),'--','LineWidth',1.3, ...
    'DisplayName','broken transfer');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Ready and transfer [binary, vertically offset]');
title('Broken producer mistakes stalled offers for transfers');
set(gca,'YTick',[0.5 2.5 4.5], ...
    'YTickLabel',{'ready','healthy transfer','broken transfer'});
ylim([-0.2 5.2]);
xlim([1 14]);
drawnow;

%% Broken view 2 - payload changes through the stall
figure(brokenFigure);
subplot(2,2,2);
stairs(broken.cycle(1:14),broken.reference.dataCode(1:14), ...
    'LineWidth',1.3,'DisplayName','Healthy held payload');
hold on;
stairs(broken.cycle(1:14),broken.applied.dataCode(1:14),'--', ...
    'LineWidth',1.3,'DisplayName','Broken advancing payload');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Payload [unsigned 12-bit phase code]');
title('Data changes even though ready is low');
legend('Location','best');
xlim([1 14]);
drawnow;

%% Broken view 3 - accepted sequences
figure(brokenFigure);
subplot(2,2,3);
plot(1:numel(broken.reference.acceptedDataCodes), ...
    broken.reference.acceptedDataCodes,'-o','LineWidth',1.3, ...
    'DisplayName','Healthy');
hold on;
plot(1:numel(broken.applied.acceptedDataCodes), ...
    broken.applied.acceptedDataCodes,'--x','LineWidth',1.3, ...
    'DisplayName','Broken');
hold off;
grid on;
xlabel('Consumer transfer ordinal [token index from one]');
ylabel('Accepted payload [unsigned 12-bit phase code]');
title('Three missing middle tokens create a sequence jump');
legend('Location','best');
drawnow;

%% Broken view 4 - exact fault events
figure(brokenFigure);
subplot(2,2,4);
stem(broken.cycle(1:14),double(broken.applied.dropEvent(1:14)), ...
    'filled','LineWidth',1.1,'DisplayName','Dropped locally');
hold on;
stem(broken.cycle(1:14), ...
    2+double(broken.applied.holdViolation(1:14)), ...
    'LineWidth',1.1,'DisplayName','Hold violation');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Fault indicators [binary, vertically offset]');
title('Drops at 5-7 cause next-cycle violations at 6-8');
set(gca,'YTick',[0.5 2.5], ...
    'YTickLabel',{'drop','hold violation'});
ylim([-0.2 3.2]);
xlim([1 14]);
sgtitle('Deliberately broken case: producer advances without a handshake');
drawnow;

%% Mechanism-first explanation, limits, and next step
% Healthy producer state advances only on valid && ready. Broken state
% advances on valid alone, so it discards one token per stalled offer and
% changes data while the old offer is still owed. The fault is inert when
% no valid-without-ready edge occurs. The maximum healthy source-gap/stall
% combination completes on fixed record cycle 35. Now run run_checks.m and
% answer checks.md one prompt at a time before giving the teach-back.
