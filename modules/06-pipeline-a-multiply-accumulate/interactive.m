function interactive
%INTERACTIVE Explore product latency, bubbles, and valid/data alignment.
clear model;
modelFcn = @model;
figureName = 'P06 Multiply-Accumulate Pipeline Explorer';
delete(findall(groot,'Type','figure','Name',figureName));

fig = uifigure('Name',figureName,'Position',[80 80 1200 760]);
gridLayout = uigridlayout(fig,[4 4]);
gridLayout.RowHeight = {64,'1x',116,136};
gridLayout.ColumnWidth = {'1x','1x','1x','1x'};

instruction = uilabel(gridLayout,'WordWrap','on', ...
    'Text',['Read the two-stage baseline first. Change pipeline stages or ' ...
    'input period independently. Stages delay product and valid together; ' ...
    'input period inserts bubbles. Then bypass the valid delay to break ' ...
    'the alignment contract.']);
instruction.Layout.Row = 1;
instruction.Layout.Column = [1 4];

scheduleAxes = uiaxes(gridLayout);
scheduleAxes.Layout.Row = 2;
scheduleAxes.Layout.Column = [1 2];
sumAxes = uiaxes(gridLayout);
sumAxes.Layout.Row = 2;
sumAxes.Layout.Column = [3 4];

stagePanel = uipanel(gridLayout,'Title','Lever 1: product pipeline stages');
stagePanel.Layout.Row = 3;
stagePanel.Layout.Column = 1;
stageGrid = uigridlayout(stagePanel,[2 1]);
stageGrid.RowHeight = {46,'1x'};
uilabel(stageGrid,'WordWrap','on', ...
    'Text','Adds cycle latency and modeled storage without changing products.');
stageSpinner = uispinner(stageGrid,'Limits',[0 4], ...
    'RoundFractionalValues','on','Step',1,'Value',2, ...
    'Tooltip','Registered product stages L; zero is the direct limiting case.');

periodPanel = uipanel(gridLayout,'Title','Lever 2: input period');
periodPanel.Layout.Row = 3;
periodPanel.Layout.Column = 2;
periodGrid = uigridlayout(periodPanel,[2 1]);
periodGrid.RowHeight = {46,'1x'};
uilabel(periodGrid,'WordWrap','on', ...
    'Text','Inserts bubbles while preserving token order and final sum.');
periodSpinner = uispinner(periodGrid,'Limits',[1 4], ...
    'RoundFractionalValues','on','Step',1,'Value',1, ...
    'Tooltip','Clock cycles between offered product tokens.');

cyclePanel = uipanel(gridLayout,'Title','Inspect one cycle');
cyclePanel.Layout.Row = 3;
cyclePanel.Layout.Column = 3;
cycleGrid = uigridlayout(cyclePanel,[2 1]);
cycleGrid.RowHeight = {46,'1x'};
uilabel(cycleGrid,'WordWrap','on', ...
    'Text','Selects a visible cycle without changing the pipeline calculation.');
cycleSpinner = uispinner(cycleGrid,'Limits',[1 10], ...
    'RoundFractionalValues','on','Step',1,'Value',5, ...
    'Tooltip','Cycle in the current bounded timeline.');

faultPanel = uipanel(gridLayout,'Title','Deliberately broken case');
faultPanel.Layout.Row = 3;
faultPanel.Layout.Column = 4;
faultGrid = uigridlayout(faultPanel,[2 1]);
faultGrid.RowHeight = {52,'1x'};
uilabel(faultGrid,'WordWrap','on', ...
    'Text','Available only when product data passes through a register.');
faultCheckbox = uicheckbox(faultGrid, ...
    'Text','Bypass valid/token delay','Value',false, ...
    'Tooltip','Violates equal delay for product data, valid, and token identity.');

summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 4;
summary.Layout.Column = [1 4];

