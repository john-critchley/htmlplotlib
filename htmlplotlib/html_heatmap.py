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
    """
    vmin = vmin if vmin is not None else np.min(data)
    vmax = vmax if vmax is not None else np.max(data)
    norm_data = (data - vmin) / (vmax - vmin)
    colors = get_cmap(cmap)

    # Generate the grid HTML
    grid_html = generate_grid_html(norm_data, colors, annot, fmt, linewidths, linecolor, 
                                   square, xticklabels, yticklabels, scale_factor, font_size)

    # Adjust the color bar width to match the grid width
    grid_width = f"{scale_factor * 50 * data.shape[1]}px"
    
    # Generate the color bar HTML
    color_bar_html = generate_color_bar_html(cmap, colors, width=grid_width, height='20px', debug=debug)

    # X-axis label (xlabel) HTML
    xlabel_html = (
        f'<div style="text-align: center; font-weight: bold; margin-bottom: 10px;">{xlabel}</div>'
        if xlabel else ''
    )

    # Y-axis label (ylabel) HTML
    ylabel_html = (
        f'<div style="writing-mode: vertical-rl; transform: rotate(180deg); text-align: center; '
        f'font-weight: bold; margin-right: 10px; height: {scale_factor * 50 * data.shape[0]}px;">{ylabel}</div>'
        if ylabel else ''
    )

    # Combine all components into a flexbox container
    full_html = (
        f'<div style="display: flex; align-items: center; justify-content: center;">'
        f'{ylabel_html}'  # Restored Y-axis label to the left of the heatmap
        f'<div>'
        f'{xlabel_html}'  # xlabel is correctly at the top
        f'{grid_html}'
        f'{color_bar_html}'  # Horizontal color bar below the heatmap
        f'</div>'
        f'</div>'
    )

    if debug and 'html comments' in debug:
        full_html = f'<!-- full_html --> {full_html} <!-- end full_html -->'

    if show:
        ipy_display(HTML(full_html))
    else:
        return full_html

def generate_grid_html(data: np.ndarray, colors: List[str], annot: bool, fmt: str, 
                       linewidths: float, linecolor: str, square: bool, 
                       xticklabels: Optional[Union[List[str], np.ndarray]], 
                       yticklabels: Optional[Union[List[str], np.ndarray]], 
                       scale_factor: float, font_size: int) -> str:
    """
    Generates the HTML for the heatmap grid with annotations and labels.
    """
    num_rows, num_cols = data.shape

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
    for i, row in enumerate(data):
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
                f'{f"{val:{fmt}}" if annot else ""}</td>'
            )
            for j, val in enumerate(row)
        )
        rows_html += f'<tr>{row_html}</tr>'

    # Combine x-axis and y-axis HTML
    table_html = (
        f'<table style="border-collapse: collapse; font-size: {font_size}px; margin: 0;">'
        f'{xtick_html}{rows_html}</table>'
    )

    return table_html

def generate_color_bar(cmap_name: str, width: str = '100%', height: str = '20px',
                       num_labels: int = 6, labels: Optional[List[str]] = None,
                       label_style: Optional[dict] = None, debug: Optional[Union[List[str], Set[str]]] = None,
                       horizontal: bool = True) -> str:
    """
    Generates an HTML-based color bar, either horizontal or vertical, using the provided colormap.

    Parameters:
    - cmap_name (str): Name of the colormap.
    - width (str): CSS width for the color bar (for vertical bar, this is the thickness).
    - height (str): CSS height for the color bar (for horizontal bar, this is the thickness).
    - num_labels (int): Number of labels to display alongside the color bar.
    - labels (Optional[List[str]]): Custom labels for the color bar. Defaults to numeric labels from 0 to 1.
    - label_style (Optional[dict]): CSS styles for the labels.
    - debug (Optional[Union[List[str], Set[str]]]): Debugging options to include comments in the HTML.
    - horizontal (bool): If True, the bar is horizontal; if False, the bar is vertical.

    Returns:
    - str: HTML string for the color bar.
    """
    colors_list = get_cmap(cmap_name)
    label_texts = labels or [f'{tick:.1f}' for tick in np.linspace(0, 1, num_labels)]
    label_css = '; '.join(f'{k}: {v}' for k, v in (label_style or {}).items())

    orientation_style = {
        'bar_dimension': f'width: {width}; height: {height};' if horizontal else f'width: {height}; height: {width};',
        'bar_gradient': 'to right' if horizontal else 'to bottom',
        'label_pos': 'left' if horizontal else 'top',
        'label_transform': 'translate(-50%, -50%)',
        'label_center': '50%' if horizontal else '50%',
        'label_aligned': 'middle' if horizontal else 'middle',
    }

    label_html = (
        f'<span style="position: absolute; {orientation_style["label_pos"]}: {pos * 100:.2f}%; '
        f'{orientation_style["label_pos"]}: {orientation_style["label_center"]}; transform: {orientation_style["label_transform"]}; '
        f'text-align: {orientation_style["label_aligned"]};'
        f'font-size: 10px; color: {calculate_text_color(colors_list[int(pos * (len(colors_list) - 1))])}; {label_css}">{text}</span>'
        for text, pos in zip(label_texts, np.linspace(0, 1, num_labels))
    )

    html = (
        f'<div style="position: relative; {orientation_style["bar_dimension"]} margin-top: 20px; margin-left: 40px;">'
        f'<div style="width: 100%; height: 100%; background: linear-gradient({orientation_style["bar_gradient"]}, {", ".join(colors_list)});"></div>'
        f'{"".join(label_html)}'
        f'</div>'
    )

    if debug and 'html comments' in debug:
        html = f'<!-- generate_color_bar -->\n{html}\n<!-- end generate_color_bar -->'

    return html


def generate_color_bar_html(cmap_name: str, colors: List[str], width: str, height: str, 
                            num_labels: int = 6, debug: Optional[Union[List[str], Set[str]]] = None) -> str:
    """
    Generates an HTML-based color bar using the provided colormap.

    Parameters:
    - cmap_name (str): Name of the colormap.
    - colors (List[str]): List of colors representing the colormap.
    - width (str): CSS width for the color bar.
    - height (str): CSS height for the color bar.
    - num_labels (int): Number of labels to display alongside the color bar.
    - debug (Optional[Union[List[str], Set[str]]] Optional[List[str], Set[str]]): Debugging options to include comments in the HTML.

    Returns:
    - str: HTML string for the color bar.
    """
    label_texts = [f'{tick:.1f}' for tick in np.linspace(0, 1, num_labels)]
    label_positions = np.linspace(0, 1, num_labels)

    label_html = []
    for text, pos in zip(label_texts, label_positions):
        alignment = 'center'
        if pos == 0:
            alignment = 'left'
        elif pos == 1:
            alignment = 'right'
        
        label_html.append(
            f'<span style="position: absolute; left: {pos * 100:.2f}%; '
            f'transform: translate(-{pos * 100:.2f}%, -50%); '
            f'top: 50%; text-align: {alignment}; font-size: 10px; color: {text_color_for_background(colors[int(pos * (len(colors) - 1))])};">'
            f'{text}</span>'
        )

    html = (
        f'<div style="position: relative; width: {width}; height: {height}; margin-top: 20px; margin-left: 40px;">'
        f'<div style="width: 100%; height: 100%; background: linear-gradient(to right, {", ".join(colors)});"></div>'
        f'{"".join(label_html)}'
        f'</div>'
    )

    if debug and 'html comments' in debug:
        html = f'<!-- generate_color_bar_html -->{html}<!-- end generate_color_bar_html -->'

    return html

