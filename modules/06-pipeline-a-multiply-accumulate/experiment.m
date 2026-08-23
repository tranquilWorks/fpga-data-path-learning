%% P06 - Pipeline a Multiply-Accumulate
% Run one section at a time. The operands are fixed signed codes with two
% fractional bits. Every sweep resets the other lever before changing one
% scheduling property.
figureNames = {'P06 baseline MAC pipeline','P06 pipeline-stage sweep', ...
    'P06 input-period sweep','P06 broken valid alignment'};
for figureIndex = 1:numel(figureNames)
    delete(findall(groot,'Type','figure','Name',figureNames{figureIndex}));
end
clear model;
clc;

%% Baseline - two product registers with one input every cycle
% Operand codes use F=2. Their product codes therefore use Fp=4 and an LSB
% of 1/16. A product accepted at cycle k reaches the accumulator at k+L,
% where L is the number of registered product stages. Product, valid, and
% token identity take the same path in the healthy model.
baseline = model(2,1,5,false);
fprintf(['Baseline: %d products, L=%d registered product stages, input ' ...
    'period=%d cycle, first accumulation cycle=%d, completion cycle=%d.\n'], ...
    baseline.sampleCount,baseline.pipelineStages,baseline.inputPeriod, ...
    baseline.firstReferenceAccumulationCycle,baseline.completionCycle);
fprintf(['Final MAC code/value=%d/%g, product LSB=%g, reference code ' ...
    'range=[%d,%d], conservative accumulator width=%d modeled bits.\n'], ...
    baseline.finalSumCode,baseline.finalSum,baseline.productLsb, ...
    baseline.minimumReferenceCode,baseline.maximumReferenceCode, ...
    baseline.modeledAccumulatorWordLength);
fprintf(['Selected cycle %d: input token=%d, accumulator data token=%d, ' ...
    'valid=%d, product code=%d, running sum code=%d.\n'], ...
    baseline.selectedCycle,baseline.selectedInputToken, ...
    baseline.selectedDataToken,baseline.selectedActualValid, ...
    baseline.selectedAccumulatorProductCode,baseline.selectedRunningSumCode);

figure('Name',figureNames{1});
subplot(3,1,1);
stem(baseline.cycle(baseline.inputValid), ...
    baseline.inputProductValue(baseline.inputValid),'o', ...
    'LineWidth',1.25,'DisplayName','Accepted input product');
hold on;
stem(baseline.cycle(baseline.referenceAccumulatorValid), ...
    baseline.accumulatorProductValue(baseline.referenceAccumulatorValid), ...
    '--s','LineWidth',1.25,'DisplayName','Product at accumulator');
hold off;
grid on;
xlabel('Clock edge [cycles]');
ylabel('Product value [unitless product]');
title('Baseline data view: the product sequence is delayed, not changed');
legend('Location','best');

subplot(3,1,2);
stairs(baseline.cycle,double(baseline.inputValid)+1.5,'LineWidth',1.25, ...
    'DisplayName','Input valid + 1.5');
hold on;
stairs(baseline.cycle,double(baseline.referenceAccumulatorValid), ...
    '--','LineWidth',1.25,'DisplayName','Accumulator valid');
hold off;
grid on;
xlabel('Clock edge [cycles]');
ylabel('Valid row [binary, vertically offset]');
title('Baseline control view: valid receives the same two-cycle delay');
legend('Location','best');

subplot(3,1,3);
stairs(baseline.cycle,baseline.runningSum,'LineWidth',1.35, ...
    'DisplayName','Accumulated result');
grid on;
xlabel('Clock edge [cycles]');
ylabel('Running MAC result [unitless]');
title('Baseline state view: eight products accumulate to -0.5625');
legend('Location','best');

