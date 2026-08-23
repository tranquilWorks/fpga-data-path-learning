%% P08 - Generate a Numerically Controlled Oscillator
% Run one section at a time. The 12-bit phase accumulator keeps its full
% precision. Only the lookup address discards low phase bits. Each sweep
% resets the other lever so frequency control and lookup resolution remain
% independent.
figureNames = {'P08 baseline NCO', ...
    'P08 tuning-word sweep','P08 phase-address sweep', ...
    'P08 broken increment truncation'};
for figureIndex = 1:numel(figureNames)
    delete(findall(groot,'Type','figure','Name',figureNames{figureIndex}));
end
clear model;
clc;

%% Read the governing recurrence, then establish the deterministic baseline
% Before plotting, predict whether K=411 adds 411 phase codes before or
% after the 8-bit lookup address is formed. Inspect the baseline once. Make
% no second prediction; later sections ask for observations and mechanisms.
baseline = model(411,8,0,false);
assert(all(baseline.referencePhaseStepCode == 411) && ...
    isequal(baseline.phaseCode,baseline.referencePhaseCode) && ...
    baseline.referenceWrapCount == 411 && ...
    baseline.referenceWithinRecordWrapCount == 410 && ...
    baseline.referenceTerminalNextPhaseCode == 0, ...
    'P08:BaselineRecurrence', ...
    'The healthy baseline must add the full tuning word modulo 2^12.');
assert(abs(baseline.requestedFrequencyMHz-10.0341796875) < 1e-12 && ...
    baseline.lookupEntryCount == 256 && ...
    baseline.phaseTruncationFactor == 16 && ...
    baseline.discardedTuningWordCode == 0, ...
    'P08:BaselineMetrics', ...
    'Baseline frequency, lookup size, or healthy tuning precision changed.');
fprintf(['Baseline: B=%d accumulator bits, K=%d codes/sample, ' ...
    'P=%d lookup-address bits, f_s=%g MHz (assumed), f_out=%0.9g MHz, ' ...
    'resolution=%0.9g kHz.\n'],baseline.accumulatorBits, ...
    baseline.tuningWord,baseline.phaseAddressBits,baseline.sampleClockMHz, ...
    baseline.requestedFrequencyMHz,baseline.frequencyResolutionKHz);
fprintf(['The %d stored states show %d wrap discontinuities; counting all ' ...
    '%d modeled next-state transitions, including the terminal transition ' ...
    'to sample 4096, gives %d wraps. The lookup ' ...
    'has %d phase entries, %g degree steps, %0.6g degree maximum phase ' ...
    'truncation error, and %0.6g degree RMS phase error.\n'], ...
    baseline.recordSampleCount,baseline.withinRecordWrapCount, ...
    baseline.transitionCount,baseline.wrapCount, ...
    baseline.lookupEntryCount,baseline.lookupPhaseStepDegrees, ...
    baseline.maximumPhaseTruncationErrorDegrees, ...
    baseline.phaseTruncationRmsDegrees);
fprintf('%s\n',baseline.equationText);

%% Visualize the baseline one view at a time
baselineFigure = figure('Name',figureNames{1},'NumberTitle','off');
visibleSamples = 64;
subplot(2,2,1);
stairs(baseline.sampleIndex(1:visibleSamples), ...
    baseline.phaseCode(1:visibleSamples),'LineWidth',1.2);
grid on;
xlabel('Sample [index]');
ylabel('Accumulator phase [unsigned 12-bit code]');
title('Modulo phase accumulator');
drawnow;

%% Baseline view 2 - quadrature lookup output
figure(baselineFigure);
subplot(2,2,2);
plot(baseline.sampleTimeMicroseconds(1:visibleSamples), ...
    baseline.cosineOutput(1:visibleSamples),'LineWidth',1.2, ...
    'DisplayName','Cosine');
hold on;
plot(baseline.sampleTimeMicroseconds(1:visibleSamples), ...
    baseline.sineOutput(1:visibleSamples),'--','LineWidth',1.2, ...
    'DisplayName','Sine');
