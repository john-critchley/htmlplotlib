import numpy as np
from IPython.display import HTML, display as ipy_display
from typing import Union, List, Optional, Set
from .color_ranges import COLOR_RANGES
from .gradient import linear_gradient

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

def generate_horizontal_color_bar(cmap_name: str, width: str = '100%',
                                  height: str = '20px', num_labels: int = 6,
                                  labels: Optional[List[str]] = None,
                                  label_style: Optional[dict] = None,
                                  debug: Optional[Union[List[str], Set[str]]] = None) -> str:
    """
    Generates an HTML-based horizontal color bar using the provided colormap.

    Parameters:
    - cmap_name (str): Name of the colormap.
    - width (str): CSS width for the color bar.
    - height (str): CSS height for the color bar.
    - num_labels (int): Number of labels to display alongside the color bar.
    - labels (Optional[List[str]]): Custom labels for the color bar.
    - label_style (Optional[dict]): CSS styles for the labels.
    - debug (Optional[Union[List[str], Set[str]]]): Debugging options to include comments in the HTML.

    Returns:
    - str: HTML string for the color bar.
    """
    colors = ', '.join(get_cmap(cmap_name))
    label_texts = labels or [f'{tick:.1f}' for tick in np.linspace(0, 1, num_labels)]
    label_css = '; '.join(f'{k}: {v}' for k, v in (label_style or {}).items())

    label_html = (
        f'<span style="position: absolute; left: {pos * 100:.2f}%; top: 50%; transform: translate(-50%, -50%); '
        f'font-size: 10px; color: {text_color_for_background(get_cmap(cmap_name)[int(pos * (len(get_cmap(cmap_name)) - 1))])}; {label_css}">{text}</span>'
        for text, pos in zip(label_texts, np.linspace(0, 1, num_labels))
    )

    html = (
        f'<div style="position: relative; width: {width}; height: {height}; margin-top: 20px; margin-left: 40px;">'
        f'<div style="width: 100%; height: 100%; background: linear-gradient(to right, {colors});"></div>'
        f'{"".join(label_html)}'
        f'</div>'
    )

    if debug and 'html comments' in debug:
        html = (
            f'<!-- generate_horizontal_color_bar -->\n{html}\n<!-- end generate_horizontal_color_bar -->'
        )

    return html

