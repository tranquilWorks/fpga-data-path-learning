%% P04 - Control Behavior with a Finite-State Machine
% Guiding question:
% What inputs, observable effects, and failure modes matter when you control Behavior with a Finite-State Machine?
clear model interactive;

%% Read - turn P03 stored state into controlled behavior
% P03 showed that a register remembers a value from one edge to the next.
% An FSM gives that register named meanings such as IDLE and WAIT. A
% P02-style combinational decision uses current state plus sampled inputs to
% choose next state; the state register remembers that choice after the edge.
disp(['Mental model: inputs and current state enter the transition rule ' ...
    'before an edge; registered next state and Moore outputs appear after it.']);
disp('Prediction: with completion delay 3 and timeout 5, what state and output follow edge 5?');

%% Visualize the deterministic baseline
baseline = model(3,5,5,false);
delete(findall(groot,'Type','figure','Name','P04 lesson baseline'));
figure('Name','P04 lesson baseline');
subplot(2,1,1);
stairs(baseline.cycle,baseline.stateAfter,'-o','LineWidth',1.35);
grid on;
xlabel('Clock cycle [cycles]');
ylabel('State code [unitless]');
title('Baseline: IDLE to WAIT to one-cycle DONE to IDLE');
xlim([1 baseline.cycleCount]);
ylim([-0.25 3.25]);
yticks(baseline.stateCodes);
yticklabels(baseline.stateLabels);
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
title('Inputs before each edge and decoded outputs on labeled rows');
xlim([1 baseline.cycleCount]);
ylim([-0.25 baselineOffsets(end)+1.25]);
yticks(baselineOffsets);
yticklabels(baselineSignalLabels);
fprintf('Cycle 5 samples workDone=1 in WAIT and produces state %s, done=%d.\n', ...
    baseline.selectedStateAfter,baseline.selectedDone);

%% Read the baseline mechanism
% The state recurrence is stateAfter[n] = delta(stateBefore[n],inputs[n]).
% Moore outputs decode only registered post-edge state: busy means WAIT,
% done means DONE, and timeout means TIMEOUT. DONE returns to IDLE after one
% edge, so a late deadline is ignored rather than creating a second result.
disp(baseline.equationText);

%% Move lever 1 - delay completion while the deadline stays fixed
% Reset timeout to 8 cycles and establish completion delay 3 as this sweep's
% reference. Then change only completion delay to 6 cycles. The outcome
% still succeeds, but WAIT and busy last three cycles longer.
slowCompletion = model(6,8,8,false);
fastCompletion = model(3,8,5,false);
delete(findall(groot,'Type','figure','Name','P04 lesson completion change'));
figure('Name','P04 lesson completion change');
stairs(fastCompletion.cycle,fastCompletion.stateAfter,'-o', ...
    'LineWidth',1.35,'DisplayName','delay 3 cycles');
hold on;
stairs(slowCompletion.cycle,slowCompletion.stateAfter,'--s', ...
    'LineWidth',1.35,'DisplayName','delay 6 cycles');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('State code [unitless]');
title('Changed view: later completion extends WAIT');
xlim([1 fastCompletion.cycleCount]);
ylim([-0.25 3.25]);
yticks(fastCompletion.stateCodes);
yticklabels(fastCompletion.stateLabels);
legend('Location','best');

%% Explain lever 1, reset, then move lever 2
% Mechanism first: only the workDone input moved, so the WAIT transition
% moved with it. Reset to completion delay 4, then change only timeout from
% 5 to 2 cycles. The earlier deadline now sends WAIT to TIMEOUT at cycle 4.
successfulLimit = model(4,5,6,false);
shortLimit = model(4,2,4,false);
delete(findall(groot,'Type','figure','Name','P04 lesson timeout change'));
figure('Name','P04 lesson timeout change');
stairs(successfulLimit.cycle,successfulLimit.stateAfter,'-o', ...
    'LineWidth',1.35,'DisplayName','timeout 5 cycles');
hold on;
stairs(shortLimit.cycle,shortLimit.stateAfter,'--s', ...
    'LineWidth',1.35,'DisplayName','timeout 2 cycles');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('State code [unitless]');
title('Changed view: an earlier deadline selects TIMEOUT');
xlim([1 successfulLimit.cycleCount]);
ylim([-0.25 3.25]);
yticks(successfulLimit.stateCodes);
yticklabels(successfulLimit.stateLabels);
legend('Location','best');

%% Explain lever 2, then break transition priority
% Mechanism first: the state can react only while it is WAIT. At equal
% completion and timeout delays, both inputs are HIGH at cycle 6. The
% declared policy accepts on-time completion. The broken table checks the
% deadline first and emits the wrong TIMEOUT pulse instead of DONE.
healthyTie = model(4,4,6,false);
brokenTie = model(4,4,6,true);
fprintf(['Tie at cycle 6: healthy=%s, broken=%s, mismatches=%d; ' ...
    'both recover to IDLE at cycle 7.\n'], ...
    healthyTie.selectedStateAfter,brokenTie.selectedStateAfter, ...
    brokenTie.mismatchCount);

%% Explore, check, and teach back
% Run experiment.m one section at a time for both independent sweeps and
% the broken comparison. Then use the bounded UI, run run_checks, and give
% the two-sentence teach-back in checks.md without explaining MATLAB syntax.
interactive;
