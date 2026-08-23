function interactive
%INTERACTIVE Explore a bounded three-input truth table one lever at a time.
clear model;
modelFcn = @model;
figureName = 'P02 Truth Table Explorer';
delete(findall(groot,'Type','figure','Name',figureName));

fig = uifigure('Name',figureName,'Position',[80 80 1180 760]);
gridLayout = uigridlayout(fig,[4 4]);
gridLayout.RowHeight = {52,'1x',110,92};
gridLayout.ColumnWidth = {'1x','1x','1x','1x'};

instruction = uilabel(gridLayout,'WordWrap','on', ...
    'Text',['Read the baseline first. Change k or p independently; use the ' ...
    'fault only after both healthy cases make sense. A is the address MSB.']);
instruction.Layout.Row = 1;
instruction.Layout.Column = [1 4];

truthAxes = uiaxes(gridLayout);
truthAxes.Layout.Row = 2;
truthAxes.Layout.Column = [1 2];
probabilityAxes = uiaxes(gridLayout);
probabilityAxes.Layout.Row = 2;
probabilityAxes.Layout.Column = [3 4];

thresholdPanel = uipanel(gridLayout,'Title','Lever 1: required HIGH inputs k');
thresholdPanel.Layout.Row = 3;
thresholdPanel.Layout.Column = 1;
thresholdGrid = uigridlayout(thresholdPanel,[2 1]);
thresholdGrid.RowHeight = {22,'1x'};
uilabel(thresholdGrid,'Text','1 = OR, 2 = majority, 3 = AND');
thresholdSpinner = uispinner(thresholdGrid,'Limits',[1 3], ...
    'RoundFractionalValues','on','Step',1,'Value',2, ...
    'Tooltip','Changes the specified truth-table mapping.');

probabilityPanel = uipanel(gridLayout,'Title','Lever 2: input HIGH probability p');
probabilityPanel.Layout.Row = 3;
probabilityPanel.Layout.Column = 2;
probabilityGrid = uigridlayout(probabilityPanel,[2 1]);
probabilityGrid.RowHeight = {22,'1x'};
probabilityValue = uilabel(probabilityGrid,'Text','p = 0.50 [unitless]');
probabilitySlider = uislider(probabilityGrid,'Limits',[0 1], ...
    'MajorTicks',[0 0.25 0.5 0.75 1],'Value',0.5, ...
    'Tooltip','Weights row occurrence; it does not change the truth table.');

addressPanel = uipanel(gridLayout,'Title','Inspect one input address');
addressPanel.Layout.Row = 3;
addressPanel.Layout.Column = 3;
addressGrid = uigridlayout(addressPanel,[2 1]);
addressGrid.RowHeight = {22,'1x'};
uilabel(addressGrid,'Text','Address 0..7 = binary ABC');
addressSpinner = uispinner(addressGrid,'Limits',[0 7], ...
    'RoundFractionalValues','on','Step',1,'Value',3, ...
    'Tooltip','Highlights one exhaustive truth-table row.');

faultPanel = uipanel(gridLayout,'Title','Deliberately broken case');
faultPanel.Layout.Row = 3;
faultPanel.Layout.Column = 4;
faultGrid = uigridlayout(faultPanel,[2 1]);
faultGrid.RowHeight = {38,'1x'};
uilabel(faultGrid,'WordWrap','on', ...
    'Text','Violate: every LUT entry matches its specified row.');
faultCheckbox = uicheckbox(faultGrid,'Text','Flip LUT address 6 (110)', ...
    'Value',false,'Tooltip','Injects exactly one truth-table mismatch.');

summary = uilabel(gridLayout,'WordWrap','on');
summary.Layout.Row = 4;
summary.Layout.Column = [1 4];

