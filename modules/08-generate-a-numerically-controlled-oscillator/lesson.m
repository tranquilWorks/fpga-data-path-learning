%% P08 - Generate a Numerically Controlled Oscillator
% Guiding question:
% What inputs, observable effects, and failure modes matter when you generate a Numerically Controlled Oscillator?
clear model interactive;

%% Read - separate tuning precision from lookup precision
% P07 separated modeled resources from useful throughput. P08 makes a
% related numeric separation. A 12-bit modular accumulator keeps the full
% tuning word K, while a lookup observes only its P most-significant phase
% bits. Accumulator width sets frequency resolution; lookup width trades
% phase-table entries for phase fidelity.
disp(['Mental model: advance around a 4096-position phase clock by K ' ...
    'positions per sample, wrap modulo 4096, then use the coarse lookup ' ...
    'address to select normalized sine and cosine.']);
disp(['Prediction: at K=411 and P=8, does the accumulator advance by ' ...
    '411 codes or by 400 codes before the lookup address is formed?']);

%% Visualize the deterministic baseline
% Sample zero exposes initial phase zero. Healthy phase is
% mod(phi0+n*K,4096), so the first update appears at sample one. The
% 100 MHz sample clock is an explicit teaching assumption.
baseline = model(411,8,0,false);
visibleSamples = 64;
delete(findall(groot,'Type','figure','Name','P08 lesson baseline'));
baselineFigure = figure('Name','P08 lesson baseline');
subplot(2,1,1);
stairs(baseline.sampleIndex(1:visibleSamples), ...
    baseline.phaseCode(1:visibleSamples),'LineWidth',1.25);
grid on;
xlabel('Sample [index]');
ylabel('Accumulator phase [unsigned 12-bit code]');
title('Baseline: add all 411 tuning codes, then wrap modulo 4096');
drawnow;

%% Baseline view 2 - reveal the lookup output
figure(baselineFigure);
subplot(2,1,2);
plot(baseline.sampleTimeMicroseconds(1:visibleSamples), ...
    baseline.cosineOutput(1:visibleSamples),'-','LineWidth',1.2, ...
    'DisplayName','Cosine');
hold on;
plot(baseline.sampleTimeMicroseconds(1:visibleSamples), ...
    baseline.sineOutput(1:visibleSamples),'--','LineWidth',1.2, ...
    'DisplayName','Sine');
hold off;
grid on;
xlabel('Time [microseconds at assumed 100 MHz]');
ylabel('Lookup output [normalized amplitude]');
title('Eight phase-address bits select a quadrature lookup pair');
legend('Location','best');
fprintf(['Baseline f_out=%0.9g MHz; resolution=%0.9g kHz/code; ' ...
    'wraps=%d across %d modeled transitions, including the terminal ' ...
    'next state; stored-state discontinuities=%d/%d; lookup=%d entries; ' ...
    'max phase ' ...
    'error=%0.9g degrees.\n'],baseline.requestedFrequencyMHz, ...
    baseline.frequencyResolutionKHz,baseline.wrapCount, ...
    baseline.transitionCount,baseline.withinRecordWrapCount, ...
    baseline.withinRecordTransitionCount,baseline.lookupEntryCount, ...
    baseline.maximumPhaseTruncationErrorDegrees);
drawnow;

%% Read the baseline mechanism
% The accumulator uses K=411. Only after phase is stored does the lookup
% discard four low phase bits. A staircase in lookup phase can create
% modeled spurs without changing the healthy average phase advance or
% requested frequency.
disp(baseline.equationText);

%% Move lever 1 - change K while keeping P=8
% Compare the minimum positive frequency, the baseline, and quarter-rate.
% The table remains 256 entries while phase advance, carrier, wrap count,
% and accumulator period respond to K.
minimumStep = model(1,8,0,false);
baselineTuning = model(411,8,0,false);
quarterRate = model(1024,8,0,false);
tuningCases = [minimumStep baselineTuning quarterRate];
tuningCaseWords = [tuningCases.tuningWord];
tuningCaseFrequencies = [tuningCases.actualFrequencyMHz];
tuningCaseWraps = [tuningCases.wrapCount];
delete(findall(groot,'Type','figure','Name','P08 lesson tuning change'));
tuningFigure = figure('Name','P08 lesson tuning change');
subplot(2,1,1);
plot(tuningCaseWords,tuningCaseFrequencies,'-o','LineWidth',1.3);
grid on;
xlabel('Tuning word K [phase codes/sample]');
ylabel('Output frequency [MHz at assumed 100 MHz]');
title('Changed view: frequency follows K*f_s/4096');
drawnow;

