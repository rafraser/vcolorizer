from colorize_2 import *

# Get user input
palette = input('Palette to use: ')
files = input('Files to colorize (comma-seperated, no extension): ')

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

files = files.split(',')
for file in files:
    if not os.path.isfile('vmt/' + file + '.vmt'):
        continue
    print('Processing:', file + '.vmt')
    
    # Load the VMT for the image
    lines = []
    with open('vmt/' + file + '.vmt', 'r') as base:
        lines = base.readlines()
        
    # Load the image to edit
    base_image = Image.open('input/' + file + '.png').convert('RGBA')
    
    # Preprocess the file - converts any other files if needed
    mask_mode, mask_image = file_preprocess(file, directory_fout)
    
    for key in colors:
        # Create the VMT
        process_vmt(directory_fout + file + '_' + key + '.vmt', file, lines, key, colors[key])
        
        # Colorize and save the image
        colorized = None
        if mask_mode:
            colorized = process_color_mask(base_image, mask_image, colors[key])
        else:
            colorized = process_color_base(base_image, colors[key])
        colorized.save(directory_pout + file + '_' + key + '.png')
    
# Convert the png directory to VTF
convert_png_folder(directory_pout, directory_fout, pause=True)