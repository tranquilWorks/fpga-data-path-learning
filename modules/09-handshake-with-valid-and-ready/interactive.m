function interactive
%INTERACTIVE Explore valid/ready timing and one broken producer rule.
clear model;
modelFcn = @model;
figureName = 'P09 Valid and Ready Handshake Explorer';
delete(findall(groot,'Type','figure','Name',figureName));

fig = uifigure('Name',figureName,'Position',[70 70 1240 790]);
gridLayout = uigridlayout(fig,[4 4]);
gridLayout.RowHeight = {76,'1x',126,158};
gridLayout.ColumnWidth = {'1x','1x','1x','1x'};

instruction = uilabel(gridLayout,'WordWrap','on', ...
    'Text',['Read the one-gap, three-stall baseline first. Change source ' ...
    'gap or ready-low duration independently. A transfer occurs only on ' ...
    'valid && ready; the broken switch advances the source without ready.']);
instruction.Layout.Row = 1;
instruction.Layout.Column = [1 4];

signalAxes = uiaxes(gridLayout);
signalAxes.Layout.Row = 2;
signalAxes.Layout.Column = [1 2];
payloadAxes = uiaxes(gridLayout);
payloadAxes.Layout.Row = 2;
payloadAxes.Layout.Column = [3 4];

gapPanel = uipanel(gridLayout,'Title','Lever 1: source gap');
gapPanel.Layout.Row = 3;
gapPanel.Layout.Column = 1;
gapGrid = uigridlayout(gapPanel,[2 1]);
gapGrid.RowHeight = {56,'1x'};
uilabel(gapGrid,'WordWrap','on', ...
    'Text','Idle cycles inserted only after a successful transfer.');
gapSpinner = uispinner(gapGrid,'Limits',[0 3], ...
    'RoundFractionalValues','on','Step',1,'Value',1, ...
    'Tooltip','Producer bubbles between accepted payloads.');

stallPanel = uipanel(gridLayout,'Title','Lever 2: ready-low duration');
stallPanel.Layout.Row = 3;
stallPanel.Layout.Column = 2;
stallGrid = uigridlayout(stallPanel,[2 1]);
stallGrid.RowHeight = {56,'1x'};
uilabel(stallGrid,'WordWrap','on', ...
    'Text','Consumer deasserts ready beginning at fixed cycle 5.');
stallSpinner = uispinner(stallGrid,'Limits',[0 6], ...
    'RoundFractionalValues','on','Step',1,'Value',3, ...
    'Tooltip','Number of consecutive ready-low clock cycles.');

cyclePanel = uipanel(gridLayout,'Title','Observation cycle');
cyclePanel.Layout.Row = 3;
cyclePanel.Layout.Column = 3;
cycleGrid = uigridlayout(cyclePanel,[2 1]);
cycleGrid.RowHeight = {56,'1x'};
uilabel(cycleGrid,'WordWrap','on', ...
    'Text','Highlights one pre-edge signal and payload observation.');
cycleSpinner = uispinner(cycleGrid,'Limits',[1 35], ...
    'RoundFractionalValues','on','Step',1,'Value',5, ...
    'Tooltip','Clock cycle to inspect in both linked views.');

faultPanel = uipanel(gridLayout,'Title','Deliberately broken case');
faultPanel.Layout.Row = 3;
faultPanel.Layout.Column = 4;
faultGrid = uigridlayout(faultPanel,[2 1]);
faultGrid.RowHeight = {60,'1x'};
uilabel(faultGrid,'WordWrap','on', ...
    'Text',['Enabled when a ready-low interval exists; inert if no valid ' ...
        'offer overlaps it.']);
faultCheckbox = uicheckbox(faultGrid, ...
    'Text','Advance source without ready','Value',false, ...
    'Tooltip','Violates the rule that source state advances only on transfer.');

summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 4;
summary.Layout.Column = [1 4];