thresholdSpinner.ValueChangedFcn = @(~,~) updatePlots();
addressSpinner.ValueChangedFcn = @(~,~) updatePlots();
faultCheckbox.ValueChangedFcn = @(~,~) updatePlots();
probabilitySlider.ValueChangingFcn = @(~,event) updatePlots(event.Value);
probabilitySlider.ValueChangedFcn = @(~,~) updatePlots();
updatePlots();

    function updatePlots(probabilityOverride)
        if nargin < 1
            p = probabilitySlider.Value;
        else
            p = probabilityOverride;
        end
        probabilityValue.Text = sprintf('p = %.2f [unitless]',p);
        requiredHigh = round(thresholdSpinner.Value);
        selectedAddress = round(addressSpinner.Value);
        faultAddress = -1;
        if faultCheckbox.Value
            faultAddress = 6;
        end
        out = modelFcn(requiredHigh,p,selectedAddress,faultAddress);

        cla(truthAxes);
        stairs(truthAxes,out.inputAddress,double(out.specifiedOutput),'-o', ...
            'LineWidth',1.4,'DisplayName','Specified output');
        hold(truthAxes,'on');
        stairs(truthAxes,out.inputAddress,double(out.lutOutput),'--s', ...
            'LineWidth',1.2,'DisplayName','LUT output');
        markerColor = [0.00 0.45 0.74];
        if ~out.selectedMatches
            markerColor = [0.85 0.10 0.10];
        end
        scatter(truthAxes,out.selectedAddress,double(out.selectedLutOutput), ...
            100,markerColor,'filled','DisplayName','Selected row');
        hold(truthAxes,'off');
        grid(truthAxes,'on');
        xlabel(truthAxes,'Input address 4A+2B+C [unitless]');
        ylabel(truthAxes,'Logic output Y [binary]');
        title(truthAxes,sprintf('%d-of-3 truth table',requiredHigh));
        truthAxes.XTick = 0:7;
        truthAxes.XTickLabel = out.inputLabels;
        truthAxes.YTick = [0 1];
        truthAxes.YLim = [-0.1 1.1];
        legend(truthAxes,'Location','best');

        probabilityGridValues = 0:0.02:1;
        specifiedProbability = zeros(size(probabilityGridValues));
        lutProbability = zeros(size(probabilityGridValues));
        for probabilityIndex = 1:numel(probabilityGridValues)
            curve = modelFcn(requiredHigh,probabilityGridValues(probabilityIndex), ...
                selectedAddress,faultAddress);
            specifiedProbability(probabilityIndex) = curve.specifiedHighProbability;
            lutProbability(probabilityIndex) = curve.lutHighProbability;
        end
        cla(probabilityAxes);
        plot(probabilityAxes,probabilityGridValues,specifiedProbability, ...
            'LineWidth',1.4,'DisplayName','Specified P(Y=1)');
        hold(probabilityAxes,'on');
        plot(probabilityAxes,probabilityGridValues,lutProbability,'--', ...
            'LineWidth',1.2,'DisplayName','LUT P(Y=1)');
        scatter(probabilityAxes,p,out.lutHighProbability,70,markerColor, ...
            'filled','DisplayName','Current p');
        hold(probabilityAxes,'off');
        grid(probabilityAxes,'on');
        xlabel(probabilityAxes,'Independent input HIGH probability p [unitless]');
        ylabel(probabilityAxes,'Output HIGH probability P(Y=1) [unitless]');
        title(probabilityAxes,'Row weighting under the independent-input assumption');
        probabilityAxes.XLim = [0 1];
        probabilityAxes.YLim = [0 1];
        legend(probabilityAxes,'Location','best');

        bits = out.selectedBits;
        summary.Text = sprintf([ ...
            'Address %d -> A=%d, B=%d, C=%d | specified Y=%d | LUT Y=%d | ' ...
            '%s | asserted rows=%d/8 | P(specified Y=1)=%.3f | ' ...
            'mismatches=%d | weighted mismatch probability=%.3f. ' ...
            'The probability metric assumes independent inputs with the same p.'], ...
            out.selectedAddress,bits(1),bits(2),bits(3), ...
            out.selectedSpecifiedOutput,out.selectedLutOutput,out.equationText, ...
            out.assertedRowCount,out.specifiedHighProbability, ...
            out.mismatchCount,out.mismatchProbability);
        drawnow limitrate;
    end
end
