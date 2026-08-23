function interactive
%INTERACTIVE Explore FSM event timing and a broken priority rule.
clear model;
modelFcn = @model;
figureName = 'P04 Finite-State Machine Explorer';
delete(findall(groot,'Type','figure','Name',figureName));

fig = uifigure('Name',figureName,'Position',[80 80 1180 760]);
gridLayout = uigridlayout(fig,[4 4]);
gridLayout.RowHeight = {62,'1x',112,116};
gridLayout.ColumnWidth = {'1x','1x','1x','1x'};

instruction = uilabel(gridLayout,'WordWrap','on', ...
    'Text',['Read the baseline first. Change completion delay or timeout ' ...
    'limit independently. Inputs are pre-edge; registered state and Moore ' ...
    'outputs are post-edge. Completion on the deadline succeeds.']);
instruction.Layout.Row = 1;
instruction.Layout.Column = [1 4];

stateAxes = uiaxes(gridLayout);
stateAxes.Layout.Row = 2;
stateAxes.Layout.Column = [1 2];
signalAxes = uiaxes(gridLayout);
signalAxes.Layout.Row = 2;
signalAxes.Layout.Column = [3 4];

completionPanel = uipanel(gridLayout,'Title','Lever 1: completion delay');
completionPanel.Layout.Row = 3;
completionPanel.Layout.Column = 1;
completionGrid = uigridlayout(completionPanel,[2 1]);
completionGrid.RowHeight = {42,'1x'};
uilabel(completionGrid,'WordWrap','on', ...
    'Text','Moves only the synthetic work-done input after start.');
completionSpinner = uispinner(completionGrid,'Limits',[1 8], ...
    'RoundFractionalValues','on','Step',1,'Value',3, ...
    'Tooltip','Completion delay in cycles after the start edge.');

timeoutPanel = uipanel(gridLayout,'Title','Lever 2: timeout limit');
timeoutPanel.Layout.Row = 3;
timeoutPanel.Layout.Column = 2;
timeoutGrid = uigridlayout(timeoutPanel,[2 1]);
timeoutGrid.RowHeight = {42,'1x'};
uilabel(timeoutGrid,'WordWrap','on', ...
    'Text','Moves only the synthetic deadline-expired input after start.');
timeoutSpinner = uispinner(timeoutGrid,'Limits',[1 8], ...
    'RoundFractionalValues','on','Step',1,'Value',5, ...
    'Tooltip','Inclusive timeout limit in cycles after the start edge.');

cyclePanel = uipanel(gridLayout,'Title','Inspect one edge');
cyclePanel.Layout.Row = 3;
cyclePanel.Layout.Column = 3;
cycleGrid = uigridlayout(cyclePanel,[2 1]);
cycleGrid.RowHeight = {42,'1x'};
uilabel(cycleGrid,'WordWrap','on', ...
    'Text','Compare sampled inputs and state before/after this edge.');
cycleSpinner = uispinner(cycleGrid,'Limits',[1 16], ...
    'RoundFractionalValues','on','Step',1,'Value',5, ...
    'Tooltip','Selects one deterministic clock cycle without changing it.');

faultPanel = uipanel(gridLayout,'Title','Deliberately broken case');
faultPanel.Layout.Row = 3;
faultPanel.Layout.Column = 4;
faultGrid = uigridlayout(faultPanel,[2 1]);
faultGrid.RowHeight = {50,'1x'};
uilabel(faultGrid,'WordWrap','on', ...
    'Text','Set both timing levers equal to expose contested priority.');
faultCheckbox = uicheckbox(faultGrid, ...
    'Text','Let timeout win the tie','Value',false,'Enable','off', ...
    'Tooltip','Violates the declared completion-at-deadline policy.');

summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 4;
summary.Layout.Column = [1 4];

