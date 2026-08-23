%% P06 - Pipeline a Multiply-Accumulate
% Guiding question:
% What inputs, observable effects, and failure modes matter when you pipeline a Multiply-Accumulate?
clear model interactive;

%% Read - keep numerical meaning and cycle identity together
% P05 assigned a binary point to stored codes. P06 uses signed W=4 operand
% codes with I=1 (sign excluded) and F=2, so x_code*h_code has four
% fractional bits and an LSB of 1/16. The
% product pipeline is only the feed-forward delay before the accumulator;
% it does not split or retime the accumulator feedback path.
disp(['Mental model: each offered product has a value, token identity, and ' ...
    'valid bit. Delay all three by L product-register cycles, then add only ' ...
    'when the delayed valid bit is true.']);
disp(['Prediction: with two product stages, a product offered before edge 1 ' ...
    'updates the accumulator on which numbered edge?']);

%% Visualize the deterministic baseline
% Post-edge rows show the result just after each numbered clock edge. L=2
% means token 1 is offered before edge 1, enters the first product register
% there, and updates the accumulator after edge 3. Eight dense products
% finish at edge 10.
baseline = model(2,1,5,false);
delete(findall(groot,'Type','figure','Name','P06 lesson baseline'));
figure('Name','P06 lesson baseline');
subplot(3,1,1);
stem(baseline.cycle(baseline.inputValid), ...
    baseline.inputProductValue(baseline.inputValid),'o','LineWidth',1.2, ...
    'DisplayName','Offered product');
hold on;
stem(baseline.cycle(baseline.referenceAccumulatorValid), ...
    baseline.accumulatorProductValue(baseline.referenceAccumulatorValid), ...
    '--s','LineWidth',1.2,'DisplayName','Product at accumulator');
hold off;
grid on;
xlabel('Clock edge [cycles]');
ylabel('Product value [unitless product]');
title('Baseline data: the same eight products arrive two cycles later');
legend('Location','best');
subplot(3,1,2);
stairs(baseline.cycle,double(baseline.inputValid)+1.5,'LineWidth',1.2, ...
    'DisplayName','Input valid + 1.5');
hold on;
stairs(baseline.cycle,double(baseline.referenceAccumulatorValid),'--', ...
    'LineWidth',1.2,'DisplayName','Delayed valid');
hold off;
grid on;
xlabel('Clock edge [cycles]');
ylabel('Valid row [binary, vertically offset]');
title('Baseline control: valid follows the same product-register delay');
legend('Location','best');
subplot(3,1,3);
stairs(baseline.cycle,baseline.runningSum,'LineWidth',1.35);
grid on;
xlabel('Clock edge [cycles]');
ylabel('Running MAC result [unitless]');
title('Baseline state: product codes accumulate to -9, or -0.5625');
fprintf(['First/final accumulation edges=%d/%d; final code/value=%d/%g; ' ...
    'alignment mismatches=%d.\n'],baseline.firstReferenceAccumulationCycle, ...
    baseline.completionCycle,baseline.finalSumCode,baseline.finalSum, ...
    baseline.validDataMismatchCount);

%% Read the baseline mechanism
% Each W=4, I=1, F=2 operand contributes two fractional bits, so the product and
% accumulator code represent units of 2^-4. Register stages move the time
% at which a product becomes visible. They do not change its code, binary
% point, order, or the wide accumulator recurrence.
disp(baseline.equationText);

%% Move lever 1 - change product-register stages at fixed dense input
% Compare the direct L=0 limiting case with L=4 while keeping one offered
% product per cycle. The final sequence and value stay fixed. Four stages
% shift the whole accumulation trace four cycles and add four modeled data
% slots plus four valid bits.
direct = model(0,1,5,false);
deep = model(4,1,5,false);
delete(findall(groot,'Type','figure','Name','P06 lesson stage change'));
figure('Name','P06 lesson stage change');
stairs(direct.cycle,direct.runningSum,'LineWidth',1.35, ...
    'DisplayName','L=0 direct product path');
hold on;
stairs(deep.cycle,deep.runningSum,'--','LineWidth',1.35, ...
    'DisplayName','L=4 registered product path');
hold off;
grid on;
xlabel('Clock edge [cycles]');
ylabel('Running MAC result [unitless]');
title('Changed view: product stages shift observation time, not arithmetic');
legend('Location','best');

%% Explain lever 1, reset, then move lever 2
% Mechanism first: every added product register delays data, valid, and
% token identity by one edge. Reset to L=2. Now increase the input period
% from one to four cycles. Bubbles enter between products and emerge after
% the same two-cycle delay, so completion moves from edge 10 to edge 31.
dense = model(2,1,5,false);
sparse = model(2,4,5,false);
delete(findall(groot,'Type','figure','Name','P06 lesson period change'));
figure('Name','P06 lesson period change');
subplot(2,1,1);
stem(dense.cycle(dense.referenceAccumulatorValid), ...
    dense.accumulatorProductValue(dense.referenceAccumulatorValid),'o', ...
    'LineWidth',1.2,'DisplayName','Period 1');
hold on;
stem(sparse.cycle(sparse.referenceAccumulatorValid), ...
    sparse.accumulatorProductValue(sparse.referenceAccumulatorValid), ...
    '--s','LineWidth',1.2,'DisplayName','Period 4');
hold off;
grid on;
xlabel('Clock edge [cycles]');
ylabel('Accumulated product [unitless product]');
title('Changed data cadence: the same products are separated by bubbles');
legend('Location','best');
subplot(2,1,2);
stairs(dense.cycle,dense.runningSum,'LineWidth',1.35, ...
    'DisplayName','Period 1');
hold on;
stairs(sparse.cycle,sparse.runningSum,'--','LineWidth',1.35, ...
    'DisplayName','Period 4');
hold off;
grid on;
xlabel('Clock edge [cycles]');
ylabel('Running MAC result [unitless]');
title('Bubbles stretch elapsed cycles while the final sum remains -0.5625');
legend('Location','best');

%% Explain lever 2, then break the valid/data alignment
% Mechanism first: input period changes when tokens are offered, not their
% values or order. In the fault case L returns to two and valid/token bypass
% those registers. The labels are now untrustworthy: early valid pulses see
% empty data, six later pulses name stale products, and tail tokens 7 and 8
% arrive after broken valid has stopped.
healthy = model(2,1,5,false);
broken = model(2,1,5,true);
delete(findall(groot,'Type','figure','Name','P06 lesson broken alignment'));
figure('Name','P06 lesson broken alignment');
stairs(healthy.cycle,healthy.referenceRunningSum,'LineWidth',1.35, ...
    'DisplayName','Healthy aligned sum');
hold on;
stairs(broken.cycle,broken.runningSum,'--','LineWidth',1.35, ...
    'DisplayName','Broken bypassed-valid sum');
hold off;
grid on;
xlabel('Clock edge [cycles]');
ylabel('Running MAC result [unitless]');
title('Broken symptom: accumulation freezes before the final two products');
legend('Location','best');
fprintf(['Broken final code/value=%d/%g instead of %d/%g; dropped ' ...
    'tokens=%s, valid/data mismatch cycles=%s.\n'],broken.finalSumCode, ...
    broken.finalSum,healthy.finalSumCode,healthy.finalSum, ...
    mat2str(broken.droppedTokenIndices.'), ...
    mat2str(broken.validDataMismatchCycles.'));

%% Explore, check, and teach back
% Run experiment.m one section at a time for both independent sweeps and
% the broken comparison. Then use the bounded UI, run run_checks, and give
% the two-sentence teach-back in checks.md without explaining MATLAB syntax.
interactive;
