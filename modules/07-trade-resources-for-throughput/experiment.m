%% P07 - Trade Resources for Throughput
% Run one section at a time. Every frame contains eight deterministic
% P06-style products. Each sweep resets the other lever before changing
% either modeled multiplier replication or offered source demand. The
% scheduler is non-preemptive across frames, so partial groups stay idle.
figureNames = {'P07 baseline resource schedule', ...
    'P07 resource-unit sweep','P07 offered-interval sweep', ...
    'P07 broken floor schedule'};
for figureIndex = 1:numel(figureNames)
    delete(findall(groot,'Type','figure','Name',figureNames{figureIndex}));
end
clear model;
clc;

%% Baseline - two product lanes and one frame every four cycles
% Eight operations divided across two lanes require G=ceil(8/2)=4 issue
% cycles. A product result appears two cycles after its issue edge. The
% offered interval equals capacity, so the finite queue never builds.
baseline = model(2,4,3,false);
fprintf(['Baseline: %d frames x %d products, R=%d modeled multiplier ' ...
    'lanes, A=%d cycles/frame, G=%d cycles/frame, lane latency=%d ' ...
    'cycles.\n'],baseline.frameCount,baseline.operationCount, ...
    baseline.resourceUnits,baseline.offeredFrameInterval, ...
    baseline.capacityInitiationIntervalCycles, ...
    baseline.pipelineLatencyCycles);
