%% P05 - Quantize Arithmetic into Fixed Point
% Run one section at a time. Every sweep resets to a named format and
% changes only one bit-allocation parameter.
figureNames = {'P05 baseline fixed point','P05 fractional-bit sweep', ...
    'P05 integer-bit sweep','P05 broken overflow wrap'};
for figureIndex = 1:numel(figureNames)
    delete(findall(groot,'Type','figure','Name',figureNames{figureIndex}));
end
clear model;
clc;

%% Baseline - nearest rounding without overload
% One sign bit, two integer-magnitude bits, and three fractional bits make a
% six-bit format. Delta is 0.125 and the two's-complement range is
% [-4, 3.875]. Every fixed input fits, so the visible error isolates
% round-to-nearest quantization before the range sweep introduces overload.
baseline = model(3,2,16,false);
fprintf(['Baseline: W=%d bits (sign + %d integer + %d fractional), ' ...
    'LSB=%g, range=[%g, %g], overloads=%d, in-range RMS error=%g.\n'], ...
    baseline.wordLength,baseline.integerBits,baseline.fractionBits, ...
    baseline.lsb,baseline.rangeMinimum,baseline.rangeMaximum, ...
    baseline.overflowCount,baseline.rmsInRangeError);
fprintf(['Selected sample %d: input=%g, rounded code=%d, output=%g, ' ...
    'error=%g, overflow=%d under policy "%s".\n'], ...
    baseline.selectedSample,baseline.selectedInput, ...
    baseline.selectedRoundedCode,baseline.selectedOutput, ...
    baseline.selectedError,baseline.selectedOverflow, ...
    baseline.overflowPolicy);

figure('Name',figureNames{1});
subplot(2,1,1);
plot(baseline.inputSignal,baseline.inputSignal,':','LineWidth',1.1, ...
    'DisplayName','Ideal y=x');
hold on;
plot(baseline.inputSignal,baseline.quantizedSignal,'o', ...
    'LineStyle','none','LineWidth',1.35, ...
    'DisplayName','Rounded sample mapping');
hold off;
grid on;
xlabel('Input sample amplitude [unitless]');
ylabel('Quantized output amplitude [unitless]');
title('Baseline mapping: discrete samples land on representable codes');
legend('Location','best');

subplot(2,1,2);
stem(baseline.sampleIndex,baseline.quantizationError,'filled', ...
    'LineWidth',1.1,'DisplayName','Output - input');
hold on;
plot(baseline.sampleIndex,repmat(baseline.halfLsb,baseline.sampleCount,1), ...
    '--','LineWidth',1.1,'DisplayName','+ half LSB');
plot(baseline.sampleIndex,repmat(-baseline.halfLsb,baseline.sampleCount,1), ...
    '--','LineWidth',1.1,'DisplayName','- half LSB');
hold off;
grid on;
xlabel('Deterministic sample index [samples]');
ylabel('Quantization error [unitless]');
title('Overflow-free baseline errors remain inside half-LSB rails');
legend('Location','best');

%% Sweep 1 - change only fractional bits
% Hold integer-magnitude bits at two, which gives enough range for every
% fixed input even at F=0. Each added fractional bit halves the LSB and
% half-LSB error bound while adding one bit to the word.
fractionalBitCounts = 0:8;
precisionLsbs = zeros(size(fractionalBitCounts));
precisionRmsErrors = zeros(size(fractionalBitCounts));
precisionMaxErrors = zeros(size(fractionalBitCounts));
precisionWordLengths = zeros(size(fractionalBitCounts));
precisionReference = model(0,2,13,false);
fixedPrecisionInput = precisionReference.inputSignal;
fprintf('\nSweep 1 - fractional bits (integer-magnitude bits fixed at 2):\n');
for sweepIndex = 1:numel(fractionalBitCounts)
    current = model(fractionalBitCounts(sweepIndex),2,13,false);
    precisionLsbs(sweepIndex) = current.lsb;
    precisionRmsErrors(sweepIndex) = current.rmsInRangeError;
    precisionMaxErrors(sweepIndex) = current.maxInRangeAbsError;
    precisionWordLengths(sweepIndex) = current.wordLength;
    assert(current.integerBits == 2 && current.overflowCount == 0 && ...
        isequal(current.inputSignal,fixedPrecisionInput), ...
        'Fractional-bit sweep must preserve range allocation and inputs.');
    fprintf(['  F=%d -> W=%d bits, LSB=%g, max/RMS error=%g/%g, ' ...
        'overloads=%d\n'],current.fractionBits,current.wordLength, ...
        current.lsb,current.maxInRangeAbsError,current.rmsInRangeError, ...
        current.overflowCount);
end

figure('Name',figureNames{2});
subplot(2,1,1);
semilogy(fractionalBitCounts,precisionLsbs,'-o','LineWidth',1.35, ...
    'DisplayName','LSB weight');
hold on;
semilogy(fractionalBitCounts,precisionMaxErrors,'--s', ...
    'LineWidth',1.35,'DisplayName','Observed max |error|');
semilogy(fractionalBitCounts,precisionRmsErrors,':d', ...
    'LineWidth',1.35,'DisplayName','Observed RMS error');
hold off;
grid on;
xlabel('Fractional bits F [bits]');
ylabel('Step or error magnitude [unitless]');
title('Sweep 1: fractional bits refine in-range code spacing');
xticks(fractionalBitCounts);
legend('Location','best');

subplot(2,1,2);
plot(fractionalBitCounts,precisionWordLengths,'-o','LineWidth',1.35);
grid on;
xlabel('Fractional bits F [bits]');
ylabel('Modeled word length W [bits]');
title('One sign + two integer-magnitude bits + F fractional bits');
xticks(fractionalBitCounts);