hold off;
grid on;
xlabel('Time [microseconds at assumed 100 MHz]');
ylabel('Lookup output [normalized amplitude]');
title('Quadrature lookup outputs');
legend('Location','best');
drawnow;

%% Baseline view 3 - lookup phase error
figure(baselineFigure);
subplot(2,2,3);
plot(baseline.sampleIndex(1:visibleSamples), ...
    baseline.phaseTruncationErrorDegrees(1:visibleSamples), ...
    'LineWidth',1.2);
grid on;
xlabel('Sample [index]');
ylabel('Lookup phase error [degrees]');
title('Phase is truncated only at the lookup');
drawnow;

%% Baseline view 4 - coherent record spectrum
figure(baselineFigure);
subplot(2,2,4);
plot(baseline.spectrumFrequencyMHz, ...
    max(baseline.spectrumDbcCentered,-120),'LineWidth',1.0);
grid on;
xlabel('Discrete-time frequency [MHz at assumed 100 MHz]');
ylabel('Record spectrum [dBc]');
title('Deterministic 4096-sample complex-output spectrum');
xlim([-50 50]);
ylim([-120 5]);
sgtitle('P08 baseline: full-width accumulation, 8-bit phase lookup');
drawnow;

%% Sweep 1 - tuning word at a fixed 8-bit lookup address
% Lever 1 changes phase advance, output frequency, wrap count, and period.
% It must not change the accumulator width, lookup width, table size,
% initial phase, or record allocation.
tuningWords = [0 1 64 128 256 411 512 1024 2047];
observedRequestedFrequencyMHz = zeros(size(tuningWords));
observedDominantFrequencyMHz = zeros(size(tuningWords));
observedWrapCounts = zeros(size(tuningWords));
observedWithinRecordWrapCounts = zeros(size(tuningWords));
observedPhaseStepsDegrees = zeros(size(tuningWords));
observedPeriods = zeros(size(tuningWords));
for sweepIndex = 1:numel(tuningWords)
    current = model(tuningWords(sweepIndex),8,0,false);
    assert(current.phaseAddressBits == 8 && ...
        current.lookupEntryCount == 256 && ...
        current.initialPhaseCode == 0 && ...
        current.recordSampleCount == 4096 && ...
        ~current.brokenIncrementTruncation, ...
        'P08:TuningSweepIsolation', ...
        ['Tuning-word sweep must preserve lookup width, initial phase, ' ...
        'record size, and healthy mode.']);
    assert(all(current.phaseStepCode == tuningWords(sweepIndex)) && ...
        current.wrapCount == tuningWords(sweepIndex) && ...
        current.withinRecordWrapCount == ...
            max(tuningWords(sweepIndex)-1,0) && ...
        abs(current.actualFrequencyMHz- ...
            tuningWords(sweepIndex)*100/4096) < 1e-12, ...
        'P08:TuningSweep', ...
        'Frequency and wraps must follow the full tuning word.');
    observedRequestedFrequencyMHz(sweepIndex) = ...
        current.requestedFrequencyMHz;
    observedDominantFrequencyMHz(sweepIndex) = ...
        current.dominantFrequencyMHz;
    observedWrapCounts(sweepIndex) = current.wrapCount;
    observedWithinRecordWrapCounts(sweepIndex) = ...
        current.withinRecordWrapCount;
    observedPhaseStepsDegrees(sweepIndex) = current.actualPhaseStepDegrees;
    observedPeriods(sweepIndex) = current.accumulatorPeriodSamples;
end
expectedFrequenciesMHz = tuningWords*100/4096;
assert(max(abs(observedRequestedFrequencyMHz-expectedFrequenciesMHz)) < ...
        1e-12 && ...
    max(abs(observedDominantFrequencyMHz-expectedFrequenciesMHz)) < ...
        1e-12 && ...
    isequal(observedWrapCounts,tuningWords) && ...
    isequal(observedWithinRecordWrapCounts, ...
        [0 0 63 127 255 410 511 1023 2046]), ...
    'P08:TuningSweepLimits', ...
    'The tuning sweep no longer follows K*f_s/2^12.');

