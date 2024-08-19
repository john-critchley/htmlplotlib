import numpy as np
from typing import Union, List, Optional, Set
from .color_ranges import COLOR_RANGES
from .gradient import linear_gradient
from collections import namedtuple

DataTuple = namedtuple('DataTuple', ['original', 'normalized'])

def text_color_for_background(bg_color: str) -> str:
    rgb = np.array([int(bg_color[i:i + 2], 16) for i in (1, 3, 5)])
    brightness = np.mean(rgb) / 255  # Simplified brightness check
    return '#FFFFFF' if brightness < 0.5 else '#000000'

def calculate_nice_range(data_min: float, data_max: float) -> (float, float):
    range_span = data_max - data_min
    magnitude = 10 ** np.floor(np.log10(range_span))
    nice_min = np.floor(data_min / magnitude) * magnitude
    nice_max = np.ceil(data_max / magnitude) * magnitude
    return nice_min, nice_max

def get_cmap(cmap_name: str, n: int = 256) -> List[str]:
    if cmap_name in COLOR_RANGES:
        return linear_gradient(COLOR_RANGES[cmap_name], n)
    raise ValueError(f"Color map '{cmap_name}' is not available in custom maps.")

def generate_grid_html(data_with_norm, colors, annot, fmt, linewidths, linecolor, square,
                       xticklabels, yticklabels, scale_factor, font_size):
    rows_html = ''
    xtick_html = ''
    if xticklabels is not None:
        xtick_html = (
            '<tr>' +
            ('<th style="background-color: #f0f0f0;"></th>' if yticklabels is not None else '') +
            ''.join(
                f'<th style="text-align: center; padding: 5px; background-color: #f0f0f0;">{label}</th>'
                for label in xticklabels
            ) +
            '</tr>'
        )

    for i, row in enumerate(data_with_norm):
        y_label = (
            f'<th style="padding: 5px; text-align: center; background-color: #f0f0f0;">{yticklabels[i]}</th>'
            if yticklabels is not None else ''
        )
        row_html = y_label + ''.join(
            (
                f'<td style="background-color: {colors[int(val.normalized * (len(colors) - 1))]}; '
                f'border: {linewidths}px solid {linecolor}; text-align: center; '
                f'width: {scale_factor * 50}px; height: {scale_factor * 50}px; '
                f'color: {text_color_for_background(colors[int(val.normalized * (len(colors) - 1))])};">'
                f'{f"{val.original:{fmt}}" if annot else ""}</td>'
            )
            for val in row
        )
        rows_html += f'<tr>{row_html}</tr>'

    table_html = (
        f'<table style="border-collapse: collapse; font-size: {font_size}px; margin: 0;">'
        f'{xtick_html}{rows_html}</table>'
    )

    return table_html

def generate_color_bar_html(cmap_name, colors, width='100%', height='20px',
                            orientation='horizontal', debug=None, vmin=0, vmax=1,
                            cbar_fmt='.1f', num_labels=5):
    gradient_direction = "to right" if orientation == 'horizontal' else "to top"
    label_positions = np.linspace(vmin, vmax, num_labels)
    label_texts = [f'{tick:{cbar_fmt}}' for tick in label_positions]

    color_bar_html = (
        f'<div style="position: relative; width: {width}; height: {height}; margin-top: 20px; margin-left: 40px;">'
        f'<div style="width: 100%; height: 100%; background: linear-gradient({gradient_direction}, {", ".join(colors)});"></div>'
    )

    for i, (pos, text) in enumerate(zip(np.linspace(0, 100, num_labels), label_texts)):
        bg_color = colors[int(pos / 100 * (len(colors) - 1))]
        text_color = text_color_for_background(bg_color)

        if orientation == 'horizontal':
            label_style = f'left: {pos}%; top: 50%; transform: translate(-{pos}%, -50%);'
        else:
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

    if vmin is None or vmax is None:
        data_min, data_max = calculate_nice_range(np.min(data), np.max(data))
        vmin = vmin if vmin is not None else data_min
        vmax = vmax if vmax is not None else data_max
    else:
        vmin, vmax = calculate_nice_range(vmin, vmax)

    data_plus = [[DataTuple(val, (val - vmin) / (vmax - vmin)) for val in row] for row in data]

    colors = get_cmap(cmap)

    orientation = cbar_kws.get('orientation', 'horizontal') if cbar_kws else 'horizontal'

    grid_html = generate_grid_html(data_plus, colors, annot, fmt, linewidths, linecolor,
                                   square, xticklabels, yticklabels, scale_factor, font_size)

    color_bar_size = f"{scale_factor * 50 * data.shape[1]}px" if orientation == 'horizontal' else f"{scale_factor * 50 * data.shape[0]}px"
    color_bar_html = generate_color_bar_html(cmap, colors,
                                             width=color_bar_size if orientation == 'horizontal' else '20px',
                                             height='20px' if orientation == 'horizontal' else color_bar_size,
                                             orientation=orientation, debug=debug, vmin=vmin, vmax=vmax, cbar_fmt=cbar_fmt)

    xlabel_html = f'<div style="text-align: center; font-weight: bold; margin-bottom: 10px;">{xlabel}</div>' if xlabel else ''

    ylabel_html = (
        f'<div style="writing-mode: vertical-rl; transform: rotate(180deg); text-align: center; '
        f'font-weight: bold; margin-right: 10px; height: {scale_factor * 50 * data.shape[0]}px;">{ylabel}</div>'
        if ylabel else ''
    )

    if orientation == 'horizontal':
        full_html = (
            f'<div style="display: flex; align-items: center; justify-content: center; flex-direction: column;">'
            f'{xlabel_html}'
            f'<div style="display: flex; align-items: center; justify-content: center;">'
            f'{ylabel_html}'
            f'{grid_html}'
            f'</div>'
            f'{color_bar_html}'
            f'</div>'
        )
    else:
        full_html = (
            f'{xlabel_html}'
            f'<div style="display: flex; align-items: center; justify-content: center;">'
            f'{ylabel_html}'
            f'{grid_html}'
            f'{color_bar_html}'
            f'</div>'
        )

    if show:
        from IPython.display import display, HTML
        display(HTML(full_html))
    else:
        return full_html

