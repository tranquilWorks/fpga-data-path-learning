%% P02 - Build Combinational Logic from Truth Tables
% Guiding question:
% What inputs, observable effects, and failure modes matter when you build Combinational Logic from Truth Tables?
clear model interactive;

%% Read - connect a truth table to the datapath from P01
% P01 followed words through a FIFO whose occupancy remembered earlier
% traffic. Here A, B, and C are bits in the current word. Together they form
% address 4*A + 2*B + C, and that address selects one output row. This model
% has no stored history: the current inputs alone determine Y.
disp('Mental model: the input bits form an address; one truth-table row supplies Y.');
disp('Prediction: for ABC = 011, will a 2-of-3 voter output LOW or HIGH?');

%% Visualize the deterministic baseline
baseline = model(2,0.5,3,-1);
delete(findall(groot,'Type','figure','Name','P02 lesson baseline'));
figure('Name','P02 lesson baseline');
stairs(baseline.inputAddress,double(baseline.specifiedOutput),'-o', ...
    'LineWidth',1.4);
grid on;
xlabel('Input address 4A+2B+C [unitless]');
ylabel('Logic output Y [binary]');
title('Baseline: 2-of-3 majority truth table');
xticks(0:7);
xticklabels(baseline.inputLabels);
yticks([0 1]);
ylim([-0.1 1.1]);
fprintf('ABC=011 selects address 3 and produces Y=%d.\n', ...
    baseline.selectedLutOutput);

%% Read the baseline mechanism
% For k=2, Y=(A AND B) OR (A AND C) OR (B AND C). Exhaustive row values
% [0 0 0 1 0 1 1 1] agree with that independent equation. MATLAB uses row
% index address+1, so declaring zero-based addresses prevents an off-by-one
% implementation error.
disp(baseline.equationText);

%% Move lever 1 - require all three inputs to be HIGH
% Only k changes; p stays 0.5. The logic function becomes AND, so one rather
% than four of the eight exhaustive input rows asserts Y.
strict = model(3,0.5,3,-1);
delete(findall(groot,'Type','figure','Name','P02 lesson threshold change'));
figure('Name','P02 lesson threshold change');
stairs(baseline.inputAddress,double(baseline.specifiedOutput),'-o', ...
    'LineWidth',1.3,'DisplayName','k=2 majority');
hold on;
stairs(strict.inputAddress,double(strict.specifiedOutput),'--s', ...
    'LineWidth',1.3,'DisplayName','k=3 AND');
hold off;
grid on;
xlabel('Input address 4A+2B+C [unitless]');
ylabel('Logic output Y [binary]');
title('Changed view: k changes the mapping');
xticks(0:7);
xticklabels(baseline.inputLabels);
yticks([0 1]);
ylim([-0.1 1.1]);
legend('Location','best');

%% Reset, then move lever 2 - change input occurrence probability
% Return to k=2. Changing p does not change any truth-table entry; it changes
% how often rows occur for independent inputs sharing the same HIGH probability p.
rareHigh = model(2,0.2,3,-1);
delete(findall(groot,'Type','figure','Name','P02 lesson probability change'));
figure('Name','P02 lesson probability change');
bar([baseline.specifiedHighProbability,rareHigh.specifiedHighProbability]);
grid on;
xticks([1 2]);
xticklabels({'p=0.50','p=0.20'});
ylabel('Output HIGH probability P(Y=1) [unitless]');
title('Changed view: p reweights fixed truth-table rows');
ylim([0 1]);
assert(isequal(baseline.specifiedOutput,rareHigh.specifiedOutput), ...
    'Changing p must not change the truth table.');

%% Break one named assumption
% Flip only LUT address 6 (ABC=110). The violated assumption is: every
% reachable LUT entry matches its specified truth-table row.
broken = model(2,0.5,6,6);
fprintf('Broken LUT mismatches at address %d; specified Y=%d, LUT Y=%d.\n', ...
    broken.mismatchAddresses,broken.selectedSpecifiedOutput, ...
    broken.selectedLutOutput);

%% Explore, check, and teach back
% Run experiment.m one section at a time for both complete sweeps and the
% broken-case plot. Then use the UI, run run_checks, and explain in two
% sentences how an input address selects Y and how exhaustive comparison
% exposes a wrong row.
interactive;
