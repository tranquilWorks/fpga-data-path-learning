%% P03 - Store State with Registers
% Guiding question:
% What inputs, observable effects, and failure modes matter when you store State with Registers?
clear model interactive;

%% Read - add memory to the combinational decisions from P02
% P02's truth table mapped current input bits directly to an output and had
% no stored history. A register changes that contract: at a rising edge,
% reset loads a known value, otherwise enable captures D, and a disabled
% register holds its previous Q. Between edges, Q is the remembered state.
disp(['Mental model: inspect D before an edge and Q after it; reset has ' ...
    'priority, enable captures, and disable holds.']);
disp('Prediction: on cycle 3, will an enabled one-stage Q equal the new D or its older value?');

%% Visualize the deterministic one-register baseline
baseline = model(1,1,6,false);
delete(findall(groot,'Type','figure','Name','P03 lesson baseline'));
figure('Name','P03 lesson baseline');
baselinePlotOutput = baseline.output;
baselinePlotOutput(~baseline.outputValid) = NaN;
stairs(baseline.cycle,baseline.inputData,'-o','LineWidth',1.3, ...
    'DisplayName','D before edge');
hold on;
stairs(baseline.cycle,baselinePlotOutput,'--s','LineWidth',1.3, ...
    'DisplayName','Q after edge');
scatter(baseline.cycle(~baseline.outputValid), ...
    baseline.output(~baseline.outputValid),75,[0.35 0.35 0.35],'x', ...
    'LineWidth',1.6,'DisplayName','Reset fill (invalid)');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Unsigned 4-bit code [0..15]');
title('Baseline: reset, then capture on every enabled edge');
xlim([1 baseline.cycleCount]);
ylim([0 15]);
legend('Location','best');
fprintf('Cycle 1 reset wins over D=%d; cycle 3 captures D=%d into Q=%d.\n', ...
    baseline.inputData(1),baseline.inputData(3),baseline.output(3));

%% Read the baseline mechanism
% For one stage, Q[n]=0 when reset[n]=1; otherwise Q[n]=D[n] when
% enable[n]=1; otherwise Q[n]=Q[n-1]. The plotted zero on reset is marked
% invalid, so it is startup state rather than an accepted data sample.
disp(baseline.equationText);

%% Move lever 1 - add register stages
% Only depth changes; enable remains HIGH after reset. Every later stage
% captures the preceding stage's pre-edge value, adding one active-edge
% delay relative to Q1 and four logical state bits in this model.
threeStages = model(3,1,6,false);
delete(findall(groot,'Type','figure','Name','P03 lesson depth change'));
figure('Name','P03 lesson depth change');
threeStagePlotOutput = threeStages.output;
threeStagePlotOutput(~threeStages.outputValid) = NaN;
stairs(baseline.cycle,baselinePlotOutput,'-o','LineWidth',1.3, ...
    'DisplayName','1 stage');
hold on;
stairs(threeStages.cycle,threeStagePlotOutput,'--s','LineWidth',1.3, ...
    'DisplayName','3 stages');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Last-stage code [0..15]');
title('Changed view: depth delays the accepted sequence');
xlim([1 baseline.cycleCount]);
ylim([0 15]);
legend('Location','best');

%% Explain lever 1, reset, then move lever 2
% Mechanism first: depth changes where prior state must travel, not which
% input samples are accepted. Reset to one stage, then change only enable
% period from 1 to 3. Disabled edges now preserve Q instead of sampling D.
sparseEnable = model(1,3,6,false);
delete(findall(groot,'Type','figure','Name','P03 lesson enable change'));
figure('Name','P03 lesson enable change');
sparseEnablePlotOutput = sparseEnable.output;
sparseEnablePlotOutput(~sparseEnable.outputValid) = NaN;
stairs(baseline.cycle,baselinePlotOutput,'-o','LineWidth',1.3, ...
    'DisplayName','enable period 1');
hold on;
stairs(sparseEnable.cycle,sparseEnablePlotOutput,'--s','LineWidth',1.3, ...
    'DisplayName','enable period 3');
hold off;
grid on;
xlabel('Clock cycle [cycles]');
ylabel('Register code Q [0..15]');
title('Changed view: disabled edges hold the stored value');
xlim([1 baseline.cycleCount]);
ylim([0 15]);
legend('Location','best');
fprintf('Enable period 3 captures %d samples and holds for %d non-reset edges.\n', ...
    sparseEnable.captureCount,sparseEnable.holdCount);

%% Explain lever 2, then break simultaneous sampling
% Mechanism first: enable changes the capture schedule, not register depth.
% Now use three stages and intentionally let Q2 reuse Q1's just-updated
% value and Q3 reuse Q2's just-updated value on the same edge. The violated
% assumption is that edge-triggered registers sample pre-edge inputs
% simultaneously. The broken output becomes valid too early.
broken = model(3,1,6,true);
fprintf(['Broken cascade: first mismatch cycle %d, %d mismatched cycles, ' ...
    '%d early-valid cycles.\n'],broken.firstMismatchCycle, ...
    broken.mismatchCount,broken.earlyValidCount);

%% Explore, check, and teach back
% Run experiment.m one section at a time for both complete sweeps and the
% broken comparison. Then use the bounded UI, run run_checks, and explain
% in two sentences what a register observes at an edge and how an enable,
% reset, or incorrect stage-transfer rule changes the stored output.
interactive;
