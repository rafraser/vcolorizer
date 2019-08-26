from colorize_2 import *

def process_vmt_template(outfile, texname, lines, colname, color):
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
    new_lines[2] = new_lines[2].replace('/NAME', '/' + texname + '_' + colname)
        
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

# Get user input
palette = input('Palette to use: ')
files = input('Files to colorize (comma-seperated, no extension): ')
vmt_file = input('VMT Template: ')

# Load the color palette
if not palette.endswith('.txt'):
    palette = palette + '.txt'
colors = load_palette_file('palettes/' + palette)
colors = normalize_colors(colors)

# Create output directories with timestamp
timestamp = int(time.time())
directory_pout = 'output/png-' + str(timestamp) + '/'
directory_fout = 'output/final-' + str(timestamp) + '/'

# Make the folders
try:
    os.mkdir('output')
except:
    pass
os.mkdir(directory_pout)
os.mkdir(directory_fout)

# Load the template VMT
lines = []
with open('vmt/' + vmt_file + '.vmt', 'r') as base:
    lines = base.readlines()

files = files.split(',')
for file in files:
    print('Processing:', file + '.vmt')
        
    # Load the image to edit
    base_image = Image.open('input/' + file + '.png').convert('RGBA')
    
    # Preprocess the file - converts any other files if needed
    mask_mode, mask_image = file_preprocess(file, directory_fout)
    overlay_mode, overlay_image = file_preprocess_overlay(file)
    
    for key in colors:
        # Create the VMT
        process_vmt_template(directory_fout + file + '_' + key + '.vmt', file, lines, key, colors[key])
        
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
    
# Convert the png directory to VTF
convert_png_folder(directory_pout, directory_fout, pause=True)