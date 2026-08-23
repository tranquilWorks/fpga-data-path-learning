%% P03 - Store State with Registers
% Run one section at a time. Every sweep resets to a named baseline and
% changes only one register property.
figureNames = {'P03 baseline register','P03 depth sweep', ...
    'P03 enable sweep','P03 broken cascade'};
for figureIndex = 1:numel(figureNames)
    delete(findall(groot,'Type','figure','Name',figureNames{figureIndex}));
end
clear model;
clc;

%% Baseline - one 4-bit register captures on every enabled edge
% Values are inputs immediately before each rising edge and register state
% immediately after that edge. Reset is asserted on cycle 1 and wins over
% enable. Beginning at cycle 2, enable is HIGH on every edge.
baseline = model(1,1,6,false);
fprintf(['Baseline: %d stage, enable every %d cycle, %d captured samples, ' ...
    '%d held edges.\n'],baseline.stageCount,baseline.enablePeriod, ...
    baseline.captureCount,baseline.holdCount);
fprintf(['At cycle %d: action=%s, D=%d, Q before=%d, Q after=%d, ' ...
    'valid=%d.\n'],baseline.selectedCycle,baseline.selectedAction, ...
    baseline.selectedInput,baseline.selectedStateBefore, ...
    baseline.selectedStateAfter,baseline.selectedOutputValid);

figure('Name',figureNames{1});
subplot(2,1,1);
baselinePlotOutput = baseline.output;
baselinePlotOutput(~baseline.outputValid) = NaN;
stairs(baseline.cycle,baseline.inputData,'-o','LineWidth',1.3, ...
    'DisplayName','Input D before edge');
hold on;
stairs(baseline.cycle,baselinePlotOutput,'--s','LineWidth',1.3, ...
    'DisplayName','Register Q after edge');
scatter(baseline.cycle(~baseline.outputValid), ...
    baseline.output(~baseline.outputValid),75,[0.35 0.35 0.35],'x', ...
    'LineWidth',1.6,'DisplayName','Reset fill (invalid)');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Unsigned 4-bit code [0..15]');
title('Baseline: enabled edge captures D; reset loads zero');
xlim([1 baseline.cycleCount]);
ylim([0 15]);
legend('Location','best');

subplot(2,1,2);
stairs(baseline.cycle,double([baseline.reset baseline.captureEnable ...
    baseline.outputValid]),'LineWidth',1.2);
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Control level [binary]');
title('Reset, clock enable, and output-valid state');
yticks([0 1]);
ylim([-0.1 1.1]);
legend('reset','enable','output valid','Location','best');

%% Sweep 1 - change only register depth
% Enable remains HIGH after reset. Each additional stage adds one more
% active-edge delay between capture by Q1 and appearance at the last stage.
stageCounts = 1:4;
depthOutputs = zeros(baseline.cycleCount,numel(stageCounts));
depthPlotOutputs = NaN(baseline.cycleCount,numel(stageCounts));
firstValidCycles = zeros(size(stageCounts));
additionalDelays = zeros(size(stageCounts));
fprintf('\nSweep 1 - register depth (enable period fixed at 1):\n');
for sweepIndex = 1:numel(stageCounts)
    current = model(stageCounts(sweepIndex),1,6,false);
    depthOutputs(:,sweepIndex) = current.output;
    depthPlotOutputs(current.outputValid,sweepIndex) = ...
        current.output(current.outputValid);
    firstValidCycles(sweepIndex) = current.firstValidCycle;
    additionalDelays(sweepIndex) = current.additionalActiveEdgeDelay;
    assert(isequal(current.captureEnable,baseline.captureEnable), ...
        'Depth sweep must not change the enable schedule.');
    fprintf('  %d stage(s) -> first valid cycle %d, %d additional active-edge delay(s)\n', ...
        current.stageCount,current.firstValidCycle, ...
        current.additionalActiveEdgeDelay);
end

figure('Name',figureNames{2});
stairs(baseline.cycle,depthPlotOutputs,'-o','LineWidth',1.2);
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Last-stage code [0..15]');
title('Sweep 1: more registers delay the same accepted sequence');
xlim([1 baseline.cycleCount]);
ylim([0 15]);
depthLabels = arrayfun(@(count) sprintf('%d stage(s)',count), ...
    stageCounts,'UniformOutput',false);
legend(depthLabels,'Location','best');

