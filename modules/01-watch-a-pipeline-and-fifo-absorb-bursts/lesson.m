%% P01 - Watch a Pipeline and FIFO Absorb Bursts
% Guiding question:
% How do bursts, service rate, and FIFO depth determine loss and latency?
%
% Mental model:
% A streaming datapath is a production line. Bursts fill a FIFO, the service rate drains it, and finite depth turns temporary imbalance into overflow or backpressure.

%% Read the baseline lesson
disp('How do bursts, service rate, and FIFO depth determine loss and latency?');
disp('A streaming datapath is a production line. Bursts fill a FIFO, the service rate drains it, and finite depth turns temporary imbalance into overflow or backpressure.');

%% Run the deterministic experiment
experiment;

%% Open the live lever panel
% Move one control at a time and connect the visible change to the model.
interactive;