%% Sweep 1 - change only the number of product pipeline stages
% Hold the input period at one cycle. More stages add latency and modeled
% storage slots, but aligned product order, input cadence, and final sum do
% not change.
pipelineStageCounts = 0:4;
firstAccumulationCycles = zeros(size(pipelineStageCounts));
completionCyclesByStage = zeros(size(pipelineStageCounts));
storageSlots = zeros(size(pipelineStageCounts));
finalSumsByStage = zeros(size(pipelineStageCounts));
stageReference = model(0,1,5,false);
fixedStageProducts = stageReference.productCodeSequence;
fixedStageInputCycles = stageReference.cycle(stageReference.inputValid);
fprintf('\nSweep 1 - pipeline stages (input period fixed at 1 cycle):\n');
for sweepIndex = 1:numel(pipelineStageCounts)
    current = model(pipelineStageCounts(sweepIndex),1,5,false);
    firstAccumulationCycles(sweepIndex) = ...
        current.firstReferenceAccumulationCycle;
    completionCyclesByStage(sweepIndex) = current.completionCycle;
    storageSlots(sweepIndex) = current.modeledProductStorageSlots;
    finalSumsByStage(sweepIndex) = current.finalSum;
    assert(current.inputPeriod == 1 && ...
        isequal(current.productCodeSequence,fixedStageProducts) && ...
        isequal(current.cycle(current.inputValid),fixedStageInputCycles), ...
        'Pipeline-stage sweep must preserve products and input cadence.');
    assert(current.finalSumCode == stageReference.finalSumCode && ...
        current.validDataMismatchCount == 0, ...
        'Healthy stage changes must preserve aligned numerical results.');
    fprintf(['  L=%d -> first accumulation=%d, completion=%d cycles, ' ...
        'storage=%d product/%d valid slots, final=%g\n'], ...
        current.pipelineStages,current.firstReferenceAccumulationCycle, ...
        current.completionCycle,current.modeledProductStorageSlots, ...
        current.modeledValidStorageBits,current.finalSum);
end

figure('Name',figureNames{2});
subplot(3,1,1);
plot(pipelineStageCounts,firstAccumulationCycles,'-o','LineWidth',1.35, ...
    'DisplayName','First accumulation edge');
hold on;
plot(pipelineStageCounts,completionCyclesByStage,'--s','LineWidth',1.35, ...
    'DisplayName','Final accumulation edge');
hold off;
grid on;
xlabel('Registered product pipeline stages L [stages]');
ylabel('Observed edge [cycles]');
title('Sweep 1: each product stage adds one cycle of latency');
xticks(pipelineStageCounts);
legend('Location','best');

subplot(3,1,2);
plot(pipelineStageCounts,storageSlots,'-o','LineWidth',1.35);
grid on;
xlabel('Registered product pipeline stages L [stages]');
ylabel('Modeled product storage [values]');
title('Schedule model: one product storage slot per added stage');
xticks(pipelineStageCounts);

subplot(3,1,3);
plot(pipelineStageCounts,finalSumsByStage,'-o','LineWidth',1.35);
grid on;
xlabel('Registered product pipeline stages L [stages]');
ylabel('Final MAC result [unitless]');
title('Aligned numerical result stays fixed at every stage count');
xticks(pipelineStageCounts);

%% Sweep 2 - reset to two stages, then change only input spacing
% The product pipeline returns to L=2. Increasing the input period inserts
% bubbles between tokens. First-product latency remains two cycles, while
% accumulation-event spacing and completion time grow.
inputPeriods = 1:4;
completionCyclesByPeriod = zeros(size(inputPeriods));
accumulatorEventSpacing = zeros(size(inputPeriods));
finalSumsByPeriod = zeros(size(inputPeriods));
periodReference = model(2,1,5,false);
fixedPeriodProducts = periodReference.productCodeSequence;
fprintf('\nSweep 2 - input period (pipeline stages reset to 2):\n');
for sweepIndex = 1:numel(inputPeriods)
    current = model(2,inputPeriods(sweepIndex),5,false);
    validCycles = current.cycle(current.referenceAccumulatorValid);
    completionCyclesByPeriod(sweepIndex) = current.completionCycle;
    accumulatorEventSpacing(sweepIndex) = mean(diff(validCycles));
    finalSumsByPeriod(sweepIndex) = current.finalSum;
    assert(current.pipelineStages == 2 && ...
        current.firstReferenceAccumulationCycle == 3 && ...
        isequal(current.productCodeSequence,fixedPeriodProducts), ...
        'Input-period sweep must preserve pipeline depth and products.');
    assert(current.finalSumCode == periodReference.finalSumCode && ...
        current.validDataMismatchCount == 0, ...
        'Healthy bubbles must not drop, duplicate, or reorder products.');
    fprintf(['  period=%d -> accumulation spacing=%g cycles, ' ...
        'completion=%d cycles, products=%d, final=%g\n'], ...
        current.inputPeriod,accumulatorEventSpacing(sweepIndex), ...
        current.completionCycle,current.accumulatedProductCount, ...
        current.finalSum);
