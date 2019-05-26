from PIL import Image, ImageChops
import os
import time
import subprocess

def color_to_string(tuple):
    """ 
    Get a integer tuple format of the current color
    eg. {255, 150, 255}
    """
    if tuple[0] + tuple[1] + tuple[2] <= 3:
        # Color is in float format
        r = str(int(tuple[0]*255))
        g = str(int(tuple[1]*255))
        b = str(int(tuple[2]*255))
        return "{" + r + " " + g + " " + b + "}"
    else:
        # Color is already in integer format
        return "{" + str(tuple[0]) + " " + str(tuple[1]) + " " + str(tuple[2]) + "}"

def color_to_fstring(tuple, strength):
    """
    Get a float tuple format of the current color
    Strength is a float scale to multiply bytearray
    eg. [0.1, 0.2, 0.3]
    """
    if tuple[0] + tuple[1] + tuple[2] <= 3:
        # Color is already in float format
        return "[" + str(tuple[0]) + " " + str(tuple[1]) + " " + str(tuple[2]) + "]"
    else:
        # Color is in integer format
        r = str(round((tuple[0]/255)*strength, 2))
        g = str(round((tuple[1]/255)*strength, 2))
        b = str(round((tuple[2]/255)*strength, 2))
        return "[" + r + " " + g + " " + b + "]"

def cstrf(tuple):
    """Returns a integer format tuple with strings and newline"""
    return '"' + color_to_string(tuple) + '"\n'

def cfstrf(tuple, strength):
    """Returns a float format tuple with strings and newline"""
    return '"' + color_to_fstring(tuple, strength) + '"\n'
    
def convert_png_folder(indir, outdir, format='dxt5', pause=False):
    """Use VTFCmd.exe to convert an entire folder to VTF"""
    search = indir + '\*.png'
    args = ['./VTFCmd.exe', '-folder', search, '-output', outdir, '-format', format, '-silent']
    sp = subprocess.Popen(args)
    if pause:
        sp.wait()
    
def convert_file(infile, format='dxt5', pause=False):
    """Use VTFCmd.exe to convert a single file to VTF"""
    args = ['./VTFCmd.exe', '-file', infile, '-format', format, '-silent']
    sp = subprocess.Popen(args)
    if pause:
        sp.wait()
        
def normalize_colors(colors):
    """
    Normalize an array of colors
    This turns an array of 0-255 colors to 0-1 colors
    """
    normalized = {}
    for c in colors:
        vec = colors[c]
        if vec[0] + vec[1] + vec[2] < 3:
            # It's highly likely that this color is already normal
            # Store it as-is
            normalized[c] = vec
        else:
            # Divide each component by 255
            r = round(vec[0]/255, 4)
            g = round(vec[1]/255, 4)
            b = round(vec[2]/255, 4)
            normalized[c] = (r, g, b)
    
    return normalized
    
def load_palette_file(filename):
    """
    Loads a color palette from a file
    """
    colors = {}
    for line in open(filename):
        # Skip over comments
        if line.startswith('#'):
            continue
            
        # Split the line
        line = line.strip().split(':')
        name = line[0]
        
        if '.' in line[1]:
            # Treat the colors as floats
            color = line[1].split(',')
            colors[name] = (float(color[0]), float(color[1]), float(color[2]))
        else:
            # Treat the colors as integers
            color = line[1].split(',')
            colors[name] = (int(color[0]), int(color[1]), int(color[2]))
    
    return colors
    
def multiply_image(img, color):
    """
    Multiply an image by a given color
    This is probably terribly inefficient but hey
    Color needs to be a normalized form (0-1)
    """
    channels = img.split()
    new_chan = [None]*4
    
    for k in range(0, 3):
        new_chan[k] = channels[k].point(lambda i: ((i/255)*color[k])*255)
    new_chan[3] = channels[3]
    img = Image.merge(img.mode, new_chan)
    return img
    
def process_vmt(outfile, texname, lines, colname, color):
    """
    Process a given VMT
    This is pretty simple currently:
     - rename the basetexture to have the colour included
     - check for colorable envmap property & add that if needed
    """
    # Check for colorable envmap property
    new_lines = lines.copy()
    
    color_env_map = False
    color_env_map_strength = 1
    if new_lines[0].strip().startswith('ColorEnvMap'):
        color_env_map_strength = float(lines[0].strip().split(':')[1])
        color_env_map = True
        new_lines.pop(0)
       
    # Copy lines from template and add color
    new_lines[2] = new_lines[2].replace(texname, texname + '_' + colname)
        
    # If applicable, add a special colorizer for the envmap
    # messy line i know i'm sorry
    if color_env_map:
        print(color, cfstrf(color, color_env_map_strength))
        new_lines.insert(-1, '    $envmaptint     ' + cfstrf(color, color_env_map_strength))
    
    # Write the output to the new file
    # directory_fout + file_name + '_' + key + '.vmt'
    with open(outfile, 'w') as vmt:
        for line in new_lines:
            vmt.write(line)
            
