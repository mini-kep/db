from io import BytesIO
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from datetime import date
import pandas as pd


start = date(1998, 12, 31)
end = date(2017, 12, 31)
DEFAULT_TIMERANGE = start, end
SPLINE_GPARAMS = {'timerange': DEFAULT_TIMERANGE,
                  'figsize': (2, 0.6),
                  'style': 'ggplot',
                  'facecolor': 'white',
                  'auto_x': False,
                  'axis_on': False}


def get_data_for_spline(query_data):
    """
    Convert query to dictionary
    Args:
        DatapointsOperations query.
    Returns:
        dict(
            "x":[],
            "y":[]
        )
    """
    return dict(x=[item.date for item in query_data],
                y=[item.value for item in query_data])


def make_png(query_data):
    """
    Args:
        DatapointsOperations query.
    Returns:
        Png image.
    """
    data_dict = get_data_for_spline(query_data)
    return create_png_from_dict(data_dict, SPLINE_GPARAMS)


def create_png_from_dict(data, params):
    """
    Create Spline png image from dict.
    Args:
        dict(
            "x":[],
            "y":[]
        )
    Returns:
        Png image.
    """
    plt.style.use(params["style"])
    fig = plt.figure(figsize=params["figsize"])
    dfm = pd.DataFrame(data)
    dfm.set_index('x', inplace=True)
    axes = fig.add_subplot(1, 1, 1, facecolor=params["facecolor"])
    axes.set_xlim(params['timerange'])
    axes.plot(dfm)
    if params['auto_x']:
        fig.autofmt_xdate()
    if not params['axis_on']:
        plt.axis('off')
    fig.autofmt_xdate()
    plt.axis('off')
    canvas = FigureCanvas(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    return png_output.getvalue()