end

figure('Name',figureNames{3});
subplot(3,1,1);
plot(inputPeriods,completionCyclesByPeriod,'-o','LineWidth',1.35);
grid on;
xlabel('Input period [cycles/product]');
ylabel('Final accumulation edge [cycles]');
title('Sweep 2: input bubbles extend total completion time');
xticks(inputPeriods);

subplot(3,1,2);
plot(inputPeriods,accumulatorEventSpacing,'-o','LineWidth',1.35);
grid on;
xlabel('Input period [cycles/product]');
ylabel('Accumulation-event spacing [cycles]');
title('Delayed valid reproduces the offered bubble spacing');
xticks(inputPeriods);

subplot(3,1,3);
plot(inputPeriods,finalSumsByPeriod,'-o','LineWidth',1.35);
grid on;
xlabel('Input period [cycles/product]');
ylabel('Final MAC result [unitless]');
title('Bubbles change elapsed cycles, not the ordered numerical result');
xticks(inputPeriods);

%% Deliberately broken case - valid bypasses the product pipeline
% Named violated assumption: valid and token identity must receive exactly
% the same delay as product data. The broken path asserts valid immediately
% while the product still takes two cycles. It performs two empty early
% accumulations, pairs six valid tokens with stale products, and then drops
% product tokens 7 and 8 after valid has ended.
healthy = model(2,1,5,false);
broken = model(2,1,5,true);
assert(isequal(broken.droppedTokenIndices,[7; 8]) && ...
    broken.finalSumCode == -24 && healthy.finalSumCode == -9, ...
    'Broken valid alignment must lose the final two deterministic products.');
fprintf(['\nDeliberately broken valid alignment: premature=%d, mispaired=%d, ' ...
    'late reference products=%d, dropped tokens=%s, final code/value=' ...
    '%d/%g instead of %d/%g.\n'], ...
    broken.prematureValidCount,broken.mispairedProductCount, ...
    broken.lateReferenceCount,mat2str(broken.droppedTokenIndices.'), ...
    broken.finalSumCode,broken.finalSum,healthy.finalSumCode,healthy.finalSum);

figure('Name',figureNames{4});
subplot(3,1,1);
stairs(healthy.cycle,double(healthy.referenceAccumulatorValid)+1.5, ...
    'LineWidth',1.25,'DisplayName','Required delayed valid + 1.5');
hold on;
stairs(broken.cycle,double(broken.accumulatorValid),'--', ...
    'LineWidth',1.25,'DisplayName','Broken bypassed valid');
hold off;
grid on;
xlabel('Clock edge [cycles]');
ylabel('Valid row [binary, vertically offset]');
title('Broken control view: valid no longer names the product at the MAC');
legend('Location','best');

subplot(3,1,2);
stem(broken.cycle(broken.accumulatorValid), ...
    broken.accumulatorValidTokenIndex(broken.accumulatorValid),'o', ...
    'LineWidth',1.2,'DisplayName','Token claimed by broken valid');
hold on;
stem(broken.cycle(broken.accumulatorValid), ...
    broken.referenceAccumulatorTokenIndex(broken.accumulatorValid), ...
    '--s','LineWidth',1.2,'DisplayName','Product token actually present');
hold off;
grid on;
xlabel('Clock edge [cycles]');
ylabel('Token identity [token index]');
title('Broken association: every claimed token names empty or stale data');
legend('Location','best');

subplot(3,1,3);
stairs(healthy.cycle,healthy.referenceRunningSum,'LineWidth',1.35, ...
    'DisplayName','Healthy aligned sum');
hold on;
stairs(broken.cycle,broken.runningSum,'--','LineWidth',1.35, ...
    'DisplayName','Broken bypassed-valid sum');
hold off;
grid on;
xlabel('Clock edge [cycles]');
ylabel('Running MAC result [unitless]');
title('Recognizable symptom: the result freezes before the final products');
legend('Location','best');

%% Explain and check
% Pipeline stages shift when a result becomes observable; they do not
% change exact product codes or their order. Input spacing inserts bubbles,
% and the valid path must reproduce those bubbles after the same delay as
% data. Modeled stages and word length are not synthesis or timing results.
disp(baseline.equationText);
disp('Run run_checks, then answer checks.md one prompt at a time.');
