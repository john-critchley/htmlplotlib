import numpy as np
from IPython.display import HTML, display
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
                f'<td style="background-color: {colors[int(val * (len(colors) - 1))]}; '
                f'border: {linewidths}px solid {linecolor}; text-align: center; '
                f'width: {scale_factor * 50}px; height: {scale_factor * 50}px; '
                f'color: {text_color_for_background(colors[int(val * (len(colors) - 1))])};">'
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

def generate_color_bar_html(cmap_name: str, colors: List[str], width: str, height: str,
                            num_labels: int = 6, debug: Optional[Union[List[str], Set[str]]] = None,
                            orientation: str = 'horizontal') -> str:
    """
    Generates an HTML-based color bar using the provided colormap, either horizontally or vertically.

    Parameters:
    - cmap_name (str): Name of the colormap.
    - colors (List[str]): List of colors representing the colormap.
    - width (str): CSS width for the color bar (for vertical orientation, this is the thickness).
    - height (str): CSS height for the color bar (for horizontal orientation, this is the thickness).
    - num_labels (int): Number of labels to display alongside the color bar.
    - debug (Optional[Union[List[str], Set[str]]] Optional[List[str], Set[str]]): Debugging options to include comments in the HTML.
    - orientation (str): Either 'horizontal' or 'vertical'. Determines the orientation of the color bar.

    Returns:
    - str: HTML string for the color bar.
    """
    label_texts = [f'{tick:.1f}' for tick in np.linspace(0, 1, num_labels)]
    label_positions = np.linspace(0, 1, num_labels)

    if orientation == 'horizontal':
        bar_gradient = 'to right'
        primary_pos = 'left'
        secondary_pos = 'top'
        translate_primary = '-50%'  # Center labels horizontally
        translate_secondary = '-50%'  # Center labels vertically

        def calculate_translation(pos):
            return f'translateX(-{pos * 100:.2f}%)'

    else:
        bar_gradient = 'to bottom'
        primary_pos = 'top'
        secondary_pos = 'left'
        translate_primary = '-50%'  # Center labels horizontally
        translate_secondary = '-50%'  # Center labels vertically

        def calculate_translation(pos):
            return f'translateY(-{pos * 100:.2f}%)'

    # Generate label HTML
    label_html = []
    for text, pos in zip(label_texts, label_positions):
        if orientation == 'horizontal':
            label_html.append(
                f'<span style="position: absolute; {primary_pos}: {pos * 100:.2f}%; '
                f'transform: translate(-{pos * 100:.2f}%, {translate_secondary}); '
                f'{secondary_pos}: 50%; font-size: 10px; color: {text_color_for_background(colors[int(pos * (len(colors) - 1))])};">'
                f'{text}</span>'
            )
        else:
            label_html.append(
                f'<span style="position: absolute; {primary_pos}: {pos * 100:.2f}%; '
                f'transform: translate({translate_primary}, -{pos * 100:.2f}%); '
                f'{secondary_pos}: 50%; font-size: 10px; color: {text_color_for_background(colors[int(pos * (len(colors) - 1))])};">'
                f'{text}</span>'
            )

    # Generate the final HTML for the color bar
    html = (
        f'<div style="position: relative; width: {width}; height: {height}; margin-top: 20px; margin-left: 40px;">'
        f'<div style="width: 100%; height: 100%; background: linear-gradient({bar_gradient}, {", ".join(colors)});"></div>'
        f'{"".join(label_html)}'
        f'</div>'
    )

    if debug and 'html comments' in debug:
        html = f'<!-- generate_color_bar_html -->{html}<!-- end generate_color_bar_html -->'

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
                 cbar_kws: Optional[dict] = None,
                 debug: Optional[Union[List[str], Set[str]]] = None) -> Optional[str]:
    
    # Normalize the data for color mapping
    vmin = vmin if vmin is not None else np.min(data)
    vmax = vmax if vmax is not None else np.max(data)
    norm_data = (data - vmin) / (vmax - vmin)

    # Get the colormap
    colors = get_cmap(cmap)

    # Determine orientation from cbar_kws
    orientation = cbar_kws.get('orientation', 'horizontal') if cbar_kws else 'horizontal'

    # Generate the grid HTML
    grid_html = generate_grid_html(norm_data, colors, annot, fmt, linewidths, linecolor,
                                   square, xticklabels, yticklabels, scale_factor, font_size)

    # Y-axis label (ylabel) HTML
    ylabel_html = (
        f'<div style="writing-mode: vertical-rl; transform: rotate(180deg); text-align: center; '
        f'font-weight: bold; margin-right: 10px; height: {scale_factor * 50 * data.shape[0]}px;">{ylabel}</div>'
        if ylabel else ''
    )

    # X-axis label (xlabel) HTML
    xlabel_html = (
        f'<div style="text-align: center; font-weight: bold; margin-top: 10px;">{xlabel}</div>'
        if xlabel else ''
    )

    # Generate the color bar HTML
    color_bar_size = f"{scale_factor * 50 * data.shape[1]}px" if orientation == 'horizontal' else f"{scale_factor * 50 * data.shape[0]}px"
    color_bar_html = generate_color_bar_html(cmap, colors,
                                             width=color_bar_size if orientation == 'horizontal' else '20px',
                                             height='20px' if orientation == 'horizontal' else color_bar_size,
                                             orientation=orientation, debug=debug)

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

    # If debug is enabled, wrap the full HTML in comments
    if debug and 'html comments' in debug:
        full_html = f'<!-- full_html -->\n{full_html}\n<!-- end full_html -->'

    if show:
        display(HTML(full_html))
    else:
        return full_html

