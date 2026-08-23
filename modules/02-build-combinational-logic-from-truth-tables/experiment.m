%% P02 - Build Combinational Logic from Truth Tables
% Run one section at a time. Each section changes one named quantity while
% the other baseline quantities remain fixed.
figureNames = {'P02 baseline truth table','P02 threshold sweep', ...
    'P02 probability sweep','P02 broken LUT row'};
for figureIndex = 1:numel(figureNames)
    delete(findall(groot,'Type','figure','Name',figureNames{figureIndex}));
end
clear model;
clc;

%% Baseline - exhaustive 2-of-3 majority truth table
% A is the most-significant address bit and C is the least-significant:
% address = 4*A + 2*B + C. Logic levels and addresses are unitless.
baseline = model(2,0.5,3,-1);
fprintf('Baseline: 2-of-3 voter, p = %.2f, selected address = %d (%s)\n', ...
    baseline.inputHighProbability,baseline.selectedAddress, ...
    baseline.inputLabels{baseline.selectedAddress+1});
fprintf('Address  A B C  HIGH count  specified Y  LUT Y\n');
for row = 1:numel(baseline.inputAddress)
    fprintf('   %d     %d %d %d      %d           %d        %d\n', ...
        baseline.inputAddress(row),baseline.inputBits(row,1), ...
        baseline.inputBits(row,2),baseline.inputBits(row,3), ...
        baseline.highCount(row),baseline.specifiedOutput(row), ...
        baseline.lutOutput(row));
end
fprintf('Metric: %d of 8 rows assert Y; P(Y=1) = %.3f [unitless].\n', ...
    baseline.assertedRowCount,baseline.specifiedHighProbability);

figure('Name',figureNames{1});
stairs(baseline.inputAddress,double(baseline.specifiedOutput),'-o', ...
    'LineWidth',1.4,'DisplayName','Specified output');
grid on;
xlabel('Input address 4A+2B+C [unitless]');
ylabel('Logic output Y [binary]');
title('Baseline: every input row maps to one output');
xticks(0:7);
xticklabels(baseline.inputLabels);
yticks([0 1]);
ylim([-0.1 1.1]);

%% Sweep 1 - change only the required number of HIGH inputs
% k=1 is OR, k=2 is majority, and k=3 is AND. The input probability stays
% at 0.5, so this sweep changes the truth-table mapping itself.
thresholds = 1:3;
assertedRows = zeros(size(thresholds));
sweepOutputs = zeros(8,numel(thresholds));
fprintf('\nSweep 1 - required HIGH inputs k (p fixed at 0.50):\n');
for sweepIndex = 1:numel(thresholds)
    current = model(thresholds(sweepIndex),0.5,3,-1);
    assertedRows(sweepIndex) = current.assertedRowCount;
    sweepOutputs(:,sweepIndex) = double(current.specifiedOutput);
    fprintf('  k = %d -> %d asserted rows, P(Y=1) = %.3f\n', ...
        thresholds(sweepIndex),current.assertedRowCount, ...
        current.specifiedHighProbability);
end

figure('Name',figureNames{2});
stairs(baseline.inputAddress,sweepOutputs,'-o','LineWidth',1.2);
grid on;
xlabel('Input address 4A+2B+C [unitless]');
ylabel('Specified output Y [binary]');
title('Sweep 1: k changes which truth-table rows assert');
xticks(0:7);
xticklabels(baseline.inputLabels);
yticks([0 1]);
ylim([-0.1 1.1]);
legend('k=1 (OR)','k=2 (majority)','k=3 (AND)', ...
    'Location','best');

%% Sweep 2 - change only how often HIGH inputs occur
% The 2-of-3 truth table stays fixed. Only the independent, equal input-HIGH
% probability p changes how frequently each row is expected to occur.
probabilities = 0:0.05:1;
outputHighProbability = zeros(size(probabilities));
for sweepIndex = 1:numel(probabilities)
    current = model(2,probabilities(sweepIndex),3,-1);
    outputHighProbability(sweepIndex) = current.specifiedHighProbability;
    assert(isequal(current.specifiedOutput,baseline.specifiedOutput), ...
        'Probability sweep must not change the truth-table mapping.');
end
independentEquation = 3*probabilities.^2 - 2*probabilities.^3;

figure('Name',figureNames{3});
plot(probabilities,outputHighProbability,'o-','LineWidth',1.4, ...
    'DisplayName','Weighted truth-table rows');
hold on;
plot(probabilities,independentEquation,'--','LineWidth',1.2, ...
    'DisplayName','3p^2 - 2p^3');
hold off;
grid on;
xlabel('Independent input HIGH probability p [unitless]');
ylabel('Output HIGH probability P(Y=1) [unitless]');
title('Sweep 2: p changes row frequency, not the truth table');
legend('Location','best');
lowActivity = model(2,0.2,3,-1);
highActivity = model(2,0.8,3,-1);
fprintf('\nSweep 2 - at p = 0.20, P(Y=1) = %.3f; at p = 0.80, %.3f.\n', ...
    lowActivity.specifiedHighProbability,highActivity.specifiedHighProbability);

%% Deliberately broken case - flip LUT address 6 (binary 110)
% The named assumption is that every reachable LUT entry matches its
% specified truth-table row. One wrong entry must be found by exhaustive
% comparison even if a few favorite input examples still pass.
faultAddress = 6;
broken = model(2,0.5,faultAddress,faultAddress);
figure('Name',figureNames{4});
stairs(broken.inputAddress,double(broken.specifiedOutput),'-o', ...
    'LineWidth',1.4,'DisplayName','Specified output');
hold on;
stairs(broken.inputAddress,double(broken.lutOutput),'--s', ...
    'LineWidth',1.2,'DisplayName','Broken LUT output');
scatter(broken.mismatchAddresses,double(broken.lutOutput(broken.mismatchMask)), ...
    90,'r','filled','DisplayName','Mismatch');
hold off;
grid on;
xlabel('Input address 4A+2B+C [unitless]');
ylabel('Logic output Y [binary]');
title('Broken case: one flipped LUT entry escapes spot checks');
xticks(0:7);
xticklabels(broken.inputLabels);
yticks([0 1]);
ylim([-0.1 1.1]);
legend('Location','best');
fprintf('\nBroken case: %d mismatch at address %d; weighted error probability = %.3f [unitless].\n', ...
    broken.mismatchCount, ...
    broken.mismatchAddresses,broken.mismatchProbability);

%% Deterministic experiment guards
assert(isequal(double(baseline.specifiedOutput).',[0 0 0 1 0 1 1 1]), ...
    'The baseline majority truth vector changed.');
assert(isequal(baseline.specifiedOutput,baseline.equationOutput), ...
    'Truth table and independent majority equation disagree.');
assert(isequal(assertedRows,[7 4 1]), ...
    'Threshold sweep limiting counts changed.');
assert(max(abs(outputHighProbability-independentEquation)) < 1e-12, ...
    'Weighted truth table disagrees with the independent probability equation.');
assert(broken.mismatchCount == 1 && broken.mismatchAddresses == faultAddress, ...
    'Broken case must isolate exactly address 6.');
