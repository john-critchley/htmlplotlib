#!/usr/bin/python

import htmlplotlib
import numpy as np
import importlib

# Define size of the heatmap
sz = 16
xs = sz
ys = sz

# Generate random data for the heatmap
data = np.random.rand(xs, ys)

# Create the HTML heatmap
html = htmlplotlib.html_heatmap(
    data,
    xticklabels=np.vectorize(lambda s: chr(s + ord('A')))(np.arange(xs)),
    yticklabels=np.arange(ys),
    fmt='.2f',
    cmap='coolwarm',
    xlabel='X',
    ylabel='y',
    square=True,
    show=False,
    linewidths=1,
    linecolor='white',
    scale_factor=0.75
)

# Write the generated HTML to a file
with open('test.html', 'w') as fd:
    fd.write(html)


# OR in jupyter sheet show=True
# will return None but insert it into the sheet
