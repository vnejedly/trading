import datetime as dt
import plotly.graph_objects as go
import pandas as pd


class CandlePlot:

    name: str
    df: pd.DataFrame

    figure: go.Figure

    def __init__(self, name: str, df: pd.DataFrame):
        self.name = name
        self.df = df.copy()

        self._add_str_time()
        self._create_candle_figure()

    def _add_str_time(self):
        # add a string version of the time as a key for the candlestick chart in order 
        # to avoid the range breaks during weekends when the market is closed
        self.df['s_time'] = [dt.datetime.strftime(time, 'T%Y-%m-%d %H:%M:%S') for time in self.df.index]

    def _create_candle_figure(self) -> go.Figure:
        self.figure = go.Figure()
        self.figure.add_trace(go.Candlestick(
            x=self.df.s_time,
            open=self.df.mid_o,
            high=self.df.mid_h,
            low=self.df.mid_l,
            close=self.df.mid_c,
            name=self.name,
        ))

        return self.figure
    
    def add_trace(
        self, column: str, color: str = None,
        width: int = 1, line_shape: str = 'spline'
    ) -> 'CandlePlot':
        self.figure.add_trace(go.Scatter(
            x=self.df.s_time,
            y=self.df[column],
            line={
                "width": width, 
                "color": color,
            },
            line_shape=line_shape,
            name=column,
        ))

        return self
    
    def update_layout(
        self, nticks: int = None, 
        width: int = None, height: int = 700
    ) -> 'CandlePlot':
        self.figure.update_xaxes(
            nticks=5,
        )

        self.figure.update_layout(
            width=width,
            height=height,
            template='plotly_dark',
            margin=dict(l=0, r=20, t=20, b=10),
            # paper_bgcolor='#2c303c',
            # plot_bgcolor='#2c303c',
        )

        return self
    
    def show(self):
        self.figure.show()
        return self