stageSpinner.ValueChangedFcn = @(~,~) updatePlots();
periodSpinner.ValueChangedFcn = @(~,~) updatePlots();
cycleSpinner.ValueChangedFcn = @(~,~) updatePlots();
faultCheckbox.ValueChangedFcn = @(~,~) updatePlots();
updatePlots();

    function updatePlots
        pipelineStages = round(stageSpinner.Value);
        inputPeriod = round(periodSpinner.Value);
        sizing = modelFcn(pipelineStages,inputPeriod,1,false);
        if cycleSpinner.Value > sizing.totalCycles
            cycleSpinner.Value = sizing.totalCycles;
        end
        cycleSpinner.Limits = [1 sizing.totalCycles];
        selectedCycle = round(cycleSpinner.Value);
        if pipelineStages == 0
            faultCheckbox.Value = false;
            faultCheckbox.Enable = 'off';
        else
            faultCheckbox.Enable = 'on';
        end
        brokenValidAlignment = faultCheckbox.Value;
        out = modelFcn(pipelineStages,inputPeriod,selectedCycle, ...
            brokenValidAlignment);

        cla(scheduleAxes);
        stem(scheduleAxes,out.cycle(out.inputValid), ...
            out.inputProductValue(out.inputValid),'o','LineWidth',1.2, ...
            'DisplayName','Accepted input product');
        hold(scheduleAxes,'on');
        stem(scheduleAxes,out.cycle(out.referenceAccumulatorValid), ...
            out.accumulatorProductValue(out.referenceAccumulatorValid), ...
            '--s','LineWidth',1.2,'DisplayName','Product after data delay');
        sampledColor = [0.00 0.45 0.74];
        if out.brokenValidAlignment
            sampledColor = [0.85 0.10 0.10];
            scatter(scheduleAxes,out.cycle(out.accumulatorValid), ...
                out.accumulatorProductValue(out.accumulatorValid),70, ...
                sampledColor,'filled','DisplayName','Broken valid samples');
        end
        scatter(scheduleAxes,out.selectedCycle, ...
            out.selectedAccumulatorProductCode*out.productLsb,85, ...
            sampledColor,'filled','DisplayName','Selected accumulator data');
        hold(scheduleAxes,'off');
        grid(scheduleAxes,'on');
        xlabel(scheduleAxes,'Clock edge [cycles]');
        ylabel(scheduleAxes,'Product value [unitless product]');
        title(scheduleAxes,'Input products and delayed accumulator data');
        scheduleAxes.XLim = [1 out.totalCycles];
        legend(scheduleAxes,'Location','best');

        cla(sumAxes);
        stairs(sumAxes,out.cycle,out.referenceRunningSum,'LineWidth',1.35, ...
            'DisplayName','Healthy aligned sum');
        hold(sumAxes,'on');
        if out.brokenValidAlignment
            stairs(sumAxes,out.cycle,out.runningSum,'--','LineWidth',1.35, ...
                'DisplayName','Broken bypassed-valid sum');
        end
        scatter(sumAxes,out.selectedCycle,out.selectedRunningSumCode* ...
            out.productLsb,85,sampledColor,'filled', ...
            'DisplayName','Selected actual sum');
        hold(sumAxes,'off');
        grid(sumAxes,'on');
        xlabel(sumAxes,'Clock edge [cycles]');
        ylabel(sumAxes,'Running MAC result [unitless]');
        title(sumAxes,'Accumulation state and alignment symptom');
        sumAxes.XLim = [1 out.totalCycles];
        legend(sumAxes,'Location','best');

        alignmentHealth = 'product, valid, and token are aligned';
        if out.brokenValidAlignment
            alignmentHealth = 'BROKEN: valid/token bypass the product delay';
        end
        summary.Text = sprintf([ ...
            'Cycle %d: input valid/token/product=%d/%d/%d; accumulator ' ...
            'valid/data-token/valid-token/product=%d/%d/%d/%d; sum code ' ...
            'actual/reference=%d/%d. L=%d stages, input period=%d cycles, ' ...
            'first/final accumulation=%d/%d, final code/value=%d/%g ' ...
            '(reference %d/%g), dropped tokens=%s, valid/data mismatches=%d. ' ...
            '%s. Foperand=%d, Fproduct=%d, product LSB=%g; required ' ...
            'accumulator width=%d modeled bits (trace minimum %d). %s'], ...
            out.selectedCycle,out.selectedInputValid,out.selectedInputToken, ...
            out.selectedInputProductCode,out.selectedActualValid, ...
            out.selectedDataToken,out.selectedValidToken, ...
            out.selectedAccumulatorProductCode,out.selectedRunningSumCode, ...
            out.selectedReferenceSumCode,out.pipelineStages,out.inputPeriod, ...
            out.firstReferenceAccumulationCycle,out.completionCycle, ...
            out.finalSumCode,out.finalSum,out.referenceFinalSumCode, ...
            out.referenceFinalSum,mat2str(out.droppedTokenIndices.'), ...
            out.validDataMismatchCount,alignmentHealth, ...
            out.operandFractionBits,out.productFractionBits,out.productLsb, ...
            out.modeledAccumulatorWordLength, ...
            out.minimumSequenceAccumulatorBits,out.equationText);
        drawnow;
    end
end
