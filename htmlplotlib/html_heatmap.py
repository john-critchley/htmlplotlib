import numpy as np
from IPython.display import HTML, display
from typing import Union, List, Optional, Set
from .color_ranges import COLOR_RANGES
from .gradient import linear_gradient

def text_color_for_background(bg_color: str) -> str:
    rgb = np.array([int(bg_color[i:i + 2], 16) for i in (1, 3, 5)])
    brightness = colorsys.rgb_to_hsv(*(rgb / 255.0))[-1]
    return '#FFFFFF' if brightness < 0.5 else '#000000'

def calculate_nice_range(data_min: float, data_max: float) -> (float, float):
    """
    Calculates a 'nice' range for the data by extending the range to round numbers.

    Parameters:
    - data_min (float): The minimum value in the data.
    - data_max (float): The maximum value in the data.

    Returns:
    - (float, float): A tuple of (nice_min, nice_max) representing the extended range.
    """
    range_span = data_max - data_min

    # Calculate the order of magnitude of the range
    magnitude = 10 ** np.floor(np.log10(range_span))

    # Calculate the nice minimum and maximum
    nice_min = np.floor(data_min / magnitude) * magnitude
    nice_max = np.ceil(data_max / magnitude) * magnitude

    return nice_min, nice_max

def get_cmap(cmap_name: str, n: int = 256) -> List[str]:
    """
    Returns a color map based on the provided name.

    Parameters:
    - cmap_name (str): Name of the colormap. Must be a key in COLOR_RANGES.
    - n (int): Number of colors in the colormap gradient.

    Returns:
    - List[str]: List of color hex values representing the colormap.
    """
    if cmap_name in COLOR_RANGES:
        return linear_gradient(COLOR_RANGES[cmap_name], n)
    raise ValueError(f"Color map '{cmap_name}' is not available in custom maps.")

def text_color_for_background(bg_color: str) -> str:
    """
    Determine the appropriate text color (black or white) based on the brightness of the background color.

    Parameters:
    - bg_color (str): Hexadecimal color string for the background.

    Returns:
    - str: Hexadecimal color string for the text, either '#FFFFFF' (white) or '#000000' (black).
    """
    rgb = np.array([int(bg_color[i:i + 2], 16) for i in (1, 3, 5)])
    brightness = np.mean(rgb) / 255  # Simplified brightness check
    return '#FFFFFF' if brightness < 0.5 else '#000000'

def generate_grid_html(data, colors, annot, fmt, linewidths, linecolor, square,
                       xticklabels, yticklabels, scale_factor, font_size):
    # Start building the HTML for the grid
    rows_html = ''

    # Start the header row
    xtick_html = ''
    if xticklabels is not None:
        # Create the header row for xticklabels, including an empty cell for yticklabels
        xtick_html = (
            '<tr>' +
            ('<th style="background-color: #f0f0f0;"></th>' if yticklabels is not None else '') +
            ''.join(
                f'<th style="text-align: center; padding: 5px; background-color: #f0f0f0;">{label}</th>'
                for label in xticklabels
            ) +
            '</tr>'
        )

    for i, row in enumerate(data):
        y_label = (
            f'<th style="padding: 5px; text-align: center; background-color: #f0f0f0;">{yticklabels[i]}</th>'
            if yticklabels is not None else ''
        )
        row_html = y_label + ''.join(
            (
                f'<td style="background-color: {colors[int((val - np.min(data)) / (np.max(data) - np.min(data)) * (len(colors) - 1))]}; '
                f'border: {linewidths}px solid {linecolor}; text-align: center; '
                f'width: {scale_factor * 50}px; height: {scale_factor * 50}px; '
                f'color: {text_color_for_background(colors[int((val - np.min(data)) / (np.max(data) - np.min(data)) * (len(colors) - 1))])};">'
                f'{f"{val:{fmt}}" if annot else ""}</td>'
            )
            for val in row
        )
        rows_html += f'<tr>{row_html}</tr>'

    # Combine the header and rows HTML
    table_html = (
        f'<table style="border-collapse: collapse; font-size: {font_size}px; margin: 0;">'
        f'{xtick_html}{rows_html}</table>'
    )

    return table_html

def generate_color_bar_html(cmap_name, colors, width='100%', height='20px',
                            orientation='horizontal', debug=None, vmin=0, vmax=1,
                            cbar_fmt='.1f', num_labels=5):
    """
    Generates the HTML for a color bar with a gradient, either horizontal or vertical.

    Parameters:
    - cmap_name (str): Name of the colormap.
    - colors (List[str]): List of colors in the colormap.
    - width (str): Width of the color bar.
    - height (str): Height of the color bar.
    - orientation (str): Orientation of the color bar, either 'horizontal' or 'vertical'.
    - debug (Optional[Union[List[str], Set[str]]] Optional[List[str], Set[str]]): Debug options.
    - vmin (float): Minimum value for the color bar labels.
    - vmax (float): Maximum value for the color bar labels.
    - cbar_fmt (str): Format for the color bar labels.
    - num_labels (int): Number of labels on the color bar.

    Returns:
    - str: HTML string for the color bar.
    """

    # Determine gradient direction based on orientation
    gradient_direction = "to right" if orientation == 'horizontal' else "to top"

    # Generate the label texts
    label_positions = np.linspace(vmin, vmax, num_labels)
    label_texts = [f'{tick:{cbar_fmt}}' for tick in label_positions]

    # Create the HTML for the color bar
    color_bar_html = (
        f'<div style="position: relative; width: {width}; height: {height}; margin-top: 20px; margin-left: 40px;">'
        f'<div style="width: 100%; height: 100%; background: linear-gradient({gradient_direction}, {", ".join(colors)});"></div>'
    )

    # Add labels to the color bar
    for i, (pos, text) in enumerate(zip(np.linspace(0, 100, num_labels), label_texts)):
        # Calculate the color based on the background
        bg_color = colors[int(pos / 100 * (len(colors) - 1))]
        text_color = text_color_for_background(bg_color)

        if orientation == 'horizontal':
            # Adjusting horizontal alignment based on position
            label_style = f'left: {pos}%; top: 50%; transform: translate(-{pos}%, -50%);'
        else:
            # Adjusting vertical alignment based on position
            label_style = f'top: {100 - pos}%; left: 50%; transform: translate(-50%, -{100 - pos}%);'

        color_bar_html += (
            f'<span style="position: absolute; {label_style}; font-size: 10px; color: {text_color};">{text}</span>'
        )

    color_bar_html += '</div>'

    return color_bar_html

