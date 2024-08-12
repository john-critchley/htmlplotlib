import numpy as np

def linear_gradient(colors: list, n: int) -> list:
    """Generates a linear gradient of `n` colors between the provided colors."""
    gradient = []
    for i in range(n):
        idx = i * (len(colors) - 1) / (n - 1)
        lower, upper = int(np.floor(idx)), int(np.ceil(idx))
        mix = idx - lower
        lower_color = np.array([int(colors[lower][j:j + 2], 16) for j in (1, 3, 5)])
        upper_color = np.array([int(colors[upper][j:j + 2], 16) for j in (1, 3, 5)])
        mixed_color = np.round((1 - mix) * lower_color + mix * upper_color).astype(int)
        hex_color = ''.join(f'{c:02x}' for c in mixed_color)
        gradient.append(f'#{hex_color}')
    return gradient

