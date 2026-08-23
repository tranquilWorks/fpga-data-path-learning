function run_checks
%RUN_CHECKS Execute independent P02 truth-table and boundary checks.
clear model;

%% Baseline truth table and independent equation
expectedMajority = logical([0 0 0 1 0 1 1 1]).';
baseline = model(2,0.5,3,-1);
assert(isequal(baseline.specifiedOutput,expectedMajority), ...
    'P02:BaselineVector','The 2-of-3 truth vector is incorrect.');
assert(isequal(baseline.lutOutput,expectedMajority), ...
    'P02:HealthyLut','The healthy LUT must copy every specified row.');
assert(isequal(baseline.equationOutput,expectedMajority), ...
    'P02:IndependentEquation','The pairwise majority equation disagrees.');
assert(baseline.mismatchCount == 0, ...
    'P02:HealthyMismatch','A healthy LUT must have no mismatches.');
assert(baseline.assertedRowCount == 4 && ...
    abs(baseline.assertedRowFraction-0.5) < 1e-12, ...
    'P02:BaselineCount','Majority must assert four of eight rows.');

%% Address convention, binary bounds, and fixed resource size
expectedBits = logical([0 0 0; 0 0 1; 0 1 0; 0 1 1; ...
    1 0 0; 1 0 1; 1 1 0; 1 1 1]);
assert(isequal(baseline.inputAddress,(0:7).'), ...
    'P02:AddressOrder','Addresses must be exhaustive and zero based.');
assert(isequal(baseline.inputBits,expectedBits), ...
    'P02:BitOrder','A must be the MSB and C the LSB.');
assert(isequal(size(baseline.truthTable),[8 8]), ...
    'P02:ResourceBound','The model must remain an eight-row fixed table.');
assert(all(baseline.specifiedOutput == 0 | baseline.specifiedOutput == 1), ...
    'P02:BinaryOutput','Every output must be binary.');
selected = model(2,0.5,5,-1);
assert(isequal(selected.selectedBits,logical([1 0 1])) && ...
    selected.selectedSpecifiedOutput == 1, ...
    'P02:SelectedRow','Address 5 must map to ABC=101 and Y=1.');

%% Sweep 1 limiting cases - OR, majority, AND
orCase = model(1,0.5,0,-1);
andCase = model(3,0.5,7,-1);
assert(isequal(orCase.specifiedOutput,logical([0 1 1 1 1 1 1 1]).'), ...
    'P02:OrLimit','k=1 must implement three-input OR.');
assert(isequal(andCase.specifiedOutput,logical([0 0 0 0 0 0 0 1]).'), ...
    'P02:AndLimit','k=3 must implement three-input AND.');
assert(isequal([orCase.assertedRowCount,baseline.assertedRowCount, ...
    andCase.assertedRowCount],[7 4 1]), ...
    'P02:ThresholdSweep','Threshold sweep counts must be [7 4 1].');
assert(isequal(flipud(baseline.specifiedOutput),~baseline.specifiedOutput), ...
    'P02:ComplementSymmetry','Majority must preserve complement symmetry.');

%% Sweep 2 limits and independent probability equation
probabilities = [0 0.25 0.5 0.75 1];
for probabilityIndex = 1:numel(probabilities)
    p = probabilities(probabilityIndex);
    current = model(2,p,3,-1);
    independentProbability = 3*p^2 - 2*p^3;
    assert(abs(sum(current.rowProbability)-1) < 1e-12, ...
        'P02:ProbabilityMass','Truth-table row probabilities must sum to one.');
    assert(abs(current.specifiedHighProbability-independentProbability) < 1e-12, ...
        'P02:ProbabilityEquation','Weighted rows disagree with 3p^2-2p^3.');
    assert(isequal(current.specifiedOutput,expectedMajority), ...
        'P02:ProbabilityIsolation','Changing p must not change the mapping.');
end
zeroProbability = model(2,0,3,-1);
oneProbability = model(2,1,3,-1);
assert(zeroProbability.specifiedHighProbability == 0, ...
    'P02:ProbabilityZeroLimit','p=0 must make Y always LOW.');
assert(oneProbability.specifiedHighProbability == 1, ...
    'P02:ProbabilityOneLimit','p=1 must make Y always HIGH.');

%% Deliberately broken LUT row and recognizable symptom
faultProbability = 0.5;
broken = model(2,faultProbability,6,6);
assert(broken.mismatchCount == 1 && ...
    isequal(broken.mismatchAddresses,6), ...
    'P02:BrokenIsolation','The broken case must isolate only address 6.');
assert(broken.selectedSpecifiedOutput == 1 && broken.selectedLutOutput == 0, ...
    'P02:BrokenSymptom','The flipped 110 row must change HIGH to LOW.');
assert(abs(broken.mismatchProbability- ...
    faultProbability^2*(1-faultProbability)) < 1e-12, ...
    'P02:BrokenProbability','The address-6 error probability must be p^2(1-p).');

%% Malformed inputs, recovery, determinism, and call isolation
assertRejects(@() model(0,0.5,3,-1),'P02:InvalidRequiredHigh');
assertRejects(@() model([1 2],0.5,3,-1),'P02:InvalidRequiredHigh');
assertRejects(@() model(2,NaN,3,-1),'P02:InvalidInputHighProbability');
assertRejects(@() model(2,Inf,3,-1),'P02:InvalidInputHighProbability');
assertRejects(@() model(2,0.5+1i,3,-1),'P02:InvalidInputHighProbability');
assertRejects(@() model(2,1.01,3,-1),'P02:InvalidInputHighProbability');
assertRejects(@() model(2,0.5,2.5,-1),'P02:InvalidSelectedAddress');
assertRejects(@() model(2,0.5,3,8),'P02:InvalidFaultAddress');
baselineAfterFailure = model(2,0.5,3,-1);
differentConfiguration = model(1,0.2,7,0); %#ok<NASGU>
baselineAfterOtherCall = model(2,0.5,3,-1);
assert(isequaln(baseline,baselineAfterFailure) && ...
    isequaln(baseline,baselineAfterOtherCall), ...
    'P02:DeterminismRecovery', ...
    'Valid output must recover unchanged after failures and other calls.');

disp('P02 checks passed: truth table, sweeps, limits, fault, validation, and recovery.');
end

function assertRejects(thunk,expectedIdentifier)
rejectedAsExpected = false;
try
    thunk();
catch exception
    rejectedAsExpected = strcmp(exception.identifier,expectedIdentifier);
end
assert(rejectedAsExpected,'P02:MalformedInputAccepted', ...
    'Expected malformed input to raise %s.',expectedIdentifier);
end