tuningFigure = figure('Name',figureNames{2},'NumberTitle','off');
subplot(2,2,1);
plot(tuningWords,observedRequestedFrequencyMHz,'-o','LineWidth',1.2, ...
    'DisplayName','Equation');
hold on;
plot(tuningWords,observedDominantFrequencyMHz,'--x','LineWidth',1.2, ...
    'DisplayName','Record dominant bin');
hold off;
grid on;
xlabel('Tuning word K [phase codes/sample]');
ylabel('Output frequency [MHz at assumed 100 MHz]');
title('Frequency follows the tuning word');
legend('Location','best');
drawnow;

%% Sweep 1 view 2 - full-transition wrap count
figure(tuningFigure);
subplot(2,2,2);
plot(tuningWords,observedWrapCounts,'-o','LineWidth',1.2);
grid on;
xlabel('Tuning word K [phase codes/sample]');
ylabel('Accumulator wraps [events/4096 transitions]');
title('Count includes the terminal next-state transition');
drawnow;

%% Sweep 1 view 3 - phase advance
figure(tuningFigure);
subplot(2,2,3);
plot(tuningWords,observedPhaseStepsDegrees,'-o','LineWidth',1.2);
grid on;
xlabel('Tuning word K [phase codes/sample]');
ylabel('Phase advance [degrees/sample]');
title('Phase-step mechanism');
drawnow;

%% Sweep 1 view 4 - accumulator period
figure(tuningFigure);
subplot(2,2,4);
semilogy(tuningWords,observedPeriods,'-o','LineWidth',1.2);
grid on;
xlabel('Tuning word K [phase codes/sample]');
ylabel('Accumulator period [samples]');
title('Period depends on gcd(4096,K)');
sgtitle('Sweep 1: move K while the 256-entry lookup stays fixed');
drawnow;

%% Read the first changed-view mechanism
% K is an integer phase advance, so one code changes frequency by
% f_s/2^12 = 24.4140625 kHz under the explicit 100 MHz teaching clock.
% The 8-bit lookup remains a 256-entry phase map. It shapes phase error and
% spurs, but healthy accumulation retains all 12 tuning-word bits.

%% Sweep 2 - phase-address bits at a fixed odd tuning word
% Reset K to 411. Lever 2 changes table entries and phase truncation. It
% must not change the accumulator recurrence, tuned frequency, sample clock,
% initial phase, or record allocation.
phaseAddressWidths = 3:12;
observedLookupEntries = zeros(size(phaseAddressWidths));
observedMaximumErrorDegrees = zeros(size(phaseAddressWidths));
observedRmsErrorDegrees = zeros(size(phaseAddressWidths));
observedWaveformRmsError = zeros(size(phaseAddressWidths));
observedSfdrDb = zeros(size(phaseAddressWidths));
expectedMaximumErrorDegrees = zeros(size(phaseAddressWidths));
expectedRmsErrorDegrees = zeros(size(phaseAddressWidths));
for sweepIndex = 1:numel(phaseAddressWidths)
    current = model(411,phaseAddressWidths(sweepIndex),0,false);
    assert(current.tuningWord == 411 && ...
        current.effectiveTuningWord == 411 && ...
        current.requestedFrequencyMHz == baseline.requestedFrequencyMHz && ...
        current.recordSampleCount == baseline.recordSampleCount && ...
        isequal(current.phaseCode,baseline.phaseCode), ...
        'P08:AddressSweepIsolation', ...
        ['Phase-address sweep must preserve full accumulator phase, ' ...
        'frequency, and record allocation.']);
    truncationFactor = 2^(12-phaseAddressWidths(sweepIndex));
    expectedMaximumErrorDegrees(sweepIndex) = ...
        (truncationFactor-1)*360/4096;
    expectedRmsErrorDegrees(sweepIndex) = ...
        sqrt(mean((0:truncationFactor-1).^2))*360/4096;
    observedLookupEntries(sweepIndex) = current.lookupEntryCount;
    observedMaximumErrorDegrees(sweepIndex) = ...
        current.maximumPhaseTruncationErrorDegrees;
    observedRmsErrorDegrees(sweepIndex) = ...
        current.phaseTruncationRmsDegrees;
    observedWaveformRmsError(sweepIndex) = current.waveformRmsError;
    observedSfdrDb(sweepIndex) = current.recordSfdrDb;
