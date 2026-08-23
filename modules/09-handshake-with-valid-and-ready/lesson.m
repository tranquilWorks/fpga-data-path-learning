%% P09 - Handshake with Valid and Ready
% Guiding question:
% What inputs, observable effects, and failure modes matter when you handshake with Valid and Ready?
clear model interactive;

%% Read - separate an offer from an accepted transfer
% P08 made eight deterministic phase codes visible. P09 uses those codes as
% payload labels. The producer owns valid and data; the consumer owns ready.
% Signals are sampled immediately before the rising edge. Exactly one token
% crosses only when valid && ready is true at that edge.
disp(['Mental model: valid says one stable payload is offered; ready says ' ...
    'the consumer has capacity; their overlap at an edge moves one token.']);
disp(['Prediction: token 822 is valid at cycle 5 while ready is low. ' ...
    'Does it transfer then, or remain owed until ready returns?']);

%% Visualize the deterministic baseline signals
baseline = model(1,3,false);
visibleCycles = 1:20;
delete(findall(groot,'Type','figure','Name','P09 lesson baseline'));
baselineFigure = figure('Name','P09 lesson baseline');
subplot(2,1,1);
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
title('Baseline: transfer is the valid-and-ready overlap');
set(gca,'YTick',[0.5 2.5 4.5], ...
    'YTickLabel',{'valid','ready','transfer'});
ylim([-0.2 5.2]);
xlim([1 20]);
drawnow;

%% Baseline view 2 - reveal the held payload
figure(baselineFigure);
subplot(2,1,2);
stairs(baseline.cycle(visibleCycles), ...
    baseline.applied.dataCode(visibleCycles),'LineWidth',1.3, ...
    'DisplayName','Offered payload');
hold on;
mask = baseline.applied.transfer(visibleCycles);
scatter(baseline.cycle(visibleCycles(mask)), ...
    baseline.applied.acceptedDataCodeByCycle(visibleCycles(mask)), ...
    42,'filled','DisplayName','Accepted at edge');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Payload [unsigned 12-bit phase code]');
title('Token 822 remains stable until the cycle-8 transfer');
legend('Location','best');
fprintf(['Baseline transfers=[1 3 8 10 12 14 16 18], ' ...
    'stalled-valid=%d cycles, source bubbles=%d cycles, completion=%d.\n'], ...
    baseline.applied.activeStallCycleCount, ...
    baseline.applied.activeSourceBubbleCycleCount, ...
    baseline.applied.completionCycle);
drawnow;

%% Read the baseline mechanism
% valid alone is an owed offer, ready alone is unused capacity, and only
% valid && ready transfers. During cycles 5-7 the held token is not consumed,
% so valid and data must remain unchanged for the next cycle.
disp(baseline.equationText);
disp(baseline.holdRuleText);

%% Move lever 1 - source gaps while ready remains high
gapCases = 0:3;
gapCompletion = zeros(size(gapCases));
gapBubbles = zeros(size(gapCases));
for caseIndex = 1:numel(gapCases)
    current = model(gapCases(caseIndex),0,false);
    gapCompletion(caseIndex) = current.applied.completionCycle;
    gapBubbles(caseIndex) = current.applied.activeSourceBubbleCycleCount;
end
delete(findall(groot,'Type','figure','Name','P09 lesson source gap'));
gapFigure = figure('Name','P09 lesson source gap');
subplot(2,1,1);
plot(gapCases,gapCompletion,'-o','LineWidth',1.3);
grid on;
xlabel('Source gap after transfer [cycles]');
ylabel('Final transfer edge [clock cycle]');
title('Changed view: completion is 8 + 7 times the source gap');
drawnow;

%% Lever 1 view 2 - reveal supply bubbles
figure(gapFigure);
subplot(2,1,2);
plot(gapCases,gapBubbles,'-o','LineWidth',1.3);
grid on;
xlabel('Source gap after transfer [cycles]');
ylabel('Source bubbles before completion [cycles]');
title('Ready stays high, but no valid offer exists in a bubble');
drawnow;

%% Explain lever 1, reset, then move lever 2
% Seven inter-token gaps explain the completion change. Reset gap to zero.
% Now move only the ready-low duration beginning at cycle 5.
stallCases = 0:6;
stallCompletion = zeros(size(stallCases));
stallMaximumWait = zeros(size(stallCases));
for caseIndex = 1:numel(stallCases)
    current = model(0,stallCases(caseIndex),false);
    stallCompletion(caseIndex) = current.applied.completionCycle;
    stallMaximumWait(caseIndex) = current.applied.maximumWaitCycles;
end
delete(findall(groot,'Type','figure','Name','P09 lesson ready stall'));
stallFigure = figure('Name','P09 lesson ready stall');
subplot(2,1,1);
plot(stallCases,stallCompletion,'-o','LineWidth',1.3);
grid on;
xlabel('Ready-low duration [cycles]');
ylabel('Final transfer edge [clock cycle]');
title('Changed view: every stalled edge delays completion once');
drawnow;

%% Lever 2 view 2 - reveal held-token wait
figure(stallFigure);
subplot(2,1,2);
plot(stallCases,stallMaximumWait,'-o','LineWidth',1.3);
grid on;
xlabel('Ready-low duration [cycles]');
ylabel('Maximum offer-to-transfer wait [cycles]');
title('The same payload stays owed throughout the stall');
drawnow;

%% Explain lever 2, then break the producer-advance rule
% A stalled offer is not consumed. The deliberately broken source advances
% anyway during cycles 5-7, dropping three tokens before ready returns.
healthy = model(0,3,false);
broken = model(0,3,true);
delete(findall(groot,'Type','figure','Name', ...
    'P09 lesson broken advance'));
brokenFigure = figure('Name','P09 lesson broken advance');
subplot(2,1,1);
stairs(broken.cycle(1:14),broken.reference.dataCode(1:14), ...
    'LineWidth',1.3,'DisplayName','Healthy held payload');
hold on;
stairs(broken.cycle(1:14),broken.applied.dataCode(1:14),'--', ...
    'LineWidth',1.3,'DisplayName','Broken advancing payload');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Payload [unsigned 12-bit phase code]');
title('Broken symptom: data changes while valid is stalled');
legend('Location','best');
xlim([1 14]);
drawnow;

%% Broken view 2 - reveal missing accepted tokens
figure(brokenFigure);
subplot(2,1,2);
plot(1:numel(healthy.applied.acceptedDataCodes), ...
    healthy.applied.acceptedDataCodes,'-o','LineWidth',1.3, ...
    'DisplayName','Healthy');
hold on;
plot(1:numel(broken.applied.acceptedDataCodes), ...
    broken.applied.acceptedDataCodes,'--x','LineWidth',1.3, ...
    'DisplayName','Broken');
hold off;
grid on;
xlabel('Consumer transfer ordinal [token index from one]');
ylabel('Accepted payload [unsigned 12-bit phase code]');
title('Advancing without ready loses three middle tokens');
legend('Location','best');
fprintf(['Broken accepted token indices=[1 2 3 4 8]; drops=%d; ' ...
    'hold violations=%d; lost=%d.\n'],broken.applied.dropCount, ...
    broken.applied.holdViolationCount,broken.applied.lostTokenCount);
drawnow;

%% Explore, check, and teach back
% Run experiment.m one section at a time for both complete sweeps. Then use
% the bounded UI, run run_checks, answer checks.md one prompt at a time, and
% give the two-sentence teach-back without explaining MATLAB syntax.
interactive;
