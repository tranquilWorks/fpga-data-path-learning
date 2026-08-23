function interactive
%INTERACTIVE Explore register depth, clock enable, and a broken update rule.
clear model;
modelFcn = @model;
figureName = 'P03 Register State Explorer';
delete(findall(groot,'Type','figure','Name',figureName));

fig = uifigure('Name',figureName,'Position',[80 80 1180 760]);
gridLayout = uigridlayout(fig,[4 4]);
gridLayout.RowHeight = {58,'1x',112,104};
gridLayout.ColumnWidth = {'1x','1x','1x','1x'};

instruction = uilabel(gridLayout,'WordWrap','on', ...
    'Text',['Read the one-stage baseline first. Change depth or enable ' ...
    'period independently, then enable the broken cascade. All values are ' ...
    'sampled at rising edges; reset has priority over enable.']);
instruction.Layout.Row = 1;
instruction.Layout.Column = [1 4];

timingAxes = uiaxes(gridLayout);
timingAxes.Layout.Row = 2;
timingAxes.Layout.Column = [1 2];
stateAxes = uiaxes(gridLayout);
stateAxes.Layout.Row = 2;
stateAxes.Layout.Column = [3 4];

depthPanel = uipanel(gridLayout,'Title','Lever 1: register depth');
depthPanel.Layout.Row = 3;
depthPanel.Layout.Column = 1;
depthGrid = uigridlayout(depthPanel,[2 1]);
depthGrid.RowHeight = {34,'1x'};
uilabel(depthGrid,'WordWrap','on', ...
    'Text','Stages add active-edge delay and 4 storage bits each.');
depthSpinner = uispinner(depthGrid,'Limits',[1 4], ...
    'RoundFractionalValues','on','Step',1,'Value',1, ...
    'Tooltip','Changes pipeline depth while preserving the enable schedule.');

enablePanel = uipanel(gridLayout,'Title','Lever 2: enable period');
enablePanel.Layout.Row = 3;
enablePanel.Layout.Column = 2;
enableGrid = uigridlayout(enablePanel,[2 1]);
enableGrid.RowHeight = {34,'1x'};
uilabel(enableGrid,'WordWrap','on', ...
    'Text','Period 1 captures every edge; larger periods create holds.');
enableSpinner = uispinner(enableGrid,'Limits',[1 4], ...
    'RoundFractionalValues','on','Step',1,'Value',1, ...
    'Tooltip','Changes capture cadence while preserving register depth.');

cyclePanel = uipanel(gridLayout,'Title','Inspect one edge');
cyclePanel.Layout.Row = 3;
cyclePanel.Layout.Column = 3;
cycleGrid = uigridlayout(cyclePanel,[2 1]);
cycleGrid.RowHeight = {34,'1x'};
uilabel(cycleGrid,'WordWrap','on', ...
    'Text','Compare state immediately before and after this edge.');
cycleSpinner = uispinner(cycleGrid,'Limits',[1 16], ...
    'RoundFractionalValues','on','Step',1,'Value',6, ...
    'Tooltip','Highlights one deterministic clock cycle.');

faultPanel = uipanel(gridLayout,'Title','Deliberately broken case');
faultPanel.Layout.Row = 3;
faultPanel.Layout.Column = 4;
faultGrid = uigridlayout(faultPanel,[2 1]);
faultGrid.RowHeight = {44,'1x'};
uilabel(faultGrid,'WordWrap','on', ...
    'Text','Choose depth 2..4, then violate pre-edge sampling.');
faultCheckbox = uicheckbox(faultGrid, ...
    'Text','Cascade new values on one edge','Value',false, ...
    'Tooltip','Incorrectly reuses each stage''s just-updated value.');

summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 4;
summary.Layout.Column = [1 4];

