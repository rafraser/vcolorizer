from colorize_2 import *

# Get user input
palette = input('Palette to use: ')
files = input('Files to colorize (comma-seperated): ')

# Load the color palette
if not palette.endswith('.txt'):
    palette = palette + '.txt'
colors = load_palette_file('palettes/' + palette)
colors = normalize_colors(colors)

# Create output directories with timestamp
timestamp = int(time.time())
directory_pout = 'output/png-' + str(timestamp) + '/'

# Make the folders
try:
    os.mkdir('output')
except:
    pass
os.mkdir(directory_pout)


files = files.split(',')
for file in files:
    if not os.path.isfile('input/' + file + '.png'):
        continue
    print('Processing:', file + '.png')
    
    # Load the image to edit
    base_image = Image.open('input/' + file + '.png').convert('RGBA')
    
    # Preprocess the mask - loads the mask if applicable
    mask_mode, mask_image = file_preprocess_mask(file)
    
    for key in colors:
        # Colorize and save the image
        colorized = None
        if mask_mode:
            colorized = process_color_mask(base_image, mask_image, colors[key])
        else:
            colorized = process_color_base(base_image, colors[key])
        colorized.save(directory_pout + file + '_' + key + '.png')