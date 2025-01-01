
# Plot theme settings
PLOT_SETTINGS = {
    'background_fill_color': '#1a1a1a',
    'border_fill_color': '#1a1a1a',
    'outline_line_color': '#404040',
    'text_color': '#e0e0e0',
    'axis_label_text_color': '#e0e0e0',
    'major_label_text_color': '#e0e0e0',
    'grid_line_color': '#404040',
    'grid_line_alpha': 0.3
}

# Layout settings
LAYOUT_SETTINGS = {
    'sizing_mode': 'stretch_both',
    'styles': {
        'background-color': '#202020',
    }
}

def apply_plot_theme(plot):
    """Apply the dark theme to a plot"""
    plot.background_fill_color = PLOT_SETTINGS['background_fill_color']
    plot.border_fill_color = PLOT_SETTINGS['border_fill_color']
    plot.outline_line_color = PLOT_SETTINGS['outline_line_color']
    
    # Set text colors
    plot.title.text_color = PLOT_SETTINGS['text_color']
    plot.xaxis.axis_label_text_color = PLOT_SETTINGS['axis_label_text_color']
    plot.yaxis.axis_label_text_color = PLOT_SETTINGS['axis_label_text_color']
    plot.xaxis.major_label_text_color = PLOT_SETTINGS['major_label_text_color']
    plot.yaxis.major_label_text_color = PLOT_SETTINGS['major_label_text_color']
    
    # Set grid colors
    plot.grid.grid_line_color = PLOT_SETTINGS['grid_line_color']
    plot.grid.grid_line_alpha = PLOT_SETTINGS['grid_line_alpha']