def process_color_mask(base, mask, color):
    """
    Colorize an image with mask and return the result
    """
    new_mask = multiply_image(mask, color)
    new_image = base.copy()
    new_image.paste(new_mask, mask=new_mask)
    return new_image

def process_color_base(base, color):
    """
    Colorize an image with no mask and return the result
    """
    return multiply_image(base, color)
    
def file_preprocess(filename, fdir):
    """
    Handles some common preprocessing tasks
     - Converts normal maps to VTF
     - Converts envmapmask to VTF
     - Loads mask images if applicable
     
    Returns if the image has a mask, and the mask image if so
    """
    # Convert normal map to VTF (if it exists)
    if os.path.isfile('norms/' + filename + '.png'):
        convert_file('norms/' + filename + '.png', format='bgr888', pause=True)
        os.rename('norms/' + filename + '.vtf', fdir + filename + '_norm.vtf')
        
    # Convert envmapmask to VTF (if it exists)
    if os.path.isfile('envmapmasks/' + filename + '.png'):
        convert_file('envmapmasks/' + filename + '.png', format='dxt5', pause=True)
        os.rename('envmapmasks/' + filename + '.vtf', fdir + filename + '_envmapmask.vtf')
    
    # Check for a mask image and return the result
    try:
        mask_image = Image.open('masks/' + filename + '.png').convert('RGBA')
        return True, mask_image
    except:
        return False, None
    
def file_preprocess_mask(filename):
    """
    Similar to the above function
    Does no VTF conversions, only checks for masks
    """
    # Check for a mask image and return the result
    try:
        mask_image = Image.open('masks/' + filename + '.png').convert('RGBA')
        return True, mask_image
    except:
        return False, None
        
def file_preprocess_overlay(filename):
    """
    Checks if the image has an overlay
    Returns if the overlay exists and the image if so
    """
    try:
        overlay_image = Image.open('overlays/' + filename + '.png').convert('RGBA')
        return True, overlay_image
    except:
        return False, None
    
if __name__ == "__main__":
    colors = load_palette_file('palettes/flatui.txt')
    colors = normalize_colors(colors)
    
    # Get the timestamp
    # This is used to create unique directories for each project
    timestamp = int(time.time())
    
    # Register & create directories
    directory_pout = 'output/png-' + str(timestamp) + '/'
    directory_fout = 'output/final-' + str(timestamp) + '/'
    
    # Create the directory if it doesn't exist
    try:
        os.mkdir('output')
    except:
        pass
    
    os.mkdir(directory_pout)
    os.mkdir(directory_fout)
    
    for path in os.listdir('vmt'):
        file_name, ext = os.path.splitext(path)
        print('Starting processing of', file_name)
        
        # Load the VMT for the image
        lines = []
        with open('vmt/' + file_name + '.vmt', 'r') as base:
            lines = base.readlines()
        
        # Load the image to edit
        base_image = Image.open('input/' + file_name + '.png').convert('RGBA')
        mask_mode, mask_image = file_preprocess(file_name, directory_fout)
        overlay_mode, overlay_image = file_preprocess_mask(file_name)
        
        # Iterate over each color and create a new .vmt & colorized .png for each
        print('Generating colored PNGs')
        for key in colors:
            # Create the VMT
            process_vmt(directory_fout + file_name + '_' + key + '.vmt', file_name, lines, key, colors[key])
            
            # Colorize and save the image
            colorized = None
            if mask_mode:
                colorized = process_color_mask(base_image, mask_image, colors[key])
            else:
                colorized = process_color_base(base_image, colors[key])
            
            # Apply overlay if applicable
            if overlay_mode:
                overlay_image.copy()
                colorized.paste(overlay_image, mask=overlay_image)
            
            colorized.save(directory_pout + file + '_' + key + '.png')
    
    # Finish off by converting the folder to VTF
    print('Converting recolors to VTF')
    convert_png_folder(directory_pout, directory_fout, pause=True)
    print('Done!')
    
    # Print finish message when everything is processed
    print('Finished all files. Output:', directory_fout)