%% Lever 1 view 2 - reveal full-transition wrap count
figure(tuningFigure);
subplot(2,1,2);
plot(tuningCaseWords,tuningCaseWraps,'-o','LineWidth',1.3);
grid on;
xlabel('Tuning word K [phase codes/sample]');
ylabel('Accumulator wraps [events/4096 transitions]');
title('Count includes the terminal next-state transition');
drawnow;

%% Explain lever 1, reset, then move lever 2
% Mechanism first: K is the integer phase advance. Reset K to odd 411 so a
% full record visits every phase code. Now compare P=3, P=8, and P=12.
% Table entries and phase error change, but the phase recurrence and tone do
% not.
coarseLookup = model(411,3,0,false);
baselineLookup = model(411,8,0,false);
fullLookup = model(411,12,0,false);
lookupCases = [coarseLookup baselineLookup fullLookup];
lookupCaseBits = [lookupCases.phaseAddressBits];
lookupCaseEntries = [lookupCases.lookupEntryCount];
lookupCaseErrors = [lookupCases.maximumPhaseTruncationErrorDegrees];
delete(findall(groot,'Type','figure','Name','P08 lesson lookup change'));
lookupFigure = figure('Name','P08 lesson lookup change');
subplot(2,1,1);
semilogy(lookupCaseBits,lookupCaseEntries,'-o','LineWidth',1.3);
grid on;
xlabel('Lookup phase-address width P [bits]');
ylabel('Lookup [phase entries]');
title('Changed resource: each phase-address bit doubles entries');
drawnow;

%% Lever 2 view 2 - reveal phase fidelity
figure(lookupFigure);
subplot(2,1,2);
plot(lookupCaseBits,lookupCaseErrors,'-o','LineWidth',1.3);
grid on;
xlabel('Lookup phase-address width P [bits]');
ylabel('Maximum phase error [degrees]');
title('Changed fidelity: full P=12 removes phase truncation');
drawnow;

%% Explain lever 2, then break the precision boundary
% Mechanism first: lookup truncation changes phase granularity after the
% accumulator; it must not change K. The deliberately broken path at
% K=411, P=8 clears K's low four bits before accumulation. Applied K becomes
% 400, moving the carrier and shortening the phase sequence.
healthy = model(411,8,0,false);
broken = model(411,8,0,true);
delete(findall(groot,'Type','figure','Name', ...
    'P08 lesson broken increment'));
brokenFigure = figure('Name','P08 lesson broken increment');
subplot(2,1,1);
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
title('Broken symptom: premature K truncation creates phase drift');
legend('Location','best');
drawnow;

%% Broken view 2 - reveal the carrier displacement
figure(brokenFigure);
subplot(2,1,2);
plot(healthy.spectrumFrequencyMHz, ...
    max(healthy.referenceSpectrumDbcCentered,-120),'LineWidth',1.2, ...
    'DisplayName','Required carrier');
hold on;
plot(broken.spectrumFrequencyMHz, ...
    max(broken.spectrumDbcCentered,-120),'--','LineWidth',1.2, ...
    'DisplayName','Broken carrier');
hold off;
grid on;
xlabel('Discrete-time frequency [MHz at assumed 100 MHz]');
ylabel('Record spectrum [dBc to each carrier]');
title('Removed tuning bits shift the carrier by eleven resolution steps');
xlim([8.5 11]);
ylim([-120 5]);
legend('Location','best');
fprintf(['Broken K required/applied=%d/%d; frequency required/actual=' ...
    '%0.9g/%0.9g MHz; error=%0.9g kHz; period required/actual=' ...
    '%d/%d samples.\n'],broken.tuningWord,broken.effectiveTuningWord, ...
    broken.requestedFrequencyMHz,broken.actualFrequencyMHz, ...
    broken.frequencyErrorKHz, ...
    broken.referenceAccumulatorPeriodSamples, ...
    broken.accumulatorPeriodSamples);
fprintf(['Record SFDR is finite only above the %g dBc numerical floor; ' ...
    'Inf means no modeled spur was resolved above it.\n'], ...
    broken.spectralNumericalFloorDbc);
drawnow;

%% Explore, check, and teach back
% Run experiment.m one section at a time for both complete sweeps. Then use
% the bounded UI, run run_checks, answer checks.md one prompt at a time, and
% give the two-sentence teach-back without explaining MATLAB syntax.
interactive;
