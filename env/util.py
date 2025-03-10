import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image


# calculate stock price volatility before current day step, over lookback days
# input: data - nxm daily stock prices (m stocks over n days)
# input: current_step -  day's step index
# input: lookback - desired volatility lookback window
# output: 1xm volatility of stocks within lookback window
def calculate_volatility(data, current_step, lookback):
    if current_step in (0, 1):
        # at steps 0,1 we don't have any volatility to compute yet
        return np.ones((1, data.shape[1])) / data.shape[1]

    lookback_start = max(current_step + 1 - lookback, 0)
    lookback_end = current_step + 1
    perc_change_window = data[lookback_start:lookback_end]  # P[t-1] - latest lookback prices excluding today

    perc_change_mean = np.mean(perc_change_window, axis=0)
    variance = (1 / (lookback - 1)) * np.sum(np.power(perc_change_window - perc_change_mean, 2), axis=0)  # price variance
    return np.sqrt(variance)

  
def plot_portfolio(portfolio, total_gains, title=None, dims=(15.24, 5.12), holdings_portion=0.75):
    holdings_dims = (dims[0] * holdings_portion, dims[1])
    meta_dims = (dims[0] * (1.0 - holdings_portion), dims[1])
    holdings_plot_img = plot_holdings(portfolio.stock_w, dims=holdings_dims, title=title)
    meta_plot_img = plot_portfolio_meta(portfolio, total_gains, dims=meta_dims)

    return concat_images([holdings_plot_img, meta_plot_img])


def plot_portfolio_meta(portfolio, total_gains, dims, y_limit=15000):
    x = ['current_gains', 'total_gains']
    y = [portfolio.curr_gains(), total_gains]
    plt.figure()
    fig = sns.barplot(x=x, y=y).get_figure()
    fig.set_size_inches(dims)
    ax = plt.axes()
    ax.set(ylim=(0, y_limit))
    plt.close()

    return fig_to_img(fig)

  
def plot_holdings(stock_w, dims, title=None, y_limit=100):
    x = np.array(range(stock_w.shape[0]))
    y = stock_w.squeeze()

    plt.figure()
    fig = sns.barplot(x=x, y=y).get_figure()
    fig.set_size_inches(dims)

    ax = plt.axes()
    if title is not None:
        ax.set_title(title)
    ax.set(ylim=(0, y_limit))

    img = fig_to_img(fig)

    plt.close()

    return img


def concat_images(images):
    total_width = sum([img.width for img in images])
    height = images[0].height

    new_im = Image.new('RGB', (total_width, height))

    x_cursor = 0
    for img in images:
        new_im.paste(img, (x_cursor, 0))
        x_cursor += img.width

    return new_im


def fig_to_img(fig):
    canvas = FigureCanvas(fig)
    canvas.draw()  # draw the canvas, cache the renderer

    return Image.frombytes('RGB', canvas.get_width_height(),
                                canvas.tostring_rgb())


