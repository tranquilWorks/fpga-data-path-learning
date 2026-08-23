function interactive
%INTERACTIVE Explore fixed-point precision, range, and overflow policy.
clear model;
modelFcn = @model;
figureName = 'P05 Fixed-Point Quantizer Explorer';
delete(findall(groot,'Type','figure','Name',figureName));

fig = uifigure('Name',figureName,'Position',[80 80 1180 760]);
gridLayout = uigridlayout(fig,[4 4]);
gridLayout.RowHeight = {62,'1x',112,124};
gridLayout.ColumnWidth = {'1x','1x','1x','1x'};

instruction = uilabel(gridLayout,'WordWrap','on', ...
    'Text',['Read the overflow-free baseline first. Change fractional or ' ...
    'integer-magnitude bits independently. Fraction bits set LSB spacing; ' ...
    'integer bits (sign excluded) set range. Reduce range to expose wrap.']);
instruction.Layout.Row = 1;
instruction.Layout.Column = [1 4];

transferAxes = uiaxes(gridLayout);
transferAxes.Layout.Row = 2;
transferAxes.Layout.Column = [1 2];
errorAxes = uiaxes(gridLayout);
errorAxes.Layout.Row = 2;
errorAxes.Layout.Column = [3 4];

fractionPanel = uipanel(gridLayout,'Title','Lever 1: fractional bits');
fractionPanel.Layout.Row = 3;
fractionPanel.Layout.Column = 1;
fractionGrid = uigridlayout(fractionPanel,[2 1]);
fractionGrid.RowHeight = {42,'1x'};
uilabel(fractionGrid,'WordWrap','on', ...
    'Text','Halves LSB spacing per added bit and increases word length.');
fractionSpinner = uispinner(fractionGrid,'Limits',[0 8], ...
    'RoundFractionalValues','on','Step',1,'Value',3, ...
    'Tooltip','Fractional bits F; LSB equals 2 raised to minus F.');

integerPanel = uipanel(gridLayout,'Title','Lever 2: integer bits');
integerPanel.Layout.Row = 3;
integerPanel.Layout.Column = 2;
integerGrid = uigridlayout(integerPanel,[2 1]);
integerGrid.RowHeight = {42,'1x'};
uilabel(integerGrid,'WordWrap','on', ...
    'Text','Expands signed range; excludes the always-present sign bit.');
integerSpinner = uispinner(integerGrid,'Limits',[0 4], ...
    'RoundFractionalValues','on','Step',1,'Value',2, ...
    'Tooltip','Integer-magnitude bits I, excluding the sign bit.');

samplePanel = uipanel(gridLayout,'Title','Inspect one sample');
samplePanel.Layout.Row = 3;
samplePanel.Layout.Column = 3;
sampleGrid = uigridlayout(samplePanel,[2 1]);
sampleGrid.RowHeight = {42,'1x'};
uilabel(sampleGrid,'WordWrap','on', ...
    'Text','Selects one fixed input without changing the vector.');
sampleSpinner = uispinner(sampleGrid,'Limits',[1 25], ...
    'RoundFractionalValues','on','Step',1,'Value',16, ...
    'Tooltip','Deterministic sample index from 1 through 25.');

faultPanel = uipanel(gridLayout,'Title','Deliberately broken case');
faultPanel.Layout.Row = 3;
faultPanel.Layout.Column = 4;
faultGrid = uigridlayout(faultPanel,[2 1]);
faultGrid.RowHeight = {50,'1x'};
uilabel(faultGrid,'WordWrap','on', ...
    'Text','Enabled only when at least one rounded code overflows.');
faultCheckbox = uicheckbox(faultGrid, ...
    'Text','Wrap instead of saturate','Value',false,'Enable','off', ...
    'Tooltip','Violates the declared saturating-overflow contract.');

summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 4;
summary.Layout.Column = [1 4];

