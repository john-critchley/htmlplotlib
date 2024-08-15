#!/usr/bin/python

import numpy as np
import htmlplotlib
import argparse

# Default values for xs and ys
xs = ys = 16

def main(
    data,
    xs=xs,
    ys=ys,
    xticklabels=None,
    yticklabels=None,
    fmt='.2f',
    cmap='coolwarm',
    xlabel='X',
    ylabel='y',
    square=True,
    show=False,
    linewidths=1,
    linecolor='white',
    scale_factor=0.75
):
    # If xticklabels or yticklabels are not provided, generate them based on xs and ys
    if xticklabels is None:
        xticklabels = np.vectorize(lambda s: chr(s + ord('A')))(np.arange(xs))
    if yticklabels is None:
        yticklabels = np.arange(ys)

    return htmlplotlib.html_heatmap(
        data,
        xticklabels=xticklabels,
        yticklabels=yticklabels,
        fmt=fmt,
        cmap=cmap,
        xlabel=xlabel,
        ylabel=ylabel,
        square=square,
        show=show,
        linewidths=linewidths,
        linecolor=linecolor,
        scale_factor=scale_factor
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an HTML heatmap.")

    # Add arguments for xs and ys
    parser.add_argument("--xs", type=int, default=xs, help="Number of X-axis labels")
    parser.add_argument("--ys", type=int, default=ys, help="Number of Y-axis labels")
    
    # Add other arguments
    parser.add_argument("--fmt", type=str, default='.2f', help="String format for labels")
    parser.add_argument("--cmap", type=str, default='coolwarm', help="Colormap for heatmap")
    parser.add_argument("--xlabel", type=str, default='X', help="Label for X-axis")
    parser.add_argument("--ylabel", type=str, default='y', help="Label for Y-axis")

    # Use store_true for square and store_false for rectangle
    parser.add_argument("--square", action="store_true", default=True, help="Enforce square cells")
    parser.add_argument("--rectangle", dest="square", action="store_false", help="Do not enforce square cells (rectangle mode)")
    
    parser.add_argument("--show", action="store_true", default=False, help="Show the heatmap immediately")
    parser.add_argument("--linewidths", type=float, default=1, help="Width of the lines that will divide each cell")
    parser.add_argument("--linecolor", type=str, default='white', help="Color of the lines that will divide each cell")
    parser.add_argument("--scale_factor", type=float, default=0.75, help="Scale factor for the heatmap")

    args = parser.parse_args()

    # Convert argparse.Namespace to a dictionary, filtering out None values (i.e., not provided on command line)
    argdict = {k: v for k, v in vars(args).items() if v is not None}

    # You would need to provide the `data` argument as well, possibly from a different source.
    # For the example, assuming `data` is available:
    data = np.random.rand(argdict.get('xs', xs), argdict.get('ys', ys))  # Generate example data based on xs and ys

    # Call main with filtered command line arguments and print the result
    result = main(data, **argdict)
    print(result)
