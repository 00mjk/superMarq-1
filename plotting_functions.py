import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom", fontsize=12)
    cbar.ax.tick_params(labelsize=10)

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels, fontsize=8) # regular fontsize is 12
    ax.set_yticklabels(row_labels, fontsize=8)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    ax.spines[:].set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)
    
    # Rotate the 3 typical features separately
    for t in ax.get_xticklabels()[-3:]:
        t.set_horizontalalignment('left')
        t.set_rotation(35)

    return im, cbar


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=("black", "white"),
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A pair of colors.  The first is used for values below a threshold,
        the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts


def regression_plot(device, feature, feature_df, score_df):
    print(device, feature)
    
    application_features = feature_df.loc[:, feature]
    scores = score_df.loc[device, :]

    x, y, stddevs = [], [], []
    ec_benchmarks = []
    for benchmark in scores.index:
        if isinstance(scores.loc[benchmark], tuple):
            if 'code' in benchmark:
                ec_benchmarks.append(
                    (
                    application_features.loc[benchmark],
                    scores.loc[benchmark][0],
                    scores.loc[benchmark][1]
                    )
                )
                continue
            x.append(application_features.loc[benchmark])
            y.append(scores.loc[benchmark][0])
            stddevs.append(scores.loc[benchmark][1])


    fig, ax = plt.subplots(dpi=150)
    
    # Regression excluding error-correction benchmarks
    X = np.array(x)[:, np.newaxis]
    Y = np.array(y)
    
    model = LinearRegression().fit(X, Y)
    correlation_without = model.score(X, Y)

    ax.errorbar(X, Y, yerr=stddevs, marker='o', linestyle='none', color='grey', ms=4, elinewidth=1, capsize=4)
    ax.plot(X, model.predict(X), color='tab:orange', ls='-', label=r'w/o EC ($R^2={:.3f}$)'.format(correlation_without))
    
    # Regression including error-correction benchmarks
    x_extended = x + [p[0] for p in ec_benchmarks]
    y_extended = y + [p[1] for p in ec_benchmarks]
    X = np.array(x_extended)[:, np.newaxis]
    Y = np.array(y_extended)
    
    model = LinearRegression().fit(X, Y)
    correlation_with = model.score(X, Y)
    
    ax.errorbar([p[0] for p in ec_benchmarks], [p[1] for p in ec_benchmarks],
                yerr=[p[2] for p in ec_benchmarks], marker='x', linestyle='none',
                color='tab:blue', ms=6, elinewidth=1, capsize=4, label='EC Benchmarks')
    ax.plot(X, model.predict(X), color='tab:blue', ls='-', label=r'w/ EC ($R^2={:.3f}$)'.format(correlation_with))
    
    ax.set_ylabel('Benchmark Score', fontsize=16)
    ax.set_xlabel(f'{feature} feature', fontsize=16)
    ax.set_title(f'{device} performance correlation', fontsize=16)
    ax.legend()
    plt.tight_layout()
    #plt.savefig('figures/toronto_performance_correlation.pdf')
    plt.show()
    plt.close()