def html_heatmap(data, xticklabels=None, yticklabels=None, annot=True, fmt='.2f',
                 cmap='viridis', vmin=None, vmax=None, square=False,
                 linewidths=1, linecolor='white', mask=None,
                 xlabel='', ylabel='', show=False, font_size=10, scale_factor=1.0,
                 cbar_kws=None, cbar_fmt='.1f', debug=False):
    """
    Create an HTML heatmap visualization.

    Parameters:
    - data (np.ndarray): The data to visualize.
    - xticklabels (List[str]): Labels for the x-axis.
    - yticklabels (List[str]): Labels for the y-axis.
    - annot (bool): Annotate each cell with the numeric value.
    - fmt (str): Format for annotating numeric values.
    - cmap (str): Colormap name.
    - vmin (float): Minimum value for colormap normalization.
    - vmax (float): Maximum value for colormap normalization.
    - square (bool): Enforce square cells.
    - linewidths (float): Width of the lines separating cells.
    - linecolor (str): Color of the lines separating cells.
    - mask (np.ndarray): Boolean array indicating where to mask cells.
    - xlabel (str): Label for the x-axis.
    - ylabel (str): Label for the y-axis.
    - show (bool): Display the heatmap immediately.
    - font_size (int): Font size for labels.
    - scale_factor (float): Scaling factor for heatmap size.
    - cbar_kws (dict): Keyword arguments for color bar.
    - cbar_fmt (str): Format for color bar labels.
    - debug (bool): Enable debug information.

    Returns:
    - str: HTML string representing the heatmap.
    """

    # If vmin or vmax are not provided, use the data's min/max
    if vmin is None or vmax is None:
        data_min, data_max = calculate_nice_range(np.min(data), np.max(data))
        vmin = vmin if vmin is not None else data_min
        vmax = vmax if vmax is not None else data_max
    else:
        vmin, vmax = calculate_nice_range(vmin, vmax)

    # Normalize data for color mapping only
    norm_data = (data - vmin) / (vmax - vmin)

    # Get the colormap
    colors = get_cmap(cmap)

    # Determine orientation from cbar_kws
    orientation = cbar_kws.get('orientation', 'horizontal') if cbar_kws else 'horizontal'

    # Generate the grid HTML using original data values for display, normalized data for colors
    grid_html = generate_grid_html(data, colors, annot, fmt, linewidths, linecolor,
                                   square, xticklabels, yticklabels, scale_factor, font_size)

    # Generate the color bar HTML
    color_bar_size = f"{scale_factor * 50 * data.shape[1]}px" if orientation == 'horizontal' else f"{scale_factor * 50 * data.shape[0]}px"
    color_bar_html = generate_color_bar_html(cmap, colors,
                                             width=color_bar_size if orientation == 'horizontal' else '20px',
                                             height='20px' if orientation == 'horizontal' else color_bar_size,
                                             orientation=orientation, debug=debug, vmin=vmin, vmax=vmax, cbar_fmt=cbar_fmt)

    # X-axis label HTML
    xlabel_html = f'<div style="text-align: center; font-weight: bold; margin-bottom: 10px;">{xlabel}</div>' if xlabel else ''

    # Y-axis label HTML
    ylabel_html = (
        f'<div style="writing-mode: vertical-rl; transform: rotate(180deg); text-align: center; '
        f'font-weight: bold; margin-right: 10px; height: {scale_factor * 50 * data.shape[0]}px;">{ylabel}</div>'
        if ylabel else ''
    )

    # Combine all components into a flexbox container
    if orientation == 'horizontal':
        full_html = (
            f'<div style="display: flex; align-items: center; justify-content: center; flex-direction: column;">'
            f'{xlabel_html}'  # X-axis label at the top of the grid
            f'<div style="display: flex; align-items: center; justify-content: center;">'
            f'{ylabel_html}'  # Y-axis label to the left of the heatmap
            f'{grid_html}'  # Heatmap grid
            f'</div>'
            f'{color_bar_html}'  # Color bar
            f'</div>'
        )
    else:  # Vertical
        full_html = (
            f'{xlabel_html}'  # X-axis label at the top
            f'<div style="display: flex; align-items: center; justify-content: center;">'
            f'{ylabel_html}'  # Y-axis label to the left of the heatmap
            f'{grid_html}'  # Heatmap grid
            f'{color_bar_html}'  # Color bar to the right
            f'</div>'
        )

    if show:
        from IPython.display import display, HTML
        display(HTML(full_html))
    else:
        return full_html