end
assert(isequal(observedLookupEntries,2.^phaseAddressWidths) && ...
    max(abs(observedMaximumErrorDegrees- ...
        expectedMaximumErrorDegrees)) < 1e-12 && ...
    max(abs(observedRmsErrorDegrees-expectedRmsErrorDegrees)) < 1e-12 && ...
    observedMaximumErrorDegrees(end) == 0 && ...
    observedWaveformRmsError(end) == 0 && ...
    isinf(observedSfdrDb(end)), ...
    'P08:AddressSweepLimits', ...
    'Lookup-size or full-width phase-truncation limits changed.');

addressFigure = figure('Name',figureNames{3},'NumberTitle','off');
subplot(2,2,1);
semilogy(phaseAddressWidths,observedLookupEntries,'-o','LineWidth',1.2);
grid on;
xlabel('Lookup phase-address width P [bits]');
ylabel('Sine/cosine lookup [phase entries]');
title('Each address bit doubles the phase table');
drawnow;

%% Sweep 2 view 2 - angular lookup error
figure(addressFigure);
subplot(2,2,2);
plot(phaseAddressWidths,observedMaximumErrorDegrees,'-o','LineWidth',1.2, ...
    'DisplayName','Maximum');
hold on;
plot(phaseAddressWidths,observedRmsErrorDegrees,'--s','LineWidth',1.2, ...
    'DisplayName','RMS');
hold off;
grid on;
xlabel('Lookup phase-address width P [bits]');
ylabel('Phase truncation error [degrees]');
title('More phase addresses reduce angular error');
legend('Location','best');
drawnow;

%% Sweep 2 view 3 - waveform error
figure(addressFigure);
subplot(2,2,3);
semilogy(phaseAddressWidths,max(observedWaveformRmsError,realmin), ...
    '-o','LineWidth',1.2);
grid on;
xlabel('Lookup phase-address width P [bits]');
ylabel('Complex waveform RMS error [normalized amplitude]');
title('Lookup output approaches the ideal phasor');
drawnow;

%% Sweep 2 view 4 - spectral purity above the numerical floor
figure(addressFigure);
observedSfdrForPlot = observedSfdrDb;
observedSfdrForPlot(isinf(observedSfdrForPlot)) = ...
    -baseline.spectralNumericalFloorDbc;
subplot(2,2,4);
plot(phaseAddressWidths,observedSfdrForPlot,'-o','LineWidth',1.2);
grid on;
xlabel('Lookup phase-address width P [bits]');
ylabel('Modeled SFDR/floor ceiling [dB]');
title('Inf is drawn at 240 dB: no spur resolved above -240 dBc');
sgtitle('Sweep 2: move lookup width while K=411 stays fixed');
drawnow;

%% Read the second changed-view mechanism
% P address bits select 2^P phase entries. Discarding low accumulator bits
% after accumulation introduces at most (2^(12-P)-1) accumulator codes of
% phase error. More entries improve the modeled phase waveform but do not
% improve the tuning resolution, which remains set by all 12 accumulator
% bits. Entry count is a model quantity, not a BRAM or area report.

%% Deliberately broken case - truncate K before the accumulator
% At K=411 and P=8, lookup truncation discards four phase-code bits. The
% broken controller also clears those four bits in K, turning 411 into 400.
% That violates the boundary: accumulate full precision, truncate only for
% lookup. The exact symptom is a lower tone and a shorter phase sequence.
healthy = model(411,8,0,false);
broken = model(411,8,0,true);
assert(broken.effectiveTuningWord == 400 && ...
    broken.discardedTuningWordCode == 11 && ...
    broken.faultActive && ...
    abs(broken.actualFrequencyMHz-9.765625) < 1e-12 && ...
    abs(broken.frequencyErrorKHz+268.5546875) < 1e-12 && ...
    broken.wrapCount == 400 && ...
    broken.withinRecordWrapCount == 399 && ...
    broken.accumulatorPeriodSamples == 256, ...
    'P08:BrokenFrequency', ...
    'The broken increment must create the exact lower-frequency symptom.');