depthSpinner.ValueChangedFcn = @(~,~) updatePlots();
enableSpinner.ValueChangedFcn = @(~,~) updatePlots();
cycleSpinner.ValueChangedFcn = @(~,~) updatePlots();
faultCheckbox.ValueChangedFcn = @(~,~) updatePlots();
updatePlots();

    function updatePlots
        stageCount = round(depthSpinner.Value);
        enablePeriod = round(enableSpinner.Value);
        selectedCycle = round(cycleSpinner.Value);
        if stageCount == 1
            faultCheckbox.Value = false;
            faultCheckbox.Enable = 'off';
        else
            faultCheckbox.Enable = 'on';
        end
        brokenCascade = faultCheckbox.Value;
        out = modelFcn(stageCount,enablePeriod,selectedCycle,brokenCascade);

        cla(timingAxes);
        plottedOutput = out.output;
        plottedOutput(~out.outputValid) = NaN;
        stairs(timingAxes,out.cycle,out.inputData,'-o','LineWidth',1.2, ...
            'DisplayName','Input D before edge');
        hold(timingAxes,'on');
        stairs(timingAxes,out.cycle,plottedOutput,'--s','LineWidth',1.3, ...
            'DisplayName','Last-stage Q after edge');
        selectedColor = [0.00 0.45 0.74];
        if out.selectedMismatch
            selectedColor = [0.85 0.10 0.10];
        end
        if out.selectedOutputValid
            scatter(timingAxes,out.selectedCycle,out.selectedOutput,90, ...
                selectedColor,'filled','DisplayName','Selected valid output');
        else
            scatter(timingAxes,out.selectedCycle,out.selectedOutput,100, ...
                [0.35 0.35 0.35],'x','LineWidth',1.8, ...
                'DisplayName','Selected invalid fill');
        end
        if out.mismatchCount > 0
            scatter(timingAxes,out.mismatchCycles, ...
                out.output(out.mismatchMask),52,[0.85 0.10 0.10], ...
                'filled','DisplayName','Mismatch');
        end
        hold(timingAxes,'off');
        grid(timingAxes,'on');
        xlabel(timingAxes,'Clock cycle [cycles]');
        ylabel(timingAxes,'Unsigned 4-bit code [0..15]');
        title(timingAxes,'Input and observable stored output');
        timingAxes.XLim = [1 out.cycleCount];
        timingAxes.YLim = [0 15];
        legend(timingAxes,'Location','best');

        cla(stateAxes);
        plottedState = out.stateAfter;
        plottedState(~out.validAfter) = NaN;
        stairs(stateAxes,out.cycle,plottedState,'LineWidth',1.25);
        grid(stateAxes,'on');
        xlabel(stateAxes,'Clock cycle [cycles]');
        ylabel(stateAxes,'Stored stage code [0..15]');
        title(stateAxes,'State after each rising edge');
        stateAxes.XLim = [1 out.cycleCount];
        stateAxes.YLim = [0 15];
        legend(stateAxes,out.stageLabels,'Location','best');

        beforeText = mat2str(out.selectedStateBefore);
        afterText = mat2str(out.selectedStateAfter);
        validity = 'not yet valid';
        if out.selectedOutputValid
            validity = 'valid';
        end
        health = 'matches simultaneous-transfer reference';
        if out.selectedMismatch
            health = 'MISMATCHES simultaneous-transfer reference';
        end
        summary.Text = sprintf([ ...
            'Cycle %d: reset=%d, enable=%d, action=%s, D=%d, state %s -> %s, ' ...
            'output=%d (%s), %s. Captures=%d, holds=%d, first valid cycle=%d, ' ...
            'modeled data storage=%d bits, mismatches=%d. %s'], ...
            out.selectedCycle,out.selectedReset,out.selectedEnable, ...
            out.selectedAction,out.selectedInput,beforeText,afterText, ...
            out.selectedOutput,validity,health,out.captureCount,out.holdCount, ...
            out.firstValidCycle,out.dataStorageBitCount,out.mismatchCount, ...
            out.equationText);
        drawnow limitrate;
    end
end
