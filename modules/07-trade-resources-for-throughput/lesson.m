%% P07 - Trade Resources for Throughput
% Guiding question:
% What inputs, observable effects, and failure modes matter when you trade Resources for Throughput?
clear model interactive;

%% Read - turn a fixed amount of work into a capacity equation
% P06 gave each fixed-point product a code, valid bit, identity, and
% two-cycle product-pipeline delay. P07 keeps that product contract and
% schedules eight products per frame across R identical multiplier lanes.
% Each lane accepts one product per cycle, so complete coverage requires
% G=ceil(8/R) issue cycles per frame. Frames are scheduled one at a time;
% a partial final group is not backfilled with products from the next frame.
disp(['Mental model: sharing fewer multiplier lanes reuses them across more ' ...
    'cycles; replicating lanes creates more issue slots. Ceiling division ' ...
    'keeps the partially filled final group in this non-preemptive policy.']);
disp(['Prediction: with R=2 lanes, A=4 cycles/frame, and a two-cycle lane ' ...
    'latency, how many issue cycles does one frame reserve, and what is ' ...
    'the edge difference from arrival 1 to its final product result?']);

%% Visualize the deterministic baseline
% Two lanes cover eight products in four issue groups. The source also
% offers one frame every four cycles, so arrivals equal starts and no frame
% waits. The modeled output is eight product codes plus eight valid bits.
baseline = model(2,4,3,false);
baselineFrameColor = repmat(1:baseline.frameCount, ...
    baseline.operationCount,1);
delete(findall(groot,'Type','figure','Name','P07 lesson baseline'));
figure('Name','P07 lesson baseline');
subplot(2,1,1);
scatter(baseline.actualIssueCycle(:),baseline.actualLaneIndex(:),52, ...
    baselineFrameColor(:),'filled');
grid on;
xlabel('Product issue edge [cycles]');
ylabel('Lane [modeled multiplier index]');
title('Baseline schedule: two lanes reserve four cycles per frame');
yticks(1:baseline.resourceUnits);
colorbar;
subplot(2,1,2);
bar(baseline.operationIndex,baseline.selectedReferenceProductCode);
grid on;
xlabel('Product position [operation index]');
ylabel('Product [signed product code]');
title('Selected frame: all eight product positions are valid');
fprintf(['Capacity/scheduled interval=%d/%d cycles/frame; first frame ' ...
    'arrival/completion=%d/%d; max wait=%d cycles; rate=%g ' ...
    'frames/cycle.\n'],baseline.capacityInitiationIntervalCycles, ...
    baseline.referenceScheduledIntervalCycles,baseline.arrivalCycle(1), ...
    baseline.referenceCompletionCycle(1), ...
    baseline.maximumReferenceWaitCycles, ...
    baseline.referenceScheduledFramesPerCycle);

%% Read the baseline mechanism
% Lane latency says when one issued product appears. Frame initiation
% interval says how often all lanes may begin another frame's group. A
% two-cycle lane can still accept one product each cycle. Here A=G=4, so
% neither source demand nor capacity outruns the other.
disp(baseline.equationText);

%% Move lever 1 - replicate multiplier lanes at fixed fast demand
% Hold A=1. Compare one shared lane, four lanes, and eight lanes. Capacity
% improves from eight to two to one cycles/frame, but intermediate counts
% can add idle slots without reducing the ceiling interval.
serial = model(1,1,3,false);
fourLanes = model(4,1,3,false);
fullyReplicated = model(8,1,3,false);
delete(findall(groot,'Type','figure','Name','P07 lesson resource change'));
figure('Name','P07 lesson resource change');
subplot(2,1,1);
bar([1 4 8],[serial.capacityInitiationIntervalCycles ...
    fourLanes.capacityInitiationIntervalCycles ...
    fullyReplicated.capacityInitiationIntervalCycles]);
grid on;
xlabel('Replicated lanes [modeled multipliers]');
ylabel('Capacity interval [cycles/frame]');
title('Changed capacity: more issue slots reduce groups discretely');
subplot(2,1,2);
plot(serial.frameIndex,serial.referenceWaitCycles,'-o','LineWidth',1.3, ...
    'DisplayName','R=1');
hold on;
plot(fourLanes.frameIndex,fourLanes.referenceWaitCycles,'--s', ...
    'LineWidth',1.3,'DisplayName','R=4');