assert(isequal(broken.referencePhaseCode,healthy.referencePhaseCode) && ...
    isequal(broken.referenceComplexOutput,healthy.referenceComplexOutput) && ...
    broken.lookupEntryCount == healthy.lookupEntryCount && ...
    broken.recordSampleCount == healthy.recordSampleCount, ...
    'P08:BrokenIsolation', ...
    'The fault must alter only the accumulated increment and its outputs.');

brokenFigure = figure('Name',figureNames{4},'NumberTitle','off');
subplot(2,2,1);
stairs(healthy.sampleIndex(1:visibleSamples), ...
    healthy.referencePhaseCode(1:visibleSamples),'LineWidth',1.2, ...
    'DisplayName','Required K=411');
hold on;
stairs(broken.sampleIndex(1:visibleSamples), ...
    broken.phaseCode(1:visibleSamples),'--','LineWidth',1.2, ...
    'DisplayName','Broken K=400');
hold off;
grid on;
xlabel('Sample [index]');
ylabel('Accumulator phase [unsigned 12-bit code]');
title('Phase drift after premature increment truncation');
legend('Location','best');
drawnow;

%% Broken view 2 - waveform separation
figure(brokenFigure);
subplot(2,2,2);
plot(healthy.sampleTimeMicroseconds(1:visibleSamples), ...
    healthy.referenceCosineOutput(1:visibleSamples),'LineWidth',1.2, ...
    'DisplayName','Required output');
hold on;
plot(broken.sampleTimeMicroseconds(1:visibleSamples), ...
    broken.cosineOutput(1:visibleSamples),'--','LineWidth',1.2, ...
    'DisplayName','Broken output');
hold off;
grid on;
xlabel('Time [microseconds at assumed 100 MHz]');
ylabel('Cosine output [normalized amplitude]');
title('Waveforms separate because their frequencies differ');
legend('Location','best');
drawnow;

%% Broken view 3 - carrier displacement
figure(brokenFigure);
subplot(2,2,3);
plot(healthy.spectrumFrequencyMHz, ...
    max(healthy.referenceSpectrumDbcCentered,-120),'LineWidth',1.2, ...
    'DisplayName','Required 10.0341797 MHz');
hold on;
plot(broken.spectrumFrequencyMHz, ...
    max(broken.spectrumDbcCentered,-120),'--','LineWidth',1.2, ...
    'DisplayName','Broken 9.765625 MHz');
hold off;
grid on;
xlabel('Discrete-time frequency [MHz at assumed 100 MHz]');
ylabel('Record spectrum [dBc to each carrier]');
title('Carrier moves by eleven frequency-resolution steps');
xlim([8.5 11]);
ylim([-120 5]);
legend('Location','best');
drawnow;

%% Broken view 4 - removed increment codes
figure(brokenFigure);
subplot(2,2,4);
bar(1:2,[healthy.tuningWord broken.effectiveTuningWord]);
grid on;
set(gca,'XTick',1:2,'XTickLabel',{'Required','Broken'});
xlabel('Accumulator path [case]');
ylabel('Applied increment [phase codes/sample]');
title(sprintf('Frequency error = %0.6g kHz',broken.frequencyErrorKHz));
sgtitle('Deliberately broken case: tuning precision removed too early');
drawnow;

%% Mechanism-first explanation, limits, and next step
% Healthy address truncation changes phase granularity without changing K.
% Broken increment truncation changes K itself, so f_out changes by eleven
% frequency-resolution steps. The fault is inert when K is divisible by the
% truncation factor, at K=0, or when P=12 discards no phase bits. Those inert
% limits identify the removed tuning bits as the cause. Now run run_checks.m
% and answer checks.md one prompt at a time before giving the teach-back.
