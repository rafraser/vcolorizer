from PIL import Image, ImageChops
import os
import time
import subprocess

# Get a integer tuple format of the current color
# eg. {255, 150, 255}
def color_to_string(tuple):
    return "{" + str(tuple[0]) + " " + str(tuple[1]) + " " + str(tuple[2]) + "}"

# Get a float tuple format of the current color
# Strength is a float scale to multiply bytearray
# eg. [0.1, 0.2, 0.3]
def color_to_fstring(tuple, strength):
    r = str(round( (tuple[0]/255)*strength, 2))
    g = str(round( (tuple[1]/255)*strength, 2))
    b = str(round( (tuple[2]/255)*strength, 2))
    return "[" + r + " " + g + " " + b + "]"

# Returns a integer format tuple with strings and newline
def cstrf(tuple):
    return '"' + color_to_string(tuple) + '"\n'

# Returns a float format tuple with strings and newline
def cfstrf(tuple, strength):
    return '"' + color_to_fstring(tuple, strength) + '"\n'
    
def convert_png_folder(indir, outdir, format='dxt5', pause=False):
    search = indir + '\*.png'
    args = ['./VTFCmd.exe', '-folder', search, '-output', outdir, '-format', format, '-silent']
    sp = subprocess.Popen(args)
    if pause:
        sp.wait()
    
def convert_file(infile, format='dxt5', pause=False):
    args = ['./VTFCmd.exe', '-file', infile, '-format', format, '-silent']
    sp = subprocess.Popen(args)
    if pause:
        sp.wait()

# Define colors to add
colors = {
    "orange": (230, 120, 23),
    "white": (255, 255, 255),
    "silver": (222, 232, 235),
    "gray": (182, 182, 182),
    "tan": (210, 180, 140),
    "navy": (26, 46, 73),
    "purple": (107, 96, 158),
    "green": (136, 212, 83),
    "blue": (100, 179, 211),
    "orange": (230, 120, 23),
    "night": (47, 54, 64),
    "yellow": (251, 197, 49),
    "red": (231, 76, 60),
    
    "flat_green": (76, 209, 55),
    "flat_blue": (0, 168, 255),
    "flat_purple": (156, 136, 255),
    "flat_yellow": (251, 197, 49),
    "flat_red": (232, 65, 24),
    "flat_pink": (255, 159, 243),
    "flat_orange": (230, 126, 34),
    "flat_lime": (123, 237, 159),
    "flat_watermelon": (255, 107, 129),
    "flat_clouds": (236, 240, 241),
    "flat_gray": (149, 165, 166),
    "flat_fuchsia": (179, 55, 113),
    "flat_turquoise": (18, 203, 196),
    "flat_violet": (95, 39, 205),
    "flat_sky": (126, 214, 223)
}

color_images = {}

# Get the timestamp
# This is used to create unique directories for each project
timestamp = int(time.time())

# Register & create directories
directory_pout = 'png-' + str(timestamp) + '/'
directory_fout = 'final-' + str(timestamp) + '/'
os.mkdir(directory_pout)
os.mkdir(directory_fout)

# Precache each color image
for key in colors:
    color_images[key] = Image.new('RGB', (512, 512), colors[key])

for path in os.listdir('vmt'):
    file_name, ext = os.path.splitext(path)
    lines = []
    
    # Load the image to edit
    base_image = Image.open('input/' + file_name + '.png').convert('RGB')
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
            convert_file('norms/' + file_name + '.png', format='bgr888', pause=True)
            os.rename('norms/' + file_name + '.vtf', directory_fout + file_name + '_norm.vtf')
            
        # Convert envmapmask to VTF (if it exists)
        if os.path.isfile('envmapmasks/' + file_name + '.png'):
            convert_file('envmapmasks/' + file_name + '.png', format='dxt5', pause=True)
            os.rename('envmapmasks/' + file_name + '.vtf', directory_fout + file_name + '_envmapmask.vtf')
            
    
    # Iterate over each color and create a new .vmt & colorized .png for each
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
        color_image = color_images[key]       
        if mask_mode:
            # Tint mask image
            new_mask = ImageChops.multiply(color_image, mask_image)
            new_image = base_image.copy()
            new_image.paste(new_mask, mask=new_mask)
            new_image.save(directory_pout + file_name + '_' + key + '.png')
        else:
            # Tint the image directly (no mask)
            new_image = ImageChops.multiply(color_image, base_image)
            new_image.save(directory_pout + file_name + '_' + key + '.png')
    
    # Finish off by converting to VTF
    convert_png_folder(directory_pout, directory_fout)