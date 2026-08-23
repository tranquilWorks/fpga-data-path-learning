function interactive
%INTERACTIVE Explore bounded P12 FIFO sizing controls.

figureName = 'P12 FIFO sizing explorer';
delete(findall(groot,'Type','figure','Name',figureName));
modelFcn = @model;
fig = uifigure('Name',figureName,'Position',[80 80 1280 780]);
layout = uigridlayout(fig,[3 6]);
layout.RowHeight = {'1x','1x',132};
layout.ColumnWidth = {'1x','1x','1x','1x','1x','1x'};

cumulativeAxes = uiaxes(layout);
cumulativeAxes.Layout.Row = 1;
cumulativeAxes.Layout.Column = [1 3];
occupancyAxes = uiaxes(layout);
occupancyAxes.Layout.Row = 1;
occupancyAxes.Layout.Column = [4 6];
admissionAxes = uiaxes(layout);
admissionAxes.Layout.Row = 2;
admissionAxes.Layout.Column = [1 4];
summary = uilabel(layout,'WordWrap','on', ...
    'VerticalAlignment','top');
summary.Layout.Row = 2;
summary.Layout.Column = [5 6];

burstPanel = uipanel(layout,'Title','Lever 1: burst duration');
burstPanel.Layout.Row = 3;
burstPanel.Layout.Column = 1;
burstGrid = uigridlayout(burstPanel,[2 1]);
burstGrid.RowHeight = {48,'1x'};
uilabel(burstGrid,'Text','Offered at fixed arrival rate [cycles]', ...
    'WordWrap','on');
burstSpinner = uispinner(burstGrid,'Limits',[1 8], ...
    'RoundFractionalValues','on','Step',1,'Value',8);

arrivalPanel = uipanel(layout,'Title','Ingress');
arrivalPanel.Layout.Row = 3;
arrivalPanel.Layout.Column = 2;
arrivalGrid = uigridlayout(arrivalPanel,[2 1]);
arrivalGrid.RowHeight = {48,'1x'};
uilabel(arrivalGrid,'Text','Aggregate arrival rate [words/cycle]', ...
    'WordWrap','on');
arrivalSpinner = uispinner(arrivalGrid,'Limits',[1 4], ...
    'RoundFractionalValues','on','Step',1,'Value',3);

servicePanel = uipanel(layout,'Title','Lever 2: service');
servicePanel.Layout.Row = 3;
servicePanel.Layout.Column = 3;
serviceGrid = uigridlayout(servicePanel,[2 1]);
serviceGrid.RowHeight = {48,'1x'};
uilabel(serviceGrid,'Text','Guaranteed stored-word service [words/cycle]', ...
    'WordWrap','on');
serviceSpinner = uispinner(serviceGrid,'Limits',[0 4], ...
    'RoundFractionalValues','on','Step',1,'Value',1);

depthPanel = uipanel(layout,'Title','Installed depth');
depthPanel.Layout.Row = 3;
depthPanel.Layout.Column = 4;
depthGrid = uigridlayout(depthPanel,[2 1]);
depthGrid.RowHeight = {48,'1x'};
uilabel(depthGrid,'Text','Registered FIFO capacity [words]', ...
    'WordWrap','on');
depthSpinner = uispinner(depthGrid,'Limits',[0 32], ...
    'RoundFractionalValues','on','Step',1,'Value',17);

cyclePanel = uipanel(layout,'Title','Observation edge');
cyclePanel.Layout.Row = 3;
cyclePanel.Layout.Column = 5;
cycleGrid = uigridlayout(cyclePanel,[2 1]);
cycleGrid.RowHeight = {48,'1x'};
uilabel(cycleGrid,'Text','Read one transition [clock cycle]', ...
    'WordWrap','on');
cycleSpinner = uispinner(cycleGrid,'Limits',[1 40], ...
    'RoundFractionalValues','on','Step',1,'Value',8);

faultPanel = uipanel(layout,'Title','Broken assumption');
faultPanel.Layout.Row = 3;
faultPanel.Layout.Column = 6;
faultGrid = uigridlayout(faultPanel,[2 1]);
faultGrid.RowHeight = {62,'1x'};
uilabel(faultGrid,'Text', ...
    'Assume new arrivals are fall-through serviceable', ...
    'WordWrap','on');
faultCheckbox = uicheckbox(faultGrid,'Text','Use broken depth estimate', ...
    'Value',false);

controls = {burstSpinner,arrivalSpinner,serviceSpinner, ...
    depthSpinner,cycleSpinner,faultCheckbox};
for controlIndex = 1:numel(controls)
    controls{controlIndex}.ValueChangedFcn = @(~,~) updatePlots();