completionSpinner.ValueChangedFcn = @(~,~) updatePlots();
timeoutSpinner.ValueChangedFcn = @(~,~) updatePlots();
cycleSpinner.ValueChangedFcn = @(~,~) updatePlots();
faultCheckbox.ValueChangedFcn = @(~,~) updatePlots();
updatePlots();

    function updatePlots
        completionDelay = round(completionSpinner.Value);
        timeoutLimit = round(timeoutSpinner.Value);
        selectedCycle = round(cycleSpinner.Value);
        if completionDelay ~= timeoutLimit
            faultCheckbox.Value = false;
            faultCheckbox.Enable = 'off';
        else
            faultCheckbox.Enable = 'on';
        end
        brokenPriority = faultCheckbox.Value;
        out = modelFcn(completionDelay,timeoutLimit,selectedCycle, ...
            brokenPriority);

        cla(stateAxes);
        stairs(stateAxes,out.cycle,out.referenceStateAfter,'-o', ...
            'LineWidth',1.3,'DisplayName','Declared priority');
        hold(stateAxes,'on');
        if out.brokenPriority
            stairs(stateAxes,out.cycle,out.stateAfter,'--s', ...
                'LineWidth',1.35,'DisplayName','Broken priority');
        end
        selectedColor = [0.00 0.45 0.74];
        if out.selectedMismatch
            selectedColor = [0.85 0.10 0.10];
        end
        scatter(stateAxes,out.selectedCycle,out.stateAfter(out.selectedCycle), ...
            85,selectedColor,'filled','DisplayName','Selected post-edge state');
        if out.mismatchCount > 0
            scatter(stateAxes,out.mismatchCycles, ...
                out.stateAfter(out.mismatchMask),65,[0.85 0.10 0.10], ...
                'filled','DisplayName','Priority mismatch');
        end
        hold(stateAxes,'off');
        grid(stateAxes,'on');
        xlabel(stateAxes,'Clock cycle [cycles]');
        ylabel(stateAxes,'State code [unitless]');
        title(stateAxes,'Registered state after each rising edge');
        stateAxes.XLim = [1 out.cycleCount];
        stateAxes.YLim = [-0.25 3.25];
        stateAxes.YTick = out.stateCodes;
        stateAxes.YTickLabel = out.stateLabels;
        legend(stateAxes,'Location','best');

        cla(signalAxes);
        signalLabels = {'reset','start','work done','deadline expired', ...
            'busy','done','timeout'};
        signals = double([out.reset out.start out.workDone ...
            out.deadlineExpired out.busy out.donePulse out.timeoutPulse]);
        signalOffsets = 2*(0:numel(signalLabels)-1);
        signalRows = signals + repmat(signalOffsets,out.cycleCount,1);
        stairs(signalAxes,out.cycle,signalRows,'LineWidth',1.15);
        grid(signalAxes,'on');
        xlabel(signalAxes,'Clock cycle [cycles]');
        ylabel(signalAxes,'Signal level [binary] (vertically offset)');
        title(signalAxes,'Inputs before edge; Moore outputs on labeled rows');
        signalAxes.XLim = [1 out.cycleCount];
        signalAxes.YLim = [-0.25 signalOffsets(end)+1.25];
        signalAxes.YTick = signalOffsets;
        signalAxes.YTickLabel = signalLabels;

        health = 'matches the declared completion-first reference';
        if out.selectedMismatch
            health = 'MISMATCHES the declared completion-first reference';
        end
        summary.Text = sprintf([ ...
            'Cycle %d: inputs reset=%d, start=%d, workDone=%d, deadline=%d; ' ...
            'state %s -> %s (%s); busy=%d, done=%d, timeout=%d; %s. ' ...
            'First terminal=%s at cycle %d, WAIT dwell=%d cycles, ' ...
            'ignored late work/deadline pulses=%d/%d, mismatches=%d, ' ...
            'modeled state bits=%d. %s'], ...
            out.selectedCycle,out.selectedReset,out.selectedStart, ...
            out.selectedWorkDone,out.selectedDeadlineExpired, ...
            out.selectedStateBefore,out.selectedStateAfter, ...
            out.selectedTransitionReason,out.selectedBusy,out.selectedDone, ...
            out.selectedTimeout,health,out.terminalStateName, ...
            out.terminalCycle,out.busyCycleCount, ...
            out.ignoredLateWorkDoneCount,out.ignoredLateDeadlineCount, ...
            out.mismatchCount,out.modeledStateBits,out.equationText);
        drawnow;
    end
end
