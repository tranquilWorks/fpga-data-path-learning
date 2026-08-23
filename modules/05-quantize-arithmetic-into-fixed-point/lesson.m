%% P05 - Quantize Arithmetic into Fixed Point
% Guiding question:
% What inputs, observable effects, and failure modes matter when you quantize Arithmetic into Fixed Point?
clear model interactive;

%% Read - give finite codes numerical weights
% P04 used finite registered codes as symbolic state labels. Here adjacent
% signed codes differ by Delta = 2^-F. One sign bit, I integer-magnitude
% bits, and F fractional bits make W = 1 + I + F total bits.
disp(['Mental model: round x/Delta to the nearest signed code, then ' ...
    'apply the declared saturation policy before multiplying by Delta.']);
disp(['Prediction: with I=2, F=3, and LSB 0.125, what nearest ' ...
    'output should input 0.31 produce?']);

%% Visualize the deterministic baseline
baseline = model(3,2,16,false);
delete(findall(groot,'Type','figure','Name','P05 lesson baseline'));
figure('Name','P05 lesson baseline');
subplot(2,1,1);
plot(baseline.inputSignal,baseline.inputSignal,':','LineWidth',1.1, ...
    'DisplayName','Ideal y=x');
hold on;
plot(baseline.inputSignal,baseline.quantizedSignal,'o', ...
    'LineStyle','none','LineWidth',1.35, ...
    'DisplayName','Nearest-rounded samples');
hold off;
grid on;
xlabel('Input sample amplitude [unitless]');
ylabel('Quantized output amplitude [unitless]');
title('Baseline: discrete samples map to nearest representable codes');
legend('Location','best');
subplot(2,1,2);
stem(baseline.sampleIndex,baseline.quantizationError,'filled', ...
    'LineWidth',1.1);
hold on;
plot(baseline.sampleIndex,repmat(baseline.halfLsb,baseline.sampleCount,1), ...
    '--','LineWidth',1.1);
plot(baseline.sampleIndex,repmat(-baseline.halfLsb,baseline.sampleCount,1), ...
    '--','LineWidth',1.1);
hold off;
grid on;
xlabel('Deterministic sample index [samples]');
ylabel('Quantization error [unitless]');
title('Every baseline error stays inside the half-LSB bound');
fprintf(['Selected input %g -> code %d -> output %g; ' ...
    'baseline overload count=%d.\n'],baseline.selectedInput, ...
    baseline.selectedCode,baseline.selectedOutput,baseline.overflowCount);

%% Read the baseline mechanism
% Rounding produces integer code c. Saturation would clamp c to [-32,31]
% for this six-bit format, but no baseline code reaches either rail.
% Negative full scale is -4, while positive full scale is one LSB lower at
% 3.875 because two's-complement codes are asymmetric.
disp(baseline.equationText);

%% Move lever 1 - add fractional precision with range held sufficient
% Establish I=2 so every input fits, then change only F from 1 to 5.
% Delta falls from 0.5 to 0.03125 and W grows from 4 to 8 bits.
coarsePrecision = model(1,2,13,false);
finePrecision = model(5,2,13,false);
delete(findall(groot,'Type','figure','Name','P05 lesson precision change'));
figure('Name','P05 lesson precision change');
stem(coarsePrecision.sampleIndex,coarsePrecision.quantizationError,'filled', ...
    'LineWidth',1.1,'DisplayName','F=1, LSB=0.5');
hold on;
stem(finePrecision.sampleIndex,finePrecision.quantizationError,'--', ...
    'LineWidth',1.1,'DisplayName','F=5, LSB=0.03125');
hold off;
grid on;
xlabel('Deterministic sample index [samples]');
ylabel('In-range quantization error [unitless]');
title('Changed view: fractional bits tighten code spacing');
legend('Location','best');

%% Explain lever 1, reset, then move lever 2
% Mechanism first: each added fractional bit halves Delta and the maximum
% nearest-rounding error, but adds one total word bit here. Reset to F=3,
% then change only I from 0 to 2. Delta remains 0.125 while endpoint range
% expands enough to remove all overloads.
narrowRange = model(3,0,13,false);
wideRange = model(3,2,13,false);
delete(findall(groot,'Type','figure','Name','P05 lesson range change'));
figure('Name','P05 lesson range change');
plot(narrowRange.inputSignal,narrowRange.quantizedSignal,'o', ...
    'LineStyle','none','LineWidth',1.35, ...
    'DisplayName','I=0: [-1, 0.875]');
hold on;
plot(wideRange.inputSignal,wideRange.quantizedSignal,'s', ...
    'LineStyle','none','LineWidth',1.35, ...
    'DisplayName','I=2: [-4, 3.875]');
plot(wideRange.inputSignal,wideRange.inputSignal,':','LineWidth',1.1, ...
    'DisplayName','Ideal y=x');
hold off;
grid on;
xlabel('Input sample amplitude [unitless]');
ylabel('Quantized output amplitude [unitless]');
title('Changed sample mapping: integer bits expand range at fixed LSB');
legend('Location','best');

%% Explain lever 2, then break the overflow policy
% Mechanism first: integer-magnitude bits add endpoint codes outside the old
% range; they do not refine the fixed 0.125 LSB. Narrow to I=1, F=3 for the
% fault case. The declared policy saturates overload. The broken path wraps modulo 32
% codes, so five overloads jump across zero and reverse direction.
healthy = model(3,1,25,false);
broken = model(3,1,25,true);
fprintf(['Broken wrap: input %g maps to %g instead of saturated %g; ' ...
    'mismatches=%d, direction reversals=%d.\n'],broken.selectedInput, ...
    broken.selectedOutput,broken.selectedReferenceOutput, ...
    broken.mismatchCount,broken.directionReversalCount);

%% Explore, check, and teach back
% Run experiment.m one section at a time for both independent sweeps and
% the broken comparison. Then use the bounded UI, run run_checks, and give
% the two-sentence teach-back in checks.md without explaining MATLAB syntax.
interactive;
