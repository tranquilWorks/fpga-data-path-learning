%% P04 - Control Behavior with a Finite-State Machine
% Run one section at a time. Every sweep resets to a named baseline and
% changes only one event-timing parameter.
figureNames = {'P04 baseline FSM','P04 completion-delay sweep', ...
    'P04 timeout-limit sweep','P04 broken priority'};
for figureIndex = 1:numel(figureNames)
    delete(findall(groot,'Type','figure','Name',figureNames{figureIndex}));
end
clear model;
clc;

%% Baseline - a command completes before its deadline
% Inputs are sampled immediately before each rising edge. State and Moore
% outputs are observed immediately after it. Reset acts at cycle 1, start
% at cycle 2, workDone three cycles later, and the deadline five cycles
% later. The controller waits, emits a one-cycle DONE state, then recovers.
baseline = model(3,5,5,false);
fprintf(['Baseline: completion delay %d cycles, timeout limit %d cycles, ' ...
    'terminal state %s at cycle %d, WAIT dwell %d cycles.\n'], ...
    baseline.completionDelay,baseline.timeoutLimit, ...
    baseline.terminalStateName,baseline.terminalCycle, ...
    baseline.busyCycleCount);
fprintf(['Selected cycle %d: %s -> %s because %s; busy=%d, done=%d, ' ...
    'timeout=%d.\n'],baseline.selectedCycle,baseline.selectedStateBefore, ...
    baseline.selectedStateAfter,baseline.selectedTransitionReason, ...
    baseline.selectedBusy,baseline.selectedDone,baseline.selectedTimeout);

figure('Name',figureNames{1});
subplot(2,1,1);
stairs(baseline.cycle,baseline.stateAfter,'-o','LineWidth',1.35, ...
    'DisplayName','State after edge');
grid on;
xlabel('Clock cycle [cycles]');
ylabel('State code [unitless]');
title('Baseline: registered state advances from IDLE to WAIT to DONE');
xlim([1 baseline.cycleCount]);
ylim([-0.25 3.25]);
yticks(baseline.stateCodes);
yticklabels(baseline.stateLabels);
legend('Location','best');

subplot(2,1,2);
baselineSignalLabels = {'reset','start','work done','deadline expired', ...
    'busy','done','timeout'};
baselineSignals = double([baseline.reset baseline.start baseline.workDone ...
    baseline.deadlineExpired baseline.busy baseline.donePulse ...
    baseline.timeoutPulse]);
baselineOffsets = 2*(0:numel(baselineSignalLabels)-1);
baselineSignalRows = baselineSignals + ...
    repmat(baselineOffsets,baseline.cycleCount,1);
stairs(baseline.cycle,baselineSignalRows,'LineWidth',1.15);
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Signal level [binary] (vertically offset)');
title('Pre-edge inputs and post-edge Moore outputs on labeled rows');
xlim([1 baseline.cycleCount]);
ylim([-0.25 baselineOffsets(end)+1.25]);
yticks(baselineOffsets);
yticklabels(baselineSignalLabels);

%% Sweep 1 - change only completion delay
% Hold the timeout limit at eight cycles. A later completion keeps the FSM
% in WAIT longer, so both busy duration and terminal cycle move together.
completionDelays = 1:6;
completionBusyCounts = zeros(size(completionDelays));
completionTerminalCycles = zeros(size(completionDelays));
completionOutcomes = zeros(size(completionDelays));
fixedDeadlineReference = model(1,8,5,false);
fixedDeadline = fixedDeadlineReference.deadlineExpired;
fprintf('\nSweep 1 - completion delay (timeout limit fixed at 8 cycles):\n');
for sweepIndex = 1:numel(completionDelays)
    current = model(completionDelays(sweepIndex),8,5,false);
    completionBusyCounts(sweepIndex) = current.busyCycleCount;
    completionTerminalCycles(sweepIndex) = current.terminalCycle;
    completionOutcomes(sweepIndex) = current.completionCount;
    assert(current.timeoutLimit == 8 && ...
        isequal(current.deadlineExpired,fixedDeadline), ...
        'Completion-delay sweep must not move the deadline.');
    fprintf('  delay %d cycles -> %s at cycle %d, busy for %d cycles\n', ...
        current.completionDelay,current.terminalStateName, ...
        current.terminalCycle,current.busyCycleCount);
end

figure('Name',figureNames{2});
subplot(2,1,1);
plot(completionDelays,completionBusyCounts,'-o','LineWidth',1.35, ...
    'DisplayName','WAIT / busy duration');
hold on;
plot(completionDelays,completionTerminalCycles,'--s','LineWidth',1.35, ...
    'DisplayName','Terminal cycle');
hold off;
grid on;
xlabel('Completion delay [cycles after start]');
ylabel('Duration or edge index [cycles]');
title('Sweep 1: later completion extends the WAIT residence');
xticks(completionDelays);
legend('Location','best');

subplot(2,1,2);
bar(completionDelays,completionOutcomes);
grid on;
xlabel('Completion delay [cycles after start]');
ylabel('DONE pulse count [pulses]');
title('Timeout fixed at 8 cycles: every swept completion succeeds');
xticks(completionDelays);
ylim([0 1.2]);