%% Sweep 2 - reset, then change only integer-magnitude bits
% Return to F=3, fixing Delta at 0.125. Expanding I changes endpoint range
% and overload count, but it cannot refine the in-range code spacing.
integerBitCounts = 0:4;
rangeMinimums = zeros(size(integerBitCounts));
rangeMaximums = zeros(size(integerBitCounts));
rangeOverloadCounts = zeros(size(integerBitCounts));
rangeRmsErrors = zeros(size(integerBitCounts));
rangeReference = model(3,0,13,false);
fixedRangeInput = rangeReference.inputSignal;
fixedRangeLsb = rangeReference.lsb;
fprintf('\nSweep 2 - integer-magnitude bits (fractional bits fixed at 3):\n');
for sweepIndex = 1:numel(integerBitCounts)
    current = model(3,integerBitCounts(sweepIndex),13,false);
    rangeMinimums(sweepIndex) = current.rangeMinimum;
    rangeMaximums(sweepIndex) = current.rangeMaximum;
    rangeOverloadCounts(sweepIndex) = current.overflowCount;
    rangeRmsErrors(sweepIndex) = current.overallRmsError;
    assert(current.fractionBits == 3 && current.lsb == fixedRangeLsb && ...
        isequal(current.inputSignal,fixedRangeInput), ...
        'Integer-bit sweep must preserve fractional precision and inputs.');
    fprintf(['  I=%d -> range=[%g, %g], LSB=%g, overloads=%d, ' ...
        'overall RMS error=%g\n'],current.integerBits, ...
        current.rangeMinimum,current.rangeMaximum,current.lsb, ...
        current.overflowCount,current.overallRmsError);
end

figure('Name',figureNames{3});
subplot(2,1,1);
plot(integerBitCounts,rangeMinimums,'-o','LineWidth',1.35, ...
    'DisplayName','Minimum');
hold on;
plot(integerBitCounts,rangeMaximums,'--s','LineWidth',1.35, ...
    'DisplayName','Maximum');
hold off;
grid on;
xlabel('Integer-magnitude bits I [bits, sign excluded]');
ylabel('Representable endpoint [unitless]');
title('Sweep 2: integer bits expand range at fixed LSB');
xticks(integerBitCounts);
legend('Location','best');

subplot(2,1,2);
bar(integerBitCounts,rangeOverloadCounts);
grid on;
xlabel('Integer-magnitude bits I [bits, sign excluded]');
ylabel('Overflowed sample count [samples]');
title('Overload disappears once the deterministic vector fits');
xticks(integerBitCounts);

%% Deliberately broken case - wrap instead of declared saturation
% Named violated assumption: overflow must saturate at the nearest endpoint.
% The broken path discards high-order overflow information modulo 32 codes.
% At the deliberately narrowed I=1, F=3 format, all five overloads wrap
% across zero and reverse
% direction instead of remaining pinned to the appropriate endpoint.
healthy = model(3,1,25,false);
broken = model(3,1,25,true);
assert(broken.mismatchCount == healthy.overflowCount && ...
    broken.directionReversalCount == healthy.overflowCount, ...
    'Every narrowed-format overload should expose one wrapped direction reversal.');
fprintf(['\nDeliberately broken wrap: %d saturation-reference mismatches, ' ...
    '%d opposite-sign outputs; selected input %g maps to %g instead of %g.\n'], ...
    broken.mismatchCount,broken.directionReversalCount,broken.selectedInput, ...
    broken.selectedOutput,broken.selectedReferenceOutput);

figure('Name',figureNames{4});
subplot(2,1,1);
plot(healthy.inputSignal,healthy.inputSignal,':','LineWidth',1.1, ...
    'DisplayName','Ideal y=x');
hold on;
plot(healthy.inputSignal,healthy.quantizedSignal,'o', ...
    'LineStyle','none','LineWidth',1.35, ...
    'DisplayName','Declared saturation samples');
plot(broken.inputSignal,broken.quantizedSignal,'s', ...
    'LineStyle','none','LineWidth',1.35, ...
    'DisplayName','Broken wrap samples');
scatter(broken.inputSignal(broken.mismatchMask), ...
    broken.quantizedSignal(broken.mismatchMask),65,[0.85 0.10 0.10], ...
    'filled','DisplayName','Wrapped overload');
hold off;
grid on;
xlabel('Input sample amplitude [unitless]');
ylabel('Quantized output amplitude [unitless]');
title('Broken sample mapping: overflow wraps across the code interval');
legend('Location','best');

subplot(2,1,2);
stem(healthy.sampleIndex,healthy.referenceError,'filled', ...
    'LineWidth',1.1,'DisplayName','Saturation error');
hold on;
stem(broken.sampleIndex,broken.quantizationError,'--', ...
    'LineWidth',1.1,'DisplayName','Wrapped error');
scatter(broken.mismatchSamples, ...
    broken.quantizationError(broken.mismatchMask),65,[0.85 0.10 0.10], ...
    'filled','DisplayName','Policy mismatch');
hold off;
grid on;
xlabel('Deterministic sample index [samples]');
ylabel('Output error [unitless]');
title('Wrapped overload produces large opposite-direction errors');
legend('Location','best');

%% Explain and check
% Fractional bits set the code spacing; integer-magnitude bits set range.
% Rounding error is half-LSB bounded only before overflow. Saturation and
% wrap are different declared policies, not two names for quantization noise.
disp(baseline.equationText);
disp('Run run_checks, then answer checks.md one prompt at a time.');