plot(fullyReplicated.frameIndex,fullyReplicated.referenceWaitCycles,':d', ...
    'LineWidth',1.3,'DisplayName','R=8');
hold off;
grid on;
xlabel('Frame [frame index]');
ylabel('Queue wait [cycles]');
title('Fast demand exposes the wait reduced by replication');
legend('Location','best');

%% Explain lever 1, reset, then move lever 2
% Mechanism first: each lane adds one slot per issue group, but ceiling
% division changes only when fewer groups cover all eight products. Reset
% to R=2. Now compare A=1 overload, A=4 balance, and A=8 supply-limited
% demand without changing capacity or modeled storage.
fastDemand = model(2,1,3,false);
balancedDemand = model(2,4,3,false);
slowDemand = model(2,8,3,false);
delete(findall(groot,'Type','figure','Name','P07 lesson demand change'));
figure('Name','P07 lesson demand change');
subplot(2,1,1);
plot(fastDemand.frameIndex,fastDemand.referenceWaitCycles,'-o', ...
    'LineWidth',1.3,'DisplayName','A=1 fast source');
hold on;
plot(balancedDemand.frameIndex,balancedDemand.referenceWaitCycles,'--s', ...
    'LineWidth',1.3,'DisplayName','A=4 balanced');
plot(slowDemand.frameIndex,slowDemand.referenceWaitCycles,':d', ...
    'LineWidth',1.3,'DisplayName','A=8 slow source');
hold off;
grid on;
xlabel('Frame [frame index]');
ylabel('Queue wait [cycles]');
title('Changed demand: only offered intervals below G build wait');
legend('Location','best');
subplot(2,1,2);
bar([1 4 8],[fastDemand.referenceScheduledFramesPerCycle ...
    balancedDemand.referenceScheduledFramesPerCycle ...
    slowDemand.referenceScheduledFramesPerCycle]);
grid on;
xlabel('Offered interval [cycles/frame]');
ylabel('Scheduled rate [frames/cycle]');
title('Capacity clamps fast demand; the source limits slow demand');

%% Explain lever 2, then break the coverage equation
% Mechanism first: A changes arrival cadence, not the two-lane capacity.
% Now set R=3 and A=2. The broken controller uses floor(8/3)=2 issue
% cycles, creating only six slots. Operations 7 and 8 never receive a lane
% or a valid result, even though the controller claims a faster cadence.
healthy = model(3,2,3,false);
broken = model(3,2,3,true);
brokenProductPlot = broken.selectedActualProductCode;
brokenProductPlot(~broken.selectedProductValid) = NaN;
delete(findall(groot,'Type','figure','Name','P07 lesson broken coverage'));
figure('Name','P07 lesson broken coverage');
subplot(2,1,1);
stem(broken.operationIndex,broken.selectedReferenceProductCode,'o', ...
    'LineWidth',1.2,'DisplayName','Required product');
hold on;
stem(broken.operationIndex,brokenProductPlot,'--s','LineWidth',1.2, ...
    'DisplayName','Broken valid product');
hold off;
grid on;
xlabel('Product position [operation index]');
ylabel('Product [signed product code]');
title('Broken symptom: tail product positions have no valid result');
legend('Location','best');
subplot(2,1,2);
stairs(broken.operationIndex,double(broken.selectedProductValid), ...
    'LineWidth',1.35);
grid on;
xlabel('Product position [operation index]');
ylabel('Output valid [binary valid]');
title('Floor division violates R*G >= 8 at non-divisible R');
ylim([-0.1 1.1]);
fprintf(['Broken dropped operations=%s; selected checksum code=%d instead ' ...
    'of %d; complete frames=%d; claimed/correct rate=%g/%g Mframes/s ' ...
    'under the assumed clock.\n'], ...
    mat2str(broken.selectedDroppedOperationIndices.'), ...
    broken.selectedActualChecksumCode,broken.selectedReferenceChecksumCode, ...
    broken.completeFrameCount,broken.scheduledMframesPerSecond, ...
    healthy.referenceScheduledMframesPerSecond);

%% Explore, check, and teach back
% Run experiment.m one section at a time for the full resource and demand
% sweeps. Then use the bounded UI, run run_checks, and give the two-sentence
% teach-back in checks.md without explaining MATLAB syntax.
interactive;