end
updatePlots();

    function updatePlots
        burstCycles = round(burstSpinner.Value);
        arrivalRate = round(arrivalSpinner.Value);
        serviceRate = round(serviceSpinner.Value);
        configuredDepth = round(depthSpinner.Value);
        selectedCycle = round(cycleSpinner.Value);
        brokenMode = logical(faultCheckbox.Value);
        if brokenMode
            depthSpinner.Enable = 'off';
        else
            depthSpinner.Enable = 'on';
        end
        out = modelFcn(burstCycles,arrivalRate,serviceRate, ...
            configuredDepth,brokenMode);

        cla(cumulativeAxes);
        stairs(cumulativeAxes,out.cycle, ...
            out.reference.cumulativeArrivals,'LineWidth',1.25, ...
            'DisplayName','cumulative arrivals');
        hold(cumulativeAxes,'on');
        stairs(cumulativeAxes,out.cycle, ...
            out.reference.cumulativeDepartures,'LineWidth',1.25, ...
            'DisplayName','cumulative departures');
        xline(cumulativeAxes,selectedCycle,':','selected edge');
        hold(cumulativeAxes,'off');
        grid(cumulativeAxes,'on');
        xlabel(cumulativeAxes,'Clock cycle [cycles]');
        ylabel(cumulativeAxes,'Cumulative work [words]');
        title(cumulativeAxes,'Lossless cumulative arrival-service gap');
        legend(cumulativeAxes,'Location','best');
        xlim(cumulativeAxes,[1 out.recordCycleCount]);

        cla(occupancyAxes);
        stairs(occupancyAxes,out.cycle, ...
            out.reference.occupancyAfter,'LineWidth',1.25, ...
            'DisplayName','required lossless backlog');
        hold(occupancyAxes,'on');
        stairs(occupancyAxes,out.cycle,out.applied.occupancyAfter, ...
            '--','LineWidth',1.25,'DisplayName','selected FIFO occupancy');
        yline(occupancyAxes,out.appliedDepthWords,':', ...
            sprintf('applied depth = %d',out.appliedDepthWords), ...
            'LineWidth',1.1);
        xline(occupancyAxes,selectedCycle,':','selected edge');
        hold(occupancyAxes,'off');
        grid(occupancyAxes,'on');
        xlabel(occupancyAxes,'Clock cycle [cycles]');
        ylabel(occupancyAxes,'Occupancy after edge [words]');
        title(occupancyAxes,'Unbounded sizing before finite-depth clipping');
        legend(occupancyAxes,'Location','best');
        xlim(occupancyAxes,[1 out.recordCycleCount]);
        ylim(occupancyAxes,[0 max([out.requiredDepthWords ...
            out.appliedDepthWords 1])+2]);

        cla(admissionAxes);
        burstEdges = 1:out.burstCycles;
        bar(admissionAxes,burstEdges, ...
            [out.applied.admittedWords(burstEdges) ...
            out.applied.notAcceptedWords(burstEdges)],'stacked');
        grid(admissionAxes,'on');
        xlabel(admissionAxes,'Burst edge [clock cycle]');
        ylabel(admissionAxes,'Admission result [words]');
        title(admissionAxes, ...
            'Full means backpressure; conditional loss if ignored');
        legend(admissionAxes,{'admitted','not accepted'}, ...
            'Location','best');
        xlim(admissionAxes,[0.5 out.burstCycles+0.5]);

        if out.reference.drainComplete
            drainText = sprintf('reference drain cycle %d', ...
                out.reference.drainCompleteCycle);
        else
            drainText = sprintf('no drain by bounded cycle %d', ...
                out.recordCycleCount);
        end
        if out.applied.notAcceptedWordCount > 0
            capacityText = sprintf([ ...
                '%d word(s) require upstream hold/retry; conditional ' ...
                'loss if ignored = %d'], ...
                out.applied.notAcceptedWordCount, ...
                out.applied.conditionalLossIfIgnoredWords);
        else
            capacityText = 'selected depth admits the complete fixed burst';
        end
        summary.Text = sprintf([ ...
            'Selected edge %d: offered/admitted/departed=%d/%d/%d words, ' ...
            'reference/applied occupancy=%d/%d words.\n\n' ...
            'Burst: %d cycles x %d words/cycle = %d words. Service: %d ' ...
            'stored words/cycle.\n\nRequired registered depth=%d words; ' ...
            'configured=%d; applied=%d (%s); margin=%d words.\n\n' ...
            'Fall-through estimate=%d words; %s; %s.\n\n' ...
            'Model bounds: 40 cycles, at most 32 words/storage entries. ' ...
            'These are modeled counts, not BRAM, timing, or measured throughput.'], ...
            selectedCycle,out.arrivalWords(selectedCycle), ...
            out.applied.admittedWords(selectedCycle), ...
            out.applied.departedWords(selectedCycle), ...
            out.reference.occupancyAfter(selectedCycle), ...
            out.applied.occupancyAfter(selectedCycle), ...
            out.burstCycles,out.arrivalRateWordsPerCycle, ...
            out.burstWordCount,out.serviceRateWordsPerCycle, ...
            out.requiredDepthWords,out.fifoDepthWords, ...
            out.appliedDepthWords,out.appliedDepthBasis, ...
            out.depthMarginWords,out.fallThroughEstimateWords, ...
            drainText,capacityText);
    end
end
