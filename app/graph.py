import plotly.express as px
from plotly.graph_objs._figure import Figure
from pandas import DataFrame


def figure(df: DataFrame, x: str, y: str, target: str) -> Figure:
    """Create a scatterplot in the style of the dark web theme.

    Keyword Arguments:
    df -- the dataframe where the data is stored.
    x -- the name of the variable to plot along the x-axis.
    y -- the name of the variable to plot along the y-axis.
    target -- the name of the variable to group each point onto a color.
    """

    df.sort_values([x, y, target], axis=0, inplace=True)
    title = ''.join([y, "by", x, "for", target])

    fig = px.scatter(df, x=x, y=y, color=target,
                     title=title,
                     hover_data=df,
                     template='plotly_dark')

    fig.update_layout(
        font_color="#aaaaaa",
        plot_bgcolor="#252525",
        paper_bgcolor="#252525",
        title_x=0.5,
        title_font_size=24,

        hoverlabel=dict(
            font_color="white",
            bgcolor="#2b2b2b",
            font_size=12,
            font_family="Monaco, sans-serif"
        )
    )

    fig.update_xaxes(gridcolor='#555', linecolor='#555',
                     zerolinecolor='#dedede', zerolinewidth=1)
    fig.update_yaxes(gridcolor='#555', linecolor='#555',
                     zerolinecolor='#dedede', zerolinewidth=1)

    return fig
