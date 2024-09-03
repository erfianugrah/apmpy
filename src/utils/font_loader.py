import tkinter.font as tkFont
import logging

def load_custom_font(font_path, font_name, sizes):
    """
    Load a custom font for use in tkinter, with fallback to default font.
    
    :param font_path: Path to the font file
    :param font_name: Name to register the font under
    :param sizes: List of sizes to load the font in
    :return: Dictionary of loaded fonts
    """
    fonts = {}
    try:
        for size in sizes:
            font = tkFont.Font(font=tkFont.Font(family="TkDefaultFont", size=size))
            font.configure(family=font_name)
            fonts[size] = font
        
        # This call seems to be necessary to register the font
        tkFont.families()
        
        logging.info(f"Custom font '{font_name}' loaded successfully")
    except Exception as e:
        logging.error(f"Error loading custom font: {e}")
        logging.info("Falling back to default font")
        for size in sizes:
            fonts[size] = tkFont.Font(family="TkDefaultFont", size=size)
    
    return fonts

def get_font(custom_fonts, size, weight="normal"):
    """
    Get a font of the specified size, with fallback to default font.
    
    :param custom_fonts: Dictionary of custom fonts
    :param size: Desired font size
    :param weight: Font weight (e.g., "normal", "bold")
    :return: Font object
    """
    if size in custom_fonts:
        font = custom_fonts[size]
        if weight == "bold":
            font = font.copy()
            font.configure(weight="bold")
        return font
    else:
        logging.warning(f"Font size {size} not found in custom fonts. Using default font.")
        return tkFont.Font(family="TkDefaultFont", size=size, weight=weight)
