import numpy as np
import plotly.graph_objects as go

from .parents import MultiSeriesPlotPresenter


class VoltageCurrentTimePlotPresenter(MultiSeriesPlotPresenter):
    """
    docstring
    """

    TITLE = "V & I vs. t"

    X_LABEL = "t [h]"

    Y_LABEL = "Ewe [V]"

    Y2_LABEL = "I [mA]"

    bbox_to_anchor = (1.4, 1)

    def extract_data(self, dataset: dict) -> tuple:
        """docstring"""
        x = dataset["time"] / 3600.0
        yv = dataset["Ewe"]
        yi = dataset["I"] * 1000.0
        return (x, yv, yi)

    def plot_series(self, eid: int, dataset: dict) -> None:
        """docstring"""
        x, yv, yi = (np.array(a) for a in self.extract_data(dataset))
        label, color = self.get_series_properties(eid)
        trace1 = go.Scatter(
            x=x,
            y=yv,
            mode="lines",
            name=f"{label}:V",
            line={"color": color},
        )
        self.model.fig.add_trace(trace1)
        self.store_color(trace1)
        trace2 = go.Scatter(
            x=x,
            y=yi,
            mode="lines",
            name=f"{label}:I",
            line={
                "color": color,
                "dash": "dash"
            },
        )
        self.model.fig.add_trace(trace2, secondary_y=True)
