import numpy as np
import colorsys
from typing import Union, List, Optional, Set
from .color_ranges import COLOR_RANGES

def get_cmap(cmap_name: str, n: int = 256) -> List[str]:
    """
    Returns a list of colors based on the provided colormap name using linear interpolation.

    Parameters:
    - cmap_name (str): Name of the colormap.
    - n (int): Number of colors in the colormap gradient.

    Returns:
    - List[str]: List of color hex values representing the colormap.
    """
    if cmap_name not in COLOR_RANGES:
        raise ValueError(f"Colormap '{cmap_name}' not found in COLOR_RANGES")

    colors = COLOR_RANGES[cmap_name]

    if len(colors) == n:
        return colors
    elif len(colors) < n:
        # Interpolate if the number of requested colors exceeds the available colors
        indices = np.linspace(0, len(colors) - 1, n)
        interpolated_colors = []
        for i in indices:
            low_idx = int(np.floor(i))
            high_idx = int(np.ceil(i))
            low_color = colors[low_idx]
            high_color = colors[high_idx]
            if low_idx == high_idx:
                interpolated_colors.append(low_color)
            else:
                # Simple linear interpolation in hex
                interpolated_color = linear_interpolate_hex(low_color, high_color, i - low_idx)
                interpolated_colors.append(interpolated_color)
        return interpolated_colors
    else:
        # Downsample if the number of requested colors is less than available
        indices = np.linspace(0, len(colors) - 1, n, dtype=int)
        return [colors[i] for i in indices]

def linear_interpolate_hex(color1, color2, t):
    """Linearly interpolate between two hex colors."""
    c1_r, c1_g, c1_b = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    c2_r, c2_g, c2_b = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)

    r = int(c1_r + (c2_r - c1_r) * t)
    g = int(c1_g + (c2_g - c1_g) * t)
    b = int(c1_b + (c2_b - c1_b) * t)

    return f'#{r:02x}{g:02x}{b:02x}'


def text_color_for_background(bg_color: str) -> str:
    """
    Determines the appropriate text color (black or white) based on the brightness of the background color
    using the HSV (Hue, Saturation, Value) color model.

    Parameters:
    - bg_color (str): Hexadecimal color string for the background (e.g., '#RRGGBB').

    Returns:
    - str: Hexadecimal color string for the text, either '#FFFFFF' (white) or '#000000' (black).
    """
    if not isinstance(bg_color, str) or len(bg_color) != 7 or not bg_color.startswith('#'):
        raise ValueError(f"Invalid color format: '{bg_color}'. Expected format: '#RRGGBB'.")

    try:
        rgb = np.array([int(bg_color[i:i + 2], 16) for i in (1, 3, 5)])
        r, g, b = rgb / 255.0
        brightness = colorsys.rgb_to_hsv(r, g, b)[-1]
        return '#FFFFFF' if brightness < 0.5 else '#000000'
    except ValueError as e:
        raise ValueError(f"Error parsing color '{bg_color}': {e}")

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
    - debug (Optional[Union[List[str], Set[str]]] Optional[List[str], Set[str]]): Debugging options to include comments in the HTML.
    - horizontal (bool): If True, the bar is horizontal; if False, the bar is vertical.

    Returns:
    - str: HTML string for the color bar.
    """

    # Retrieve the list of colors from the colormap
    colors_list = get_cmap(cmap_name)

    # Generate default labels if none are provided
    label_texts = labels or [f'{tick:.1f}' for tick in np.linspace(0, 1, num_labels)]
    # Combine any custom label styles into a single CSS string
    label_css = '; '.join(f'{k}: {v}' for k, v in (label_style or {}).items())

    # Generate the HTML for the labels, adjusting for left, center, and right alignment
    label_html = ''
    for i, (text, pos) in enumerate(zip(label_texts, np.linspace(0, 1, num_labels))):
        if i == 0:  # Leftmost label
            alignment = 'left: 0%; text-align: left;'
            transform = 'transform: translateY(-50%);' if horizontal else 'transform: translateX(-50%);'
        elif i == num_labels - 1:  # Rightmost label
            alignment = 'right: 0%; text-align: right;'
            transform = 'transform: translateY(-50%);' if horizontal else 'transform: translateX(-50%);'
        else:  # Middle labels
            alignment = f'left: {pos * 100:.2f}%; text-align: center;'
            transform = 'transform: translateX(-50%) translateY(-50%);' if horizontal else 'transform: translateY(-50%) translateX(-50%);'

        label_html += (
            f'<span style="position: absolute; {alignment} top: 50%; {transform} font-size: 10px; '
            f'color: {text_color_for_background(colors_list[int(pos * (len(colors_list) - 1))])}; {label_css}">{text}</span>'
        )

    # Assemble the full HTML for the color bar
    html = (
        f'<div style="position: relative; {width}; height: {height}; margin-top: 20px; margin-left: 40px;">'
        f'<div style="width: 100%; height: 100%; background: linear-gradient(to right, {", ".join(colors_list)});"></div>'
        f'{label_html}'
        f'</div>'
    )

    # Add HTML comments if debugging is enabled
    if debug and 'html comments' in debug:
        html = f'<!-- generate_color_bar -->\n{html}\n<!-- end generate_color_bar -->'

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
    Creates an HTML-based heatmap with X and Y axis labels.
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
        xtick_html = '<tr>'
        if yticklabels is not None:
            # Add an empty cell at the top-left corner if yticklabels are present
            xtick_html += '<td style="background-color: #f0f0f0;"></td>'
        xtick_html += ''.join(
            f'<th style="text-align: center; padding: 5px; background-color: #f0f0f0;">{label}</th>'
            for label in xticklabels
        )
        xtick_html += '</tr>'

    # HTML for y-axis labels and the data grid
    rows_html = ''
    for i, row in enumerate(norm_data):
        row_html = ''
        if yticklabels is not None:
            # Add y-axis label for each row
            row_html += (
                f'<th style="padding: 5px; text-align: center; background-color: #f0f0f0;">{yticklabels[i]}</th>'
            )
        row_html += ''.join(
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

    # Generate color bar HTML with labels centered on the bar
    color_bar_html = generate_color_bar(
        cmap_name=cmap,
        width=color_bar_width,
        height='20px',
        num_labels=6,
        label_style={'font-size': '10px'},
        horizontal=True,
        debug=debug
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
        f'{ylabel_html}'  # Y-axis label on the left
        f'<div>'
        f'{xlabel_html}'  # X-axis label at the top
        f'{table_html}'
        f'{color_bar_html}'  # Horizontal color bar below the heatmap, with labels centered
        f'</div>'
        f'</div>'
    )

    if debug and 'html comments' in debug:
        full_html = f'<!-- full_html -->\n{full_html}\n<!-- end full_html -->'

    if show:
        from IPython.display import HTML, display as ipy_display
        ipy_display(HTML(full_html))
    else:
        return full_html

