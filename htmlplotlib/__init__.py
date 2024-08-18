"""
htmlplotlib - A Python package for generating HTML-based heatmaps and gradients.

This package provides tools for creating customizable and interactive HTML visualizations,
focusing on heatmaps with various color maps and gradient options.

Modules:
- color_ranges: Contains predefined color ranges for various color maps.
- gradient: Provides functions to generate linear gradients between colors.
- html_heatmap: Main module for generating heatmaps in HTML format.

Usage Example:
    import htmlplotlib
    import numpy as np

    data = np.random.rand(16, 16)
    html = htmlplotlib.html_heatmap(
        data,
        xticklabels=np.vectorize(lambda s: chr(s + ord('A')))(np.arange(16)),
        yticklabels=np.arange(16),
        fmt='.2f',
        cmap='coolwarm',
        xlabel='X',
        ylabel='y',
        square=True,
        show=False,
        linewidths=0,
        linecolor='white',
        scale_factor=0.75
    )
    with open('heatmap.html', 'w') as f:
        f.write(html)

Repo:
    https://github.com/john-critchley/htmlplotlib
"""

from .color_ranges import COLOR_RANGES
from .gradient import linear_gradient
from .html_heatmap import html_heatmap

__VERSION__=0.1