fractionSpinner.ValueChangedFcn = @(~,~) updatePlots();
integerSpinner.ValueChangedFcn = @(~,~) updatePlots();
sampleSpinner.ValueChangedFcn = @(~,~) updatePlots();
faultCheckbox.ValueChangedFcn = @(~,~) updatePlots();
updatePlots();

    function updatePlots
        fractionBits = round(fractionSpinner.Value);
        integerBits = round(integerSpinner.Value);
        selectedSample = round(sampleSpinner.Value);
        healthy = modelFcn(fractionBits,integerBits,selectedSample,false);
        if healthy.overflowCount == 0
            faultCheckbox.Value = false;
            faultCheckbox.Enable = 'off';
        else
            faultCheckbox.Enable = 'on';
        end
        brokenWrap = faultCheckbox.Value;
        out = modelFcn(fractionBits,integerBits,selectedSample,brokenWrap);

        cla(transferAxes);
        plot(transferAxes,out.inputSignal,out.inputSignal,':', ...
            'LineWidth',1.1,'DisplayName','Ideal y=x');
        hold(transferAxes,'on');
        plot(transferAxes,out.inputSignal,out.referenceSignal,'o', ...
            'LineStyle','none','LineWidth',1.35, ...
            'DisplayName','Declared saturation samples');
        if out.brokenWrap
            plot(transferAxes,out.inputSignal,out.quantizedSignal,'s', ...
                'LineStyle','none','LineWidth',1.35, ...
                'DisplayName','Broken wrap samples');
        end
        selectedColor = [0.00 0.45 0.74];
        if out.selectedMismatch
            selectedColor = [0.85 0.10 0.10];
        end
        scatter(transferAxes,out.selectedInput,out.selectedOutput,85, ...
            selectedColor,'filled','DisplayName','Selected output');
        if out.mismatchCount > 0
            scatter(transferAxes,out.inputSignal(out.mismatchMask), ...
                out.quantizedSignal(out.mismatchMask),65,[0.85 0.10 0.10], ...
                'filled','DisplayName','Overflow-policy mismatch');
        end
        hold(transferAxes,'off');
        grid(transferAxes,'on');
        xlabel(transferAxes,'Input sample amplitude [unitless]');
        ylabel(transferAxes,'Quantized output amplitude [unitless]');
        title(transferAxes,'Discrete sample mapping and endpoint policy');
        legend(transferAxes,'Location','best');

        cla(errorAxes);
        stem(errorAxes,out.sampleIndex,out.referenceError,'filled', ...
            'LineWidth',1.1,'DisplayName','Saturation-reference error');
        hold(errorAxes,'on');
        if out.brokenWrap
            stem(errorAxes,out.sampleIndex,out.quantizationError,'--', ...
                'LineWidth',1.1,'DisplayName','Broken wrapped error');
        end
        plot(errorAxes,out.sampleIndex,repmat(out.halfLsb,out.sampleCount,1), ...
            ':','LineWidth',1.1,'DisplayName','+ half LSB');
        plot(errorAxes,out.sampleIndex,repmat(-out.halfLsb,out.sampleCount,1), ...
            ':','LineWidth',1.1,'DisplayName','- half LSB');
        scatter(errorAxes,out.selectedSample,out.selectedError,85, ...
            selectedColor,'filled','DisplayName','Selected error');
        hold(errorAxes,'off');
        grid(errorAxes,'on');
        xlabel(errorAxes,'Deterministic sample index [samples]');
        ylabel(errorAxes,'Output error [unitless]');
        title(errorAxes,'In-range bound, saturation, and wrap symptom');
        errorAxes.XLim = [1 out.sampleCount];
        legend(errorAxes,'Location','best');

        health = 'matches the declared saturation reference';
        if out.selectedMismatch
            health = 'MISMATCHES saturation because overflow wrapped';
        end
        summary.Text = sprintf([ ...
            'Sample %d: x=%g, x/LSB=%g, rounded code=%d, code/output=%d/%g, ' ...
            'error=%g, overflow=%d; %s. Format: sign + I=%d + F=%d gives ' ...
            'W=%d bits, LSB=%g, range=[%g,%g], %d codes. ' ...
            'Overloads=%d, mismatches=%d, direction reversals=%d; ' ...
            'in-range max/RMS error=%g/%g. %s'], ...
            out.selectedSample,out.selectedInput,out.selectedScaledInput, ...
            out.selectedRoundedCode,out.selectedCode,out.selectedOutput, ...
            out.selectedError,out.selectedOverflow,health,out.integerBits, ...
            out.fractionBits,out.wordLength,out.lsb,out.rangeMinimum, ...
            out.rangeMaximum,out.modeledCodeCount,out.overflowCount, ...
            out.mismatchCount,out.directionReversalCount, ...
            out.maxInRangeAbsError,out.rmsInRangeError,out.equationText);
        drawnow;
    end
end
