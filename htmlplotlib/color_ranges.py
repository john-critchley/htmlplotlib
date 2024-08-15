#!/usr/bin/python
# color_ranges.py

COLOR_RANGES = {
    'rocket': ['#0d0890', '#6a00b0', '#cb4680', '#ed6d50', '#fca640', '#fbf919'],
    'blues': ['#f7fbff', '#dfeeff', '#c8d8ff', '#a8c0ff', '#6aa1ff', '#2180ff'],
    'greens': ['#f7fcf5', '#e6f5e0', '#c8e9c0', '#a2d99b', '#74c476', '#239045'],
    'reds': ['#fff5f5', '#fee0e0', '#fcb8b8', '#fb7d7d', '#f44336', '#d32f2f'],
    'greys': ['#f5f5f5', '#e0e0e0', '#bdbdbd', '#9e9e9e', '#757575', '#424242'],
    
    # Approximated "lava" colormap
    'lava': ['#0d0887', '#350498', '#5402a3', '#7000a9', '#8b0ea7', '#a82296',
             '#c43d83', '#db5d70', '#f07d5f', '#fb9f47', '#fdca26'],
    
    # Rainbow colormap reversed, adjusted brightness in yellow-green range
    'rainbow': ['#ff0000', '#ff4400', '#ff8800', '#ddaa00', '#88cc00',
                '#44dd44', '#00ddaa', '#00aaff', '#0088ff', '#0044ff',
                '#0000ff'],
    
    # Pastel rainbow derived from Rainbow
    'pastel_rainbow': ['#f08080', '#f09080', '#f0b080', '#e0c080', '#d0d080',
                       '#c0e0c0', '#b0e0d0', '#a0d0f0', '#a0b0f0', '#90a0f0',
                       '#8080f0'],
    
    # Additional colormaps
    'viridis': ['#440154', '#482576', '#414487', '#35608D', '#2A788E',
                '#21918C', '#22A884', '#43BF71', '#7AD151', '#DCE319'],
    'magma': ['#000004', '#180f3d', '#4B0C6B', '#781C6D', '#A52C60', '#CF4446',
              '#ED6925', '#FB9A06', '#F7D03C', '#FCFDA4'],
    
    # Cool-to-Warm colormap
    'coolwarm': ['#3b4cc0', '#6690e1', '#9cb9e3', '#c8d8d6', '#e7c0a2',
                 '#f58e6e', '#d63c5a'],
    
    # Inferno colormap (similar to magma but more red-yellow)
    'inferno': ['#000004', '#1c1044', '#4f0a71', '#7b0d59', '#a11737',
                '#cb2c1a', '#ed6925', '#fdab5b', '#f8e565'],
    
    # Plasma colormap (vivid colors)
    'plasma': ['#0d0887', '#5b02a3', '#9a179b', '#cc4778', '#ed6d47', '#fca336',
               '#eff821'],
}

if __name__=="__main__":
    print(*COLOR_RANGES, sep='\n')