def html_heatmap(data: np.ndarray,
                 xticklabels: Optional[Union[List[str], np.ndarray]] = None,
                 yticklabels: Optional[Union[List[str], np.ndarray]] = None,
                 annot: bool = True, fmt: str = '.2f', cmap: str = 'rocket',
                 vmin: Optional[float] = None, vmax: Optional[float] = None,
                 square: bool = False, linewidths: float = 0,  # Default to 0 to hide borders
                 linecolor: str = 'black',
                 mask: Optional[np.ndarray] = None,
                 xlabel: Optional[str] = None,
                 ylabel: Optional[str] = None,
                 show: bool = True,
                 font_size: int = 12,
                 scale_factor: float = 1.0,
                 debug: Optional[Union[List[str], Set[str]]] = None) -> Optional[str]:
    """
    Creates an HTML-based heatmap with a horizontal color bar using CSS for rendering in Jupyter notebooks.

    Parameters:
    - data (np.ndarray): A 2D NumPy array of shape (n, m) containing the data values to be plotted as a heatmap.
    - xticklabels (Optional[Union[List[str], np.ndarray]]): List or array of labels for the x-axis (columns).
    - yticklabels (Optional[Union[List[str], np.ndarray]]): List or array of labels for the y-axis (rows).
    - annot (bool): If True, write the data value in each cell.
    - fmt (str): String formatting code to format the annotation text.
    - cmap (str): The colormap to use. Should be one of the keys in COLOR_RANGES.
    - vmin (Optional[float]): The minimum value of the colormap. If None, the minimum value in the data is used.
    - vmax (Optional[float]): The maximum value of the colormap. If None, the maximum value in the data is used.
    - square (bool): If True, set the aspect ratio of the heatmap cells to be square.
    - linewidths (float): Width of the lines that divide each cell. Default is 0 to hide borders.
    - linecolor (str): Color of the lines that divide each cell.
    - mask (Optional[np.ndarray]): A 2D boolean array where True entries will be hidden from the heatmap.
    - xlabel (Optional[str]): Label for the x-axis, displayed at the top of the table.
    - ylabel (Optional[str]): Label for the y-axis, displayed to the left of the table, rotated vertically.
    - show (bool): If True, display the heatmap. If False, return the HTML string.
    - font_size (int): Font size for the heatmap text.
    - scale_factor (float): Factor to scale the size of the heatmap cells.
    - debug (Optional[Union[List[str], Set[str]]] Optional[List[str], Set[str]]): Debugging options to include comments in the HTML.

    Returns:
    - Optional[str]: If show is False, returns the HTML string for the heatmap; otherwise, None.
    """
    vmin = vmin if vmin is not None else np.min(data)
    vmax = vmax if vmax is not None else np.max(data)
    norm_data = (data - vmin) / (vmax - vmin)

    num_rows, num_cols = data.shape
    colors = get_cmap(cmap)

    # Determine cell width and height
    cell_width = cell_height = f'{scale_factor * 50}px'
    if not square:
        cell_height = f'{scale_factor * 30}px'  # Adjust height to be rectangular

    # HTML for x-axis labels
    xtick_html = ''
    if xticklabels is not None:
        xtick_html = (
            '<tr><td style="background-color: #f0f0f0;"></td>'
            + ''.join(
                f'<th style="text-align: center; padding: 5px; background-color: #f0f0f0;">{label}</th>'
                for label in xticklabels
            )
            + '</tr>'
        )

    # HTML for y-axis labels and the data grid
    rows_html = ''
    for i, row in enumerate(norm_data):
        y_label = (
            f'<th style="padding: 5px; text-align: center; background-color: #f0f0f0;">{yticklabels[i]}</th>'
            if yticklabels is not None else ''
        )
        row_html = y_label + ''.join(
            (
                f'<td style="background-color: {colors[int(val * (len(colors) - 1))]}; '
                f'border: {linewidths}px solid {linecolor}; text-align: center; '
                f'width: {cell_width}; height: {cell_height}; '
                f'color: {text_color_for_background(colors[int(val * (len(colors) - 1))])};">'
                f'{f"{data[i,j]:{fmt}}" if annot else ""}</td>'
            )
            for j, val in enumerate(row)
        )
        rows_html += f'<tr>{row_html}</tr>'

    # Combine x-axis and y-axis HTML
    table_html = (
        f'<table style="border-collapse: collapse; font-size: {font_size}px; margin: 0;">'
        f'{xtick_html}{rows_html}</table>'
    )

    if debug and 'html comments' in debug:
        table_html = f'<!-- table_html -->\n{table_html}\n<!-- end table_html -->'

    # Adjust the color bar width to match the grid width
    grid_width = f"{scale_factor * 50 * num_cols}px"
    color_bar_width = grid_width

    # Color bar HTML
    color_bar_html = generate_horizontal_color_bar(
        cmap, width=color_bar_width, height='20px', debug=debug
    )

    # X-axis label (xlabel) HTML
    xlabel_html = (
        f'<div style="text-align: center; font-weight: bold; margin-bottom: 10px;">{xlabel}</div>'
        if xlabel else ''
    )

    # Y-axis label (ylabel) HTML
    ylabel_html = (
        f'<div style="writing-mode: vertical-rl; transform: rotate(180deg); text-align: center; '
        f'font-weight: bold; margin-right: 10px; height: {scale_factor * 50 * num_rows}px;">{ylabel}</div>'
        if ylabel else ''
    )

    # Combine all components into a flexbox container
    full_html = (
        f'<div style="display: flex; align-items: center; justify-content: center;">'
        f'{ylabel_html}'  # Restored Y-axis label to the left of the heatmap
        f'<div>'
        f'{xlabel_html}'  # xlabel is correctly at the top
        f'{table_html}'
        f'{color_bar_html}'  # Horizontal color bar below the heatmap
        f'</div>'
        f'</div>'
    )

    if debug and 'html comments' in debug:
        full_html = f'<!-- full_html -->\n{full_html}\n<!-- end full_html -->'

    if show:
        ipy_display(HTML(full_html))
    else:
        return full_html

