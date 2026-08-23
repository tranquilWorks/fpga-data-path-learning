%% P11 - Frame Packets Across a Stream
% Guiding question:
% What inputs, observable effects, and failure modes matter when you frame Packets Across a Stream?
clear model interactive;

%% Read - extend P10's held payload into a held framed beat
% P10 required a producer to hold valid and payload while ready is low.
% P11 treats LAST as part of that same offer. A receiver closes its current
% packet only on an edge where valid, ready, and LAST are all high.
disp(['Mental model: payload and LAST are one transferable beat. A packet ' ...
    'boundary is accepted with that beat, never as a free-running pulse.']);
disp(['Prediction: ready falls while beat four offers LAST=1. Does packet ' ...
    'one close immediately, or only when the held beat transfers?']);

%% Visualize the deterministic baseline handshake and held LAST
baseline = model(4,3,false);
visibleCycles = 1:18;
delete(findall(groot,'Type','figure','Name','P11 lesson baseline'));
baselineFigure = figure('Name','P11 lesson baseline');
subplot(2,2,1);
stairs(baseline.cycle(visibleCycles), ...
    double(baseline.applied.sourceValid(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','valid');
hold on;
stairs(baseline.cycle(visibleCycles), ...
    2+double(baseline.applied.sourceReady(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','ready');
stairs(baseline.cycle(visibleCycles), ...
    4+double(baseline.applied.transfer(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','transfer');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Handshake state [binary, vertically offset]');
title('Ready low prevents transfer on cycles 4-6');
set(gca,'YTick',[0.5 2.5 4.5], ...
    'YTickLabel',{'valid','ready','transfer'});
ylim([-0.2 5.2]);
xlim([1 18]);
drawnow;

%% Baseline view 2 - reveal payload identity
figure(baselineFigure);
subplot(2,2,2);
stairs(baseline.cycle(visibleCycles), ...
    baseline.applied.sourceBeatOrdinal(visibleCycles), ...
    'LineWidth',1.3,'DisplayName','offered beat');
hold on;
acceptedCycles = find(baseline.applied.transfer);
scatter(acceptedCycles, ...
    baseline.applied.acceptedBeatOrdinalByCycle(acceptedCycles), ...
    40,'filled','DisplayName','accepted beat');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Payload identity [beat ordinal from one]');
title('Payload beat four stays stable through the stall');
legend('Location','best');
xlim([1 18]);
ylim([0 13]);
drawnow;

%% Baseline view 3 - reveal the boundary sideband
figure(baselineFigure);
subplot(2,2,3);
stairs(baseline.cycle(visibleCycles), ...
    double(baseline.applied.sourceLast(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','LAST');
hold on;
stairs(baseline.cycle(visibleCycles), ...
    2+double(baseline.applied.sourceReady(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','ready');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Sideband state [binary, vertically offset]');
title('LAST stays high until beat four transfers on cycle 7');
set(gca,'YTick',[0.5 2.5],'YTickLabel',{'LAST','ready'});
ylim([-0.2 3.2]);
xlim([1 18]);
drawnow;

%% Baseline view 4 - reveal receiver packet grouping
figure(baselineFigure);
subplot(2,2,4);
stairs(baseline.beatOrdinal,baseline.expectedPacketIndexByBeat, ...
    'LineWidth',1.3);
hold on;
scatter(baseline.expectedBoundaryBeatOrdinals, ...
    baseline.expectedPacketIndexByBeat( ...
        baseline.expectedBoundaryBeatOrdinals),42,'filled');
hold off;
grid on;
xlabel('Accepted payload [beat ordinal from one]');
ylabel('Receiver packet [packet index from one]');
title('LAST closes packets after beats 4, 8, and 12');
xlim([1 12]);
ylim([0 4]);
sgtitle('P11 baseline: LAST travels with its four-beat packet payload');
fprintf(['Baseline boundaries=[4 8 12], lengths=[4 4 4], ' ...
    'completion=%d cycles, accepted=%d, boundary errors=%d.\n'], ...
    baseline.applied.completionCycle,baseline.applied.acceptedBeatCount, ...
    baseline.applied.boundaryMismatchCount);
drawnow;

%% Read the baseline mechanism
% Make no second prediction. Cycles 4-6 contain valid && ~ready, so neither
% payload nor LAST advances. The cycle-7 transfer accepts both together and
% closes packet one. Data conservation and framing integrity are separate:
% the receiver must check payload identity and boundary placement.
disp(baseline.transferEquationText);
disp(baseline.boundaryRuleText);
disp(baseline.holdRuleText);

%% Move lever 1 - packet length at fixed three-cycle stall
packetLengths = [2 3 4 6];
packetCounts = zeros(size(packetLengths));
boundaryDensities = zeros(size(packetLengths));
for caseIndex = 1:numel(packetLengths)
    current = model(packetLengths(caseIndex),3,false);
    packetCounts(caseIndex) = current.applied.observedPacketCount;
    boundaryDensities(caseIndex) = current.applied.boundaryDensity;
end
delete(findall(groot,'Type','figure','Name', ...
    'P11 lesson packet-length sweep'));
lengthFigure = figure('Name','P11 lesson packet-length sweep');
subplot(2,1,1);
plot(packetLengths,packetCounts,'-o','LineWidth',1.3);
grid on;
xlabel('Packet length [beats/packet]');
ylabel('Completed packets [packets]');
title('Changed view: 12 fixed beats form fewer, longer packets');
drawnow;

%% Lever 1 view 2 - reveal boundary density
figure(lengthFigure);
subplot(2,1,2);
plot(packetLengths,boundaryDensities,'-o','LineWidth',1.3);
grid on;
xlabel('Packet length [beats/packet]');
ylabel('Accepted LAST density [boundaries/beat]');
title('Boundary density equals one divided by packet length');
drawnow;

%% Explain lever 1, reset, then move lever 2
% LAST rides beside payload, so moving its healthy locations changes packet
% grouping without adding transfer cycles. Reset length to four and vary
% only consumer availability; expected boundaries stay on beats 4, 8, 12.
stallCases = 0:6;
stallCompletion = zeros(size(stallCases));
stallFrameErrors = zeros(size(stallCases));
for caseIndex = 1:numel(stallCases)
    current = model(4,stallCases(caseIndex),false);
    stallCompletion(caseIndex) = current.applied.completionCycle;
    stallFrameErrors(caseIndex) = current.applied.boundaryMismatchCount;
end
delete(findall(groot,'Type','figure','Name', ...
    'P11 lesson consumer-stall sweep'));
stallFigure = figure('Name','P11 lesson consumer-stall sweep');
subplot(2,1,1);
plot(stallCases,stallCompletion,'-o','LineWidth',1.3);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Final transfer edge [clock cycle]');
title('Changed view: completion is 12 plus the stall duration');
drawnow;

%% Lever 2 view 2 - reveal unchanged boundary integrity
figure(stallFigure);
subplot(2,1,2);
bar(stallCases,stallFrameErrors);
grid on;
xlabel('Consumer ready-low duration [cycles]');
ylabel('Boundary mismatches [accepted beats]');
title('Healthy backpressure changes timing, not framing');
ylim([0 1]);
drawnow;

%% Explain lever 2, then deliberately break LAST ownership
% Ready changes when the whole beat moves. It cannot change which payload
% owns LAST in a healthy source. The broken source below advances only its
% boundary counter while payload beat four remains stalled.
healthy = model(4,3,false);
broken = model(4,3,true);
delete(findall(groot,'Type','figure','Name','P11 lesson broken LAST'));
brokenFigure = figure('Name','P11 lesson broken LAST');
subplot(2,1,1);
stairs(healthy.cycle(visibleCycles), ...
    double(healthy.applied.sourceLast(visibleCycles)), ...
    'LineWidth',1.3,'DisplayName','healthy LAST');
hold on;
stairs(broken.cycle(visibleCycles), ...
    2+double(broken.applied.sourceLast(visibleCycles)), ...
    '--','LineWidth',1.3,'DisplayName','broken LAST');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('LAST state [binary, vertically offset]');
title('Broken LAST changes while the same payload is still owed');
set(gca,'YTick',[0.5 2.5], ...
    'YTickLabel',{'healthy LAST','broken LAST'});
ylim([-0.2 3.2]);
xlim([1 18]);
drawnow;

%% Broken view 2 - reveal the receiver-visible frame corruption
figure(brokenFigure);
subplot(2,1,2);
segments = ...
    [broken.applied.completedPacketLengths;broken.applied.trailingBeatCount];
bar(1:numel(segments),segments);
grid on;
xlabel('Receiver segment [segment index from one]');
ylabel('Observed length [beats/segment]');
title('All payloads arrive, but frames become 5, 4, and unfinished 3');
fprintf(['Broken accepted boundaries=[5 9], boundary errors=%d, ' ...
    'payload lost/duplicated/reordered=%d/%d/%d.\n'], ...
    broken.applied.boundaryMismatchCount,broken.applied.lostBeatCount, ...
    broken.applied.duplicateBeatCount,broken.applied.outOfOrderCount);
drawnow;

%% Explore, check, and teach back
% Run experiment.m one section at a time for both independent sweeps, the
% exact fault symptom, and the whole-packet-drift diagnostic limit. Then use
% the bounded UI, run run_checks, answer checks.md one prompt at a time, and
% give the two-sentence teach-back without explaining MATLAB syntax.
interactive;
