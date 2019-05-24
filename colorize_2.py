from PIL import Image, ImageChops
import os
import time
import subprocess

def color_to_string(tuple):
    """ 
    Get a integer tuple format of the current color
    eg. {255, 150, 255}
    """
    return "{" + str(tuple[0]) + " " + str(tuple[1]) + " " + str(tuple[2]) + "}"

def color_to_fstring(tuple, strength):
    """
    Get a float tuple format of the current color
    Strength is a float scale to multiply bytearray
    eg. [0.1, 0.2, 0.3]
    """
    r = str(round( (tuple[0]/255)*strength, 2))
    g = str(round( (tuple[1]/255)*strength, 2))
    b = str(round( (tuple[2]/255)*strength, 2))
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
            normalized[c] = (vec[0]/255, vec[1]/255, vec[2]/255)
    
    return normalized
    
def load_palette_file(filename):
    """
    Loads a color palette from a file
    """
    colors = {}
    for line in open(filename):
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
    lines = []
    print('Starting processing of', file_name)
    
    # Load the image to edit
    base_image = Image.open('input/' + file_name + '.png').convert('RGBA')
    color_env_map = False
    color_env_map_strength = 1
    
    # Load the files from the file
    with open('vmt/' + file_name + '.vmt', 'r') as base:
        lines = base.readlines()
        
        # Check for colorable envmap property
        if lines[0].strip().startswith('ColorEnvMap'):
            color_env_map_strength = float(lines[0].strip().split(':')[1])
            color_env_map = True
            lines.pop(0)
            
        # Check for mask image for colorizing
        try:
            mask_image = Image.open('masks/' + file_name + '.png').convert('RGBA')
            mask_mode = True
        except Exception as e:
            mask_mode = False
            pass
            
        # Convert normal map to VTF (if it exists)
        if os.path.isfile('norms/' + file_name + '.png'):
            print('Converting normal map to VTF...')
            convert_file('norms/' + file_name + '.png', format='bgr888', pause=True)
            os.rename('norms/' + file_name + '.vtf', directory_fout + file_name + '_norm.vtf')
            
        # Convert envmapmask to VTF (if it exists)
        if os.path.isfile('envmapmasks/' + file_name + '.png'):
            print('Converting envmapmask map to VTF...')
            convert_file('envmapmasks/' + file_name + '.png', format='dxt5', pause=True)
            os.rename('envmapmasks/' + file_name + '.vtf', directory_fout + file_name + '_envmapmask.vtf')
            
    
    # Iterate over each color and create a new .vmt & colorized .png for each
    print('Generating colored PNGs')
    for key in colors:
        # Copy lines from template and add color
        new_lines = lines.copy()
        new_lines[2] = new_lines[2].replace(file_name, file_name + '_' + key)
        
        # If applicable, add a special colorizer for the envmap
        if color_env_map:
            new_lines.insert(-1, '    $envmaptint     ' + cfstrf(colors[key], color_env_map_strength))
        
        # Write the output to the new file
        with open(directory_fout + file_name + '_' + key + '.vmt', 'w') as vmt:
            for line in new_lines:
                vmt.write(line)
                
        # Apply the color tinting
        if mask_mode:
            # Tint mask image
            new_mask = multiply_image(mask_image, colors[key])
            new_image = base_image.copy()
            new_image.paste(new_mask, mask=new_mask)
            new_image.save(directory_pout + file_name + '_' + key + '.png')
        else:
            # Tint the image directly (no mask)
            new_image = multiply_image(base_image, colors[key])
            new_image.save(directory_pout + file_name + '_' + key + '.png')
    
    # Finish off by converting to VTF
    print('Converting recolors to VTF')
    convert_png_folder(directory_pout, directory_fout, pause=True)
    print('Done!')

# Print finish message when everything is processed
print('Finished all files. Output:', directory_fout)