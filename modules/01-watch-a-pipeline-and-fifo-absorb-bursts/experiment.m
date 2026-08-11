%% P01 - Watch a Pipeline and FIFO Absorb Bursts
close all; clc;

%% Baseline
out=model(0.75,0.9,32,2,400);

figure('Name','P01 baseline');
subplot(2,1,1);
stairs(out.cycles,out.occupancy,'LineWidth',1.2); hold on;
yline(out.fifoDepth,'--','FIFO depth');
grid on; xlabel('Clock cycle'); ylabel('Words');
title('FIFO occupancy converts rate imbalance into stored latency');
subplot(2,1,2);
stairs(out.cycles,out.arrivals,'DisplayName','Arrivals'); hold on;
stairs(out.cycles,out.departures,'DisplayName','Departures');
grid on; xlabel('Clock cycle'); ylabel('Words/cycle');
title('Bursty source and finite-rate sink'); legend('Location','best');

%% Sweep 1 - FIFO depth
depths=[8 32 128];
figure('Name','P01 depth sweep'); hold on; grid on;
for i=1:numel(depths)
    s=model(0.75,0.9,depths(i),2.5,400);
    plot(s.cycles,s.occupancy,'LineWidth',1.1,'DisplayName', ...
        sprintf('depth %d, drops %d',depths(i),s.dropCount));
end
xlabel('Cycle'); ylabel('Occupancy'); title('Depth buys burst tolerance, not throughput');
legend('Location','best');

%% Sweep 2 - service rate
rates=[0.65 0.9 1.2];
fprintf('Service-rate sweep:\n');
for i=1:numel(rates)
    s=model(0.75,rates(i),32,2,400);
    fprintf('  service %.2f -> max occupancy %d, drops %d\n', ...
        rates(i),s.maxOccupancy,s.dropCount);
end

%% Broken case - deep FIFO with sustained overload
broken=model(1.05,0.9,256,1,1200);
figure('Name','P01 broken case');
plot(broken.cycles,broken.occupancy,'LineWidth',1.2); hold on;
yline(broken.fifoDepth,'--'); grid on;
xlabel('Cycle'); ylabel('Occupancy');
title(sprintf('Broken belief: depth cannot fix sustained overload; drops = %d',broken.dropCount));

assert(out.maxOccupancy<=out.fifoDepth,'Occupancy cannot exceed depth.');
