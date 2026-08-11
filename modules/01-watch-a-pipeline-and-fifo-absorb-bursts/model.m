function out = model(arrivalRate,serviceRate,fifoDepth,burstFactor,cycles)
%MODEL Discrete streaming FIFO with deterministic burst modulation.
arguments
    arrivalRate (1,1) double {mustBeNonnegative} = 0.75
    serviceRate (1,1) double {mustBeNonnegative} = 0.9
    fifoDepth (1,1) double {mustBeInteger,mustBePositive} = 32
    burstFactor (1,1) double {mustBeGreaterThanOrEqual(burstFactor,1)} = 2
    cycles (1,1) double {mustBeInteger,mustBePositive} = 400
end
occ = zeros(1,cycles);
drops = zeros(1,cycles);
arrivals = zeros(1,cycles);
departures = zeros(1,cycles);
arrivalAcc = 0; serviceAcc = 0; q = 0; dropped = 0;
for n = 1:cycles
    burst = 1 + (burstFactor-1)*(sin(2*pi*n/80) > 0);
    arrivalAcc = arrivalAcc + arrivalRate*burst;
    a = floor(arrivalAcc); arrivalAcc = arrivalAcc-a;
    serviceAcc = serviceAcc + serviceRate;
    s = floor(serviceAcc); serviceAcc = serviceAcc-s;
    accepted = min(a,max(0,fifoDepth-q));
    dropped = dropped + (a-accepted);
    q = q + accepted;
    d = min(s,q);
    q = q-d;
    arrivals(n)=a; departures(n)=d; occ(n)=q; drops(n)=dropped;
end
out=struct('cycles',1:cycles,'occupancy',occ,'drops',drops, ...
    'arrivals',arrivals,'departures',departures,'dropCount',dropped, ...
    'maxOccupancy',max(occ),'meanOccupancy',mean(occ), ...
    'estimatedLatencyCycles',mean(occ)/max(serviceRate,eps), ...
    'arrivalRate',arrivalRate,'serviceRate',serviceRate,'fifoDepth',fifoDepth);
end