fprintf(['Arrivals/starts=%s; completions=%s; max wait=%d cycles; ' ...
    'packing=%g percent; scheduled rate=%g frames/cycle (%g Mframes/s ' ...
    'at assumed %g MHz).\n'],mat2str(baseline.arrivalCycle.'), ...
    mat2str(baseline.referenceCompletionCycle.'), ...
    baseline.maximumReferenceWaitCycles,100*baseline.packingUtilization, ...
    baseline.referenceScheduledFramesPerCycle, ...
    baseline.referenceScheduledMframesPerSecond, ...
    baseline.assumedClockFrequencyMHz);
fprintf(['Selected frame %d checksum code=%d; products=%s; valid=%s. ' ...
    'The checksum is diagnostic, not a modeled reduction datapath.\n'], ...
    baseline.selectedFrame,baseline.selectedReferenceChecksumCode, ...
    mat2str(baseline.selectedReferenceProductCode.'), ...
    mat2str(double(baseline.selectedProductValid.')));

frameColor = repmat(1:baseline.frameCount,baseline.operationCount,1);
validIssue = baseline.actualProductValidByFrame;
figure('Name',figureNames{1});
subplot(3,1,1);
scatter(baseline.actualIssueCycle(validIssue), ...
    baseline.actualLaneIndex(validIssue),52,frameColor(validIssue),'filled');
grid on;
xlabel('Product issue edge [cycles]');
ylabel('Lane [modeled multiplier index]');
title('Baseline schedule: each color is one eight-product frame');
yticks(1:baseline.resourceUnits);
colorbar;

subplot(3,1,2);
stem(baseline.frameIndex,baseline.arrivalCycle,'o','LineWidth',1.2, ...
    'DisplayName','Arrival edge');
hold on;
stem(baseline.frameIndex,baseline.referenceStartCycle,'--s', ...
    'LineWidth',1.2,'DisplayName','Start edge');
stem(baseline.frameIndex,baseline.referenceCompletionCycle,':d', ...
    'LineWidth',1.2,'DisplayName','Final product result edge');
hold off;
grid on;
xlabel('Frame [frame index]');
ylabel('Clock edge [cycles]');
title('Balanced demand: every frame starts immediately');
legend('Location','best');

subplot(3,1,3);
bar(baseline.operationIndex,baseline.selectedReferenceProductCode);
grid on;
xlabel('Product position [operation index]');
ylabel('Product [signed product code]');
title('Selected output: eight valid product codes, LSB = 1/16');

%% Sweep 1 - change only the number of modeled multiplier lanes
% Hold A at one cycle/frame. Resource replication changes the ceiling
% capacity, packing utilization, pipeline storage, and finite-queue wait.
% It does not change offered arrivals, product codes, or product count.
resourceCounts = 1:8;
capacityIntervals = zeros(size(resourceCounts));
firstFrameLatencies = zeros(size(resourceCounts));
scheduledRates = zeros(size(resourceCounts));
packingPercent = zeros(size(resourceCounts));
idleSlots = zeros(size(resourceCounts));
maximumWaits = zeros(size(resourceCounts));
storageBits = zeros(size(resourceCounts));
resourceReference = model(1,1,3,false);
fixedResourceProducts = resourceReference.productCodeByFrame;
fixedResourceArrivals = resourceReference.arrivalCycle;
fprintf('\nSweep 1 - modeled multiplier lanes (A fixed at 1 cycle/frame):\n');
for sweepIndex = 1:numel(resourceCounts)
    current = model(resourceCounts(sweepIndex),1,3,false);
    capacityIntervals(sweepIndex) = ...
        current.capacityInitiationIntervalCycles;
    firstFrameLatencies(sweepIndex) = current.referenceLatencyCycles(1);
    scheduledRates(sweepIndex) = current.referenceScheduledFramesPerCycle;
    packingPercent(sweepIndex) = 100*current.packingUtilization;
    idleSlots(sweepIndex) = current.idleLaneSlotsPerFrame;
    maximumWaits(sweepIndex) = current.maximumReferenceWaitCycles;
    storageBits(sweepIndex) = current.modeledProductPipelineStorageBits;
    assert(current.offeredFrameInterval == 1 && ...
        isequal(current.arrivalCycle,fixedResourceArrivals) && ...
        isequal(current.productCodeByFrame,fixedResourceProducts), ...
        'Resource sweep must preserve source arrivals and product vectors.');
    assert(current.completeFrameCount == current.frameCount && ...
        current.totalDroppedOperationCount == 0, ...
        'Healthy resource replication must cover every product.');
    fprintf(['  R=%d -> G=%d cycles/frame, first-frame latency=%d cycles, ' ...
        'rate=%g frames/cycle, packing=%g percent, idle=%d slots/frame, ' ...
        'max wait=%d cycles, lane storage=%d modeled bits\n'], ...
        current.resourceUnits,current.capacityInitiationIntervalCycles, ...
        current.referenceLatencyCycles(1), ...
        current.referenceScheduledFramesPerCycle, ...
        100*current.packingUtilization,current.idleLaneSlotsPerFrame, ...
        current.maximumReferenceWaitCycles, ...
        current.modeledProductPipelineStorageBits);
end

figure('Name',figureNames{2});
subplot(2,2,1);
plot(resourceCounts,capacityIntervals,'-o','LineWidth',1.35, ...
    'DisplayName','Capacity interval');
hold on;
plot(resourceCounts,firstFrameLatencies,'--s','LineWidth',1.35, ...
    'DisplayName','First-frame edge latency');
hold off;
grid on;
xlabel('Replicated lanes [modeled multipliers]');
ylabel('Time [cycles]');
title('Ceiling division creates throughput plateaus');
legend('Location','best');
xticks(resourceCounts);

subplot(2,2,2);
plot(resourceCounts,scheduledRates,'-o','LineWidth',1.35);
grid on;
xlabel('Replicated lanes [modeled multipliers]');
ylabel('Scheduled rate [frames/cycle]');
title('Useful throughput rises only when G falls');
xticks(resourceCounts);

subplot(2,2,3);
plot(resourceCounts,packingPercent,'-o','LineWidth',1.35, ...
    'DisplayName','Useful packing');
hold on;
plot(resourceCounts,10*idleSlots,'--s','LineWidth',1.35, ...
    'DisplayName','Idle slots x 10');
hold off;
grid on;
xlabel('Replicated lanes [modeled multipliers]');
ylabel('Packing [percent]; idle scale [10 slots/frame]');
title('Extra lanes can sit idle in the final group');
legend('Location','best');
xticks(resourceCounts);

subplot(2,2,4);
plot(resourceCounts,maximumWaits,'-o','LineWidth',1.35, ...
    'DisplayName','Maximum finite-queue wait');
hold on;
plot(resourceCounts,storageBits/4,'--s','LineWidth',1.35, ...
    'DisplayName','Pipeline storage / 4');
hold off;
grid on;
xlabel('Replicated lanes [modeled multipliers]');
ylabel('Wait [cycles]; storage scale [modeled bits/4]');
title('Replication trades modeled storage for lower wait');
legend('Location','best');
xticks(resourceCounts);

%% Explain sweep 1, reset, then sweep 2 - offered frame interval
% Mechanism first: another lane adds an issue slot, but G changes only when
% fewer groups cover all eight products. Reset to R=2. Now change A while
% capacity and modeled resources remain fixed. Demand above capacity queues;
% demand below capacity leaves lanes waiting for the source.
offeredIntervals = 1:8;
scheduledIntervals = zeros(size(offeredIntervals));
scheduledDemandRates = zeros(size(offeredIntervals));
demandMaximumWaits = zeros(size(offeredIntervals));
requiredResourceCounts = zeros(size(offeredIntervals));
maximumQueueDepths = zeros(size(offeredIntervals));
demandReference = model(2,1,3,false);
fixedDemandProducts = demandReference.productCodeByFrame;
fixedDemandStorage = demandReference.modeledProductPipelineStorageBits;
fprintf('\nSweep 2 - offered interval (R fixed at 2 lanes):\n');
for sweepIndex = 1:numel(offeredIntervals)
    current = model(2,offeredIntervals(sweepIndex),3,false);
    scheduledIntervals(sweepIndex) = ...
        current.referenceScheduledIntervalCycles;
    scheduledDemandRates(sweepIndex) = ...
        current.referenceScheduledFramesPerCycle;
    demandMaximumWaits(sweepIndex) = current.maximumReferenceWaitCycles;
    requiredResourceCounts(sweepIndex) = ...
        current.requiredResourceUnitsForOfferedInterval;
    maximumQueueDepths(sweepIndex) = current.maximumReferenceQueueDepth;
    assert(current.resourceUnits == 2 && ...
        current.capacityInitiationIntervalCycles == 4 && ...
        current.modeledProductPipelineStorageBits == fixedDemandStorage && ...
        isequal(current.productCodeByFrame,fixedDemandProducts), ...
        'Offered-interval sweep must preserve resources and products.');
    assert(current.completeFrameCount == current.frameCount && ...
        current.totalDroppedOperationCount == 0, ...
        'Finite healthy demand sweep must remain lossless.');
    fprintf(['  A=%d cycles/frame -> scheduled interval=%d cycles/frame, ' ...
        'rate=%g frames/cycle, max wait=%d cycles, max queued=%d frames, ' ...
        'lanes needed to sustain source=%d\n'], ...
        current.offeredFrameInterval, ...
        current.referenceScheduledIntervalCycles, ...
        current.referenceScheduledFramesPerCycle, ...
        current.maximumReferenceWaitCycles, ...
        current.maximumReferenceQueueDepth, ...
        current.requiredResourceUnitsForOfferedInterval);
end

figure('Name',figureNames{3});
subplot(2,2,1);
plot(offeredIntervals,scheduledIntervals,'-o','LineWidth',1.35);
grid on;
xlabel('Offered interval [cycles/frame]');
ylabel('Scheduled interval [cycles/frame]');
title('Capacity clamps fast demand; slow demand sets cadence');
xticks(offeredIntervals);

subplot(2,2,2);
plot(offeredIntervals,scheduledDemandRates,'-o','LineWidth',1.35);
grid on;
xlabel('Offered interval [cycles/frame]');
ylabel('Scheduled rate [frames/cycle]');
title('Two lanes cannot exceed one frame per four cycles');
xticks(offeredIntervals);

subplot(2,2,3);
plot(offeredIntervals,demandMaximumWaits,'-o','LineWidth',1.35, ...
    'DisplayName','Maximum wait');
hold on;
plot(offeredIntervals,maximumQueueDepths,'--s','LineWidth',1.35, ...
    'DisplayName','Maximum queued frames');
hold off;
grid on;
xlabel('Offered interval [cycles/frame]');
ylabel('Wait [cycles]; queue [frames]');
title('Finite queue grows only when A is below capacity G');
legend('Location','best');
xticks(offeredIntervals);

subplot(2,2,4);
plot(offeredIntervals,requiredResourceCounts,'-o','LineWidth',1.35);
grid on;
xlabel('Offered interval [cycles/frame]');
ylabel('Required lanes [modeled multipliers]');
title('Ceiling rule sizes ideal lanes for the offered cadence');
xticks(offeredIntervals);

%% Deliberately broken case - floor division under-allocates lane slots
% Named violated assumption: resourceUnits*issueCycles must cover all eight
% operations. With R=3, floor(8/3)=2 reserves six slots, drops operations 7
% and 8, and falsely claims a two-cycle frame interval.
healthy = model(3,2,3,false);
broken = model(3,2,3,true);
assert(isequal(broken.selectedDroppedOperationIndices,[7; 8]) && ...
    broken.completeFrameCount == 0 && ...
    broken.scheduledMframesPerSecond == 50 && ...
    abs(healthy.referenceScheduledMframesPerSecond-100/3) < 1e-12, ...
    'Broken floor schedule must omit the deterministic tail products.');
fprintf(['\nDeliberately broken floor schedule: R=%d, A=%d, correct/broken ' ...
    'issue cycles=%d/%d, slots=%d, dropped operations/frame=%s, ' ...
    'complete frames=%d/%d, claimed/correct rate=%g/%g Mframes/s.\n'], ...
    broken.resourceUnits,broken.offeredFrameInterval, ...
    broken.capacityInitiationIntervalCycles, ...
    broken.scheduledIssueCyclesPerFrame,broken.scheduledSlotCountPerFrame, ...
    mat2str(broken.selectedDroppedOperationIndices.'), ...
    broken.completeFrameCount,broken.frameCount, ...
    broken.scheduledMframesPerSecond, ...
    broken.referenceScheduledMframesPerSecond);

brokenProductPlot = broken.selectedActualProductCode;
brokenProductPlot(~broken.selectedProductValid) = NaN;
figure('Name',figureNames{4});
subplot(2,2,1);
plot(healthy.frameIndex,healthy.referenceCompletionCycle,'-o', ...
    'LineWidth',1.35,'DisplayName','Correct final-product edge');
hold on;
plot(broken.frameIndex,broken.claimedCompletionCycle,'--s', ...
    'LineWidth',1.35,'DisplayName','Broken claimed edge');
hold off;
grid on;
xlabel('Frame [frame index]');
ylabel('Completion edge [cycles]');
title('Broken controller claims frames before all products exist');
legend('Location','best');

subplot(2,2,2);
stem(broken.operationIndex,broken.selectedReferenceProductCode,'o', ...
    'LineWidth',1.2,'DisplayName','Required product code');
hold on;
stem(broken.operationIndex,brokenProductPlot,'--s','LineWidth',1.2, ...
    'DisplayName','Broken valid product code');
scatter(broken.selectedDroppedOperationIndices, ...
    zeros(size(broken.selectedDroppedOperationIndices)),70,'x', ...
    'LineWidth',1.5,'DisplayName','Missing operation');
hold off;
grid on;
xlabel('Product position [operation index]');
ylabel('Product [signed product code]');
title('Selected frame loses the two tail operations');
legend('Location','best');

subplot(2,2,3);
stairs(broken.operationIndex,double(broken.selectedProductValid), ...
    'LineWidth',1.35);
grid on;
xlabel('Product position [operation index]');
ylabel('Output valid [binary valid]');
title('Recognizable symptom: the output vector is incomplete');
ylim([-0.1 1.1]);

subplot(2,2,4);
plot(broken.frameIndex,broken.referenceDiagnosticChecksumCode,'-o', ...
    'LineWidth',1.35,'DisplayName','Complete-vector diagnostic');
hold on;
plot(broken.frameIndex,broken.actualDiagnosticChecksumCode,'--s', ...
    'LineWidth',1.35,'DisplayName','Incomplete-vector diagnostic');
hold off;
grid on;
xlabel('Frame [frame index]');
ylabel('Diagnostic sum [signed product code]');
title('Checksum divergence reveals missing work; no adder is modeled');
legend('Location','best');

%% Explain and check
% Ceiling division preserves complete product vectors across every bounded
% resource/demand pair. Source spacing and resource replication are
% independent levers. Modeled lanes, storage, and the 100 MHz assumption
% are not synthesis, timing, power, or physical evidence.
disp(baseline.equationText);
disp('Run run_checks, then answer checks.md one prompt at a time.');