gapSpinner.ValueChangedFcn = @(~,~) updatePlots();
stallSpinner.ValueChangedFcn = @(~,~) updatePlots();
cycleSpinner.ValueChangedFcn = @(~,~) updatePlots();
faultCheckbox.ValueChangedFcn = @(~,~) updatePlots();
updatePlots();

    function updatePlots
        sourceGapCycles = round(gapSpinner.Value);
        readyStallCycles = round(stallSpinner.Value);
        selectedCycle = round(cycleSpinner.Value);
        if readyStallCycles == 0
            faultCheckbox.Value = false;
            faultCheckbox.Enable = 'off';
        else
            faultCheckbox.Enable = 'on';
        end
        brokenMode = faultCheckbox.Value;
        out = modelFcn(sourceGapCycles,readyStallCycles,brokenMode);

        cla(signalAxes);
        stairs(signalAxes,out.cycle,double(out.applied.valid), ...
            'LineWidth',1.25,'DisplayName','valid');
        hold(signalAxes,'on');
        stairs(signalAxes,out.cycle,2+double(out.ready), ...
            'LineWidth',1.25,'DisplayName','ready');
        stairs(signalAxes,out.cycle,4+double(out.applied.transfer), ...
            'LineWidth',1.25,'DisplayName','transfer');
        xline(signalAxes,selectedCycle,':','Selected cycle', ...
            'LabelVerticalAlignment','bottom');
        hold(signalAxes,'off');
        grid(signalAxes,'on');
        xlabel(signalAxes,'Clock cycle [cycles]');
        ylabel(signalAxes,'Handshake signals [binary, vertically offset]');
        title(signalAxes,'Applied valid, ready, and transfer');
        signalAxes.YTick = [0.5 2.5 4.5];
        signalAxes.YTickLabel = {'valid','ready','transfer'};
        signalAxes.YLim = [-0.2 5.2];
        signalAxes.XLim = [1 out.recordCycleCount];

        cla(payloadAxes);
        stairs(payloadAxes,out.cycle,out.reference.dataCode, ...
            'LineWidth',1.25,'DisplayName','Healthy offered payload');
        hold(payloadAxes,'on');
        stairs(payloadAxes,out.cycle,out.applied.dataCode,'--', ...
            'LineWidth',1.25,'DisplayName','Applied offered payload');
        scatter(payloadAxes,out.cycle(out.applied.transfer), ...
            out.applied.acceptedDataCodeByCycle(out.applied.transfer), ...
            38,'filled','DisplayName','Applied transfer');
        xline(payloadAxes,selectedCycle,':','Selected cycle', ...
            'LabelVerticalAlignment','bottom');
        hold(payloadAxes,'off');
        grid(payloadAxes,'on');
        xlabel(payloadAxes,'Clock cycle [cycles]');
        ylabel(payloadAxes,'Payload [unsigned 12-bit phase code]');
        title(payloadAxes,'Healthy reference versus applied producer');
        payloadAxes.XLim = [1 out.recordCycleCount];
        legend(payloadAxes,'Location','best');

        if out.applied.valid(selectedCycle)
            selectedPayload = sprintf('%g', ...
                out.applied.dataCode(selectedCycle));
        else
            selectedPayload = 'none (valid is low)';
        end
        if out.faultActive
            health = ['BROKEN: advancing without ready dropped at least ' ...
                'one owed token'];
        else
            health = ['healthy/inert: producer state changes only after ' ...
                'a transfer'];
        end
        summary.Text = sprintf([ ...
            'Selected cycle %d: valid=%d, ready=%d, transfer=%d, ' ...
            'payload=%s. Source gap=%d cycles; ready low=%d cycles from ' ...
            'cycle %d. Healthy completion/rate=%g cycles/%0.6g ' ...
            'transfers per cycle; applied accepted/lost/dropped/hold-' ...
            'violations=%d/%d/%d/%d tokens or events; applied maximum ' ...
            'wait=%g cycles. %s. Payloads are precomputed P08 phase-code ' ...
            'labels; the 35-cycle trace and 12-bit hold width are model ' ...
            'bounds, not achieved timing or FPGA utilization. %s.'], ...
            selectedCycle,out.applied.valid(selectedCycle), ...
            out.ready(selectedCycle),out.applied.transfer(selectedCycle), ...
            selectedPayload,out.sourceGapCycles,out.readyStallCycles, ...
            out.readyStallStartCycle,out.reference.completionCycle, ...
            out.reference.activeWindowTransferRate, ...
            out.applied.acceptedTokenCount,out.applied.lostTokenCount, ...
            out.applied.dropCount,out.applied.holdViolationCount, ...
            out.applied.maximumWaitCycles,health,out.equationText);
        drawnow;
    end
end
