function interactive
fig=uifigure('Name','P01 FPGA Streaming FIFO','Position',[100 100 1120 720]);
g=uigridlayout(fig,[3 5]); g.RowHeight={'1x','1x',100};
axOcc=uiaxes(g); axOcc.Layout.Row=1; axOcc.Layout.Column=[1 5];
axFlow=uiaxes(g); axFlow.Layout.Row=2; axFlow.Layout.Column=[1 4];
summary=uilabel(g,'WordWrap','on'); summary.Layout.Row=2; summary.Layout.Column=5;

aS=uislider(g,'Limits',[0 1.5],'Value',0.75); aS.Layout.Row=3; aS.Layout.Column=1;
sS=uislider(g,'Limits',[0.1 1.5],'Value',0.9); sS.Layout.Row=3; sS.Layout.Column=2;
dS=uislider(g,'Limits',[2 256],'Value',32,'MajorTicks',[2 16 32 64 128 256]);
dS.Layout.Row=3; dS.Layout.Column=3;
bS=uislider(g,'Limits',[1 5],'Value',2); bS.Layout.Row=3; bS.Layout.Column=4;
cS=uislider(g,'Limits',[100 1200],'Value',400); cS.Layout.Row=3; cS.Layout.Column=5;
controls=[aS sS dS bS cS];
for i=1:numel(controls)
    controls(i).ValueChangingFcn=@(~,~) updatePlots();
    controls(i).ValueChangedFcn=@(~,~) updatePlots();
end
updatePlots();

    function updatePlots
        out=model(aS.Value,sS.Value,round(dS.Value),bS.Value,round(cS.Value));
        cla(axOcc); stairs(axOcc,out.cycles,out.occupancy,'LineWidth',1.2);
        hold(axOcc,'on'); yline(axOcc,out.fifoDepth,'--'); hold(axOcc,'off');
        grid(axOcc,'on'); xlabel(axOcc,'Clock cycle'); ylabel(axOcc,'Words');
        title(axOcc,'FIFO occupancy');

        cla(axFlow); stairs(axFlow,out.cycles,out.arrivals,'DisplayName','Arrivals');
        hold(axFlow,'on'); stairs(axFlow,out.cycles,out.departures,'DisplayName','Departures');
        hold(axFlow,'off'); grid(axFlow,'on'); xlabel(axFlow,'Cycle');
        ylabel(axFlow,'Words/cycle'); title(axFlow,'Source and sink');
        legend(axFlow,'Location','best');

        summary.Text=sprintf(['arrival %.2f word/cycle\nservice %.2f word/cycle\n' ...
            'depth %d\nmax occupancy %d\ndrops %d\nmean latency %.1f cycles'], ...
            aS.Value,sS.Value,out.fifoDepth,out.maxOccupancy,out.dropCount,out.estimatedLatencyCycles);
    end
end