%% Sweep 2 - change only the clock-enable period
% Return to one stage. A larger period creates more disabled edges, so Q
% holds its previous value longer and fewer input samples are captured.
enablePeriods = 1:4;
enableOutputs = zeros(baseline.cycleCount,numel(enablePeriods));
enablePlotOutputs = NaN(baseline.cycleCount,numel(enablePeriods));
captureCounts = zeros(size(enablePeriods));
holdCounts = zeros(size(enablePeriods));
fprintf('\nSweep 2 - enable period (register depth fixed at 1):\n');
for sweepIndex = 1:numel(enablePeriods)
    current = model(1,enablePeriods(sweepIndex),6,false);
    enableOutputs(:,sweepIndex) = current.output;
    enablePlotOutputs(current.outputValid,sweepIndex) = ...
        current.output(current.outputValid);
    captureCounts(sweepIndex) = current.captureCount;
    holdCounts(sweepIndex) = current.holdCount;
    assert(current.stageCount == 1, ...
        'Enable sweep must keep register depth at one.');
    fprintf('  period %d -> %d captured samples, %d held edges\n', ...
        current.enablePeriod,current.captureCount,current.holdCount);
end

figure('Name',figureNames{3});
subplot(2,1,1);
stairs(baseline.cycle,enablePlotOutputs,'LineWidth',1.2);
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Register code Q [0..15]');
title('Sweep 2: disabled edges preserve the previous state');
xlim([1 baseline.cycleCount]);
ylim([0 15]);
enableLabels = arrayfun(@(period) sprintf('period %d',period), ...
    enablePeriods,'UniformOutput',false);
legend(enableLabels,'Location','best');

subplot(2,1,2);
bar(enablePeriods,[captureCounts(:) holdCounts(:)]);
grid on;
xlabel('Enable period [cycles]');
ylabel('Edge count [edges]');
title('Captured versus held non-reset edges');
xticks(enablePeriods);
legend('captured','held','Location','best');

%% Deliberately broken case - cascade new values through three stages
% Named violated assumption: all edge-triggered registers sample their
% pre-edge inputs simultaneously. The broken calculation reuses Q1's new
% value for Q2 and then Q2's new value for Q3 on the same edge, collapsing
% the intended delay and making the output valid too early.
healthyDeep = model(3,1,6,false);
broken = model(3,1,6,true);
figure('Name',figureNames{4});
subplot(2,1,1);
healthyPlotOutput = healthyDeep.output;
healthyPlotOutput(~healthyDeep.outputValid) = NaN;
brokenPlotOutput = broken.output;
brokenPlotOutput(~broken.outputValid) = NaN;
stairs(healthyDeep.cycle,healthyPlotOutput,'-o','LineWidth',1.3, ...
    'DisplayName','Correct simultaneous transfer');
hold on;
stairs(broken.cycle,brokenPlotOutput,'--s','LineWidth',1.3, ...
    'DisplayName','Broken cascading update');
scatter(broken.mismatchCycles,broken.output(broken.mismatchMask), ...
    65,'r','filled','DisplayName','Output mismatch');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Last-stage code [0..15]');
title('Broken case: post-edge reuse collapses register latency');
xlim([1 broken.cycleCount]);
ylim([0 15]);
legend('Location','best');

subplot(2,1,2);
healthyPlotState = healthyDeep.stateAfter;
healthyPlotState(~healthyDeep.validAfter) = NaN;
stairs(healthyDeep.cycle,healthyPlotState,'LineWidth',1.2);
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Stored stage code [0..15]');
title('Correct view: each stage advances the prior stage state');
xlim([1 healthyDeep.cycleCount]);
ylim([0 15]);
legend(healthyDeep.stageLabels,'Location','best');
fprintf(['\nBroken case: %d mismatched output cycles; output becomes valid ' ...
    '%d cycles too early.\n'],broken.mismatchCount,broken.earlyValidCount);

%% Deterministic experiment guards
expectedBaseline = [0 2 13 5 14 7 1 12 3 10 6 15 4 11 8 1];
assert(isequal(baseline.output.',expectedBaseline), ...
    'The one-stage baseline trace changed.');
assert(isequal(firstValidCycles,[2 3 4 5]) && ...
    isequal(additionalDelays,[0 1 2 3]), ...
    'Depth sweep latency limits changed.');
assert(isequal(captureCounts,[15 8 5 4]) && ...
    isequal(holdCounts,[0 7 10 11]), ...
    'Enable sweep capture/hold counts changed.');
assert(isequal(healthyDeep.stateAfter(4,:),[5 13 2]), ...
    'Correct stages must use pre-edge values.');
assert(isequal(broken.stateAfter(4,:),[5 5 5]) && ...
    broken.mismatchCount == 15 && broken.earlyValidCount == 2, ...
    'Broken cascade symptom changed.');
