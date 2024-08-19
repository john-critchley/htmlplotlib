"""
htmlplotlib - A Python package for generating HTML-based heatmaps and color bars.

This package provides tools for creating customizable and interactive HTML visualizations,
focusing on heatmaps with various color maps and gradient options. The main functionality
is to generate HTML output, providing flexibility for web integration and use in reports.

Modules:
- color_ranges: Contains predefined color ranges for various color maps.
- gradient: Provides functions to generate linear gradients between colors.
- html_heatmap: Main module for generating heatmaps and color bars in HTML format.

Main Features:
- Generate heatmaps with a wide variety of color maps.
- Create customizable color bars that can be displayed horizontally or vertically.
- Support for labels on both axes, including automatic generation.
- Options for fine-tuning appearance, including cell size, line width, and more.
- Seamless integration with Jupyter Notebooks.

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
        xlabel='X Axis',
        ylabel='Y Axis',
        square=True,
        show=False,
        linewidths=1,
        linecolor='white',
        scale_factor=0.75,
        cbar_kws={'orientation': 'horizontal'}
    )
    with open('heatmap.html', 'w') as f:
        f.write(html)

Repo:
    https://github.com/john-critchley/htmlplotlib

Version: 0.2.3
"""

from .color_ranges import COLOR_RANGES
from .gradient import linear_gradient
from .html_heatmap import html_heatmap

__version__ = "0.2.3"