%% Sweep 2 - reset, then change only timeout limit
% Return completion delay to four cycles. Timeout limits below four expire
% first; a limit of four succeeds because the declared policy accepts a
% completion that arrives exactly on the deadline.
timeoutLimits = 1:8;
timeoutBusyCounts = zeros(size(timeoutLimits));
timeoutTerminalCycles = zeros(size(timeoutLimits));
timeoutOutcomes = zeros(numel(timeoutLimits),2);
fixedCompletionReference = model(4,1,6,false);
fixedCompletion = fixedCompletionReference.workDone;
fprintf('\nSweep 2 - timeout limit (completion delay fixed at 4 cycles):\n');
for sweepIndex = 1:numel(timeoutLimits)
    current = model(4,timeoutLimits(sweepIndex),6,false);
    timeoutBusyCounts(sweepIndex) = current.busyCycleCount;
    timeoutTerminalCycles(sweepIndex) = current.terminalCycle;
    timeoutOutcomes(sweepIndex,:) = ...
        [current.completionCount current.timeoutCount];
    assert(current.completionDelay == 4 && ...
        isequal(current.workDone,fixedCompletion), ...
        'Timeout sweep must not move the completion input.');
    fprintf('  limit %d cycles -> %s at cycle %d, busy for %d cycles\n', ...
        current.timeoutLimit,current.terminalStateName, ...
        current.terminalCycle,current.busyCycleCount);
end

figure('Name',figureNames{3});
subplot(2,1,1);
plot(timeoutLimits,timeoutBusyCounts,'-o','LineWidth',1.35, ...
    'DisplayName','WAIT / busy duration');
hold on;
plot(timeoutLimits,timeoutTerminalCycles,'--s','LineWidth',1.35, ...
    'DisplayName','Terminal cycle');
hold off;
grid on;
xlabel('Timeout limit [cycles after start]');
ylabel('Duration or edge index [cycles]');
title('Sweep 2: the earlier event ends WAIT');
xticks(timeoutLimits);
legend('Location','best');

subplot(2,1,2);
bar(timeoutLimits,timeoutOutcomes,'stacked');
grid on;
xlabel('Timeout limit [cycles after start]');
ylabel('Terminal pulse count [pulses]');
title('Inclusive boundary: limit 4 changes TIMEOUT to DONE');
xticks(timeoutLimits);
ylim([0 1.2]);
legend('done','timeout','Location','best');

%% Deliberately broken case - timeout incorrectly wins a tie
% Named violated assumption: the controller specification declares that a
% completion sampled on the deadline succeeds. The broken transition table
% checks deadlineExpired before workDone. With both HIGH at cycle 6 it
% reports TIMEOUT instead of DONE, then safely recovers to IDLE at cycle 7.
healthyTie = model(4,4,6,false);
broken = model(4,4,6,true);
figure('Name',figureNames{4});
subplot(2,1,1);
stairs(healthyTie.cycle,healthyTie.stateAfter,'-o','LineWidth',1.35, ...
    'DisplayName','Declared completion-first policy');
hold on;
stairs(broken.cycle,broken.stateAfter,'--s','LineWidth',1.35, ...
    'DisplayName','Broken timeout-first priority');
scatter(broken.mismatchCycles,broken.stateAfter(broken.mismatchMask), ...
    75,'r','filled','DisplayName','Wrong terminal state');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('State code [unitless]');
title('Broken case: transition priority changes the boundary outcome');
xlim([1 broken.cycleCount]);
ylim([-0.25 3.25]);
yticks(broken.stateCodes);
yticklabels(broken.stateLabels);
legend('Location','best');

subplot(2,1,2);
brokenSignalLabels = {'reset','work done','deadline expired','done','timeout'};
brokenSignals = double([broken.reset broken.workDone ...
    broken.deadlineExpired broken.donePulse broken.timeoutPulse]);
brokenOffsets = 2*(0:numel(brokenSignalLabels)-1);
brokenSignalRows = brokenSignals + ...
    repmat(brokenOffsets,broken.cycleCount,1);
stairs(broken.cycle,brokenSignalRows,'LineWidth',1.2);
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Signal level [binary] (vertically offset)');
title('At cycle 6 the labeled input rows expose the wrong output pulse');
xlim([1 broken.cycleCount]);
ylim([-0.25 brokenOffsets(end)+1.25]);
yticks(brokenOffsets);
yticklabels(brokenSignalLabels);
fprintf(['\nBroken case: %d mismatch at cycle %d; wrong timeout pulses=%d. ' ...
    'Both traces recover to IDLE on cycle 7.\n'],broken.mismatchCount, ...
    broken.mismatchCycles,broken.wrongTimeoutCount);

%% Deterministic experiment guards
assert(isequal(baseline.stateAfter,[0 1 1 1 2 zeros(1,11)].'), ...
    'The baseline FSM trace changed.');
assert(isequal(completionBusyCounts,1:6) && ...
    isequal(completionTerminalCycles,3:8) && ...
    all(completionOutcomes == 1), ...
    'Completion-delay sweep limits changed.');
assert(isequal(timeoutBusyCounts,[1 2 3 4 4 4 4 4]) && ...
    isequal(timeoutTerminalCycles,[3 4 5 6 6 6 6 6]) && ...
    isequal(timeoutOutcomes(:,2).',[1 1 1 0 0 0 0 0]), ...
    'Timeout-limit sweep or inclusive boundary changed.');
assert(healthyTie.donePulse(6) && broken.timeoutPulse(6) && ...
    isequal(broken.mismatchCycles,6) && broken.wrongTimeoutCount == 1, ...
    'Broken priority symptom changed.');
