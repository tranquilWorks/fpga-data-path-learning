function run_checks
a=model(0.5,1.0,16,1,200);
assert(a.dropCount==0,'Underloaded nonbursty baseline should not drop.');
assert(a.maxOccupancy<=16,'FIFO occupancy exceeded depth.');
b=model(1.2,0.8,8,1,300);
assert(b.dropCount>0,'Sustained overload should drop data.');
c=model(0.8,0.8,16,3,300);
assert(c.maxOccupancy>0,'Burst case should exercise the FIFO.');
disp('P01 checks passed.');
end
