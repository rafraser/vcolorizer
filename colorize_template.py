from colorize_2 import *

def process_vmt_template(outfile, texname, lines, colname, path):
    """
    Process a given VMT
    This is pretty simple currently:
     - rename the basetexture to have the colour included
    """
    # Check for colorable envmap property
    new_lines = lines.copy()
    new_lines = [line.replace("%NAME%", texname + "_" + colname) for line in new_lines]
    new_lines = [line.replace("%BASENAME%", texname) for line in new_lines]
    new_lines = [line.replace("%PATH%", path) for line in new_lines]

    # Write the output to the new file
    # directory_fout + file_name + '_' + key + '.vmt'
    with open(outfile, "w") as vmt:
        for line in new_lines:
            vmt.write(line)

def main(palette, files, vmt_file, path):
    # Load the color palette
    if not palette.endswith(".txt"):
        palette = palette + ".txt"
    colors = load_palette_file("palettes/" + palette)
    colors = normalize_colors(colors)

    # Create output directories with timestamp
    timestamp = int(time.time())
    directory_pout = "output/png-" + str(timestamp) + "/"
    directory_fout = "output/final-" + str(timestamp) + "/" + path + "/"

    os.makedirs(directory_pout, exist_ok=True)
    os.makedirs(directory_fout, exist_ok=True)

    # Load the template VMT
    lines = []
    with open("vmt/" + vmt_file + ".vmt", "r") as base:
        lines = base.readlines()

    files = files.split(",")
    for file in files:
        print("Processing:", file + ".vmt")

        # Load the image to edit
        base_image = Image.open("input/" + file + ".png").convert("RGBA")

        # Preprocess the file - converts any other files if needed
        mask_mode, mask_image = file_preprocess(file, directory_fout)
        overlay_mode, overlay_image = file_preprocess_overlay(file)

        for key in colors:
            # Create the VMT
            process_vmt_template(
                directory_fout + file + "_" + key + ".vmt", file, lines, key, path,
            )

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

            colorized.save(directory_pout + file + "_" + key + ".png")

    # Convert the png directory to VTF
    convert_png_folder(directory_pout, directory_fout, pause=True)


if __name__ == "__main"__:
    palette = input("Palette to use: ")
    files = input("Files to colorize (comma-seperated, no extension): ")
    vmt_file = input("VMT Template: ")
    path = input("Path: ")
    main(palette, files, vmt_file, path)

