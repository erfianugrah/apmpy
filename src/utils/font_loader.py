import os
import tkinter.font as tkFont

def load_custom_font(font_path, font_name, sizes):
    """
    Load a custom font for use in tkinter.
    
    :param font_path: Path to the font file
    :param font_name: Name to register the font under
    :param sizes: List of sizes to load the font in
    :return: Dictionary of loaded fonts
    """
    fonts = {}
    for size in sizes:
        fonts[size] = tkFont.Font(font=tkFont.Font(family="TkDefaultFont", size=size))
        fonts[size].configure(family=font_name)
    
    tkFont.families()  # This call seems to be necessary to register the font
    return fonts

# Usage example:
# font_path = os.path.join('assets', 'fonts', 'IosevkaTermNerdFont-Regular.ttf')
# custom_fonts = load_custom_font(font_path, "Iosevka Term Nerd Font", [12, 14, 20, 24])
