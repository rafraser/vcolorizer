# vcolorizer
### Automated texture colorizer to help out my workflow

## VTFLib
For the program to automatically convert files to .vtf; you will need to install VTFCmd from [this page](http://nemesis.thewavelength.net/index.php?c=177#p177). Place VTFCmd.exe and the required .dll files into the root directory of this program.

## Preamble
This program was made primarily to help my workflow, with documentation being mostly an afterthought.
The goal of this program is to take a .vmt file that is provided, and automatically generate a mixed color palette for that texture. To do this:
* a .vmt is needed in the vmt/ folder
* a .png with the same name is needed in the input/ folder
The program will then automatically generate .vmts and .vtfs for each color variation required.
Also supported:
* A color mask .png can be placed into masks/. This will be tinted and placed on the image
* A bumpmap .png can be placed into norms. This will automatically be converted to filename_norm.vtf
* An envmapmask .png can be placed into envmapmasks/. This will automatically be converted to filename_envmapmask.vtf

When writing the .vmt file, consider the following:
* ensure that the basetexture and the filename are the same
* remember that any normals will be created as filename_norm.vtf
* remember that any envmapmasks will be created as filename_envmapmask.vtf

Other than that, the .vmt can be written in any way that seems acceptable. The program does not do much processing to the .vmt file, apart from ensuring the textures line up for each color variation. There are also some additional .vmt options to help with the coloring process; see the section below for how to use these. In most cases, *you should be able to write the base .vmt as normal*.

## Example Texture
This repository includes a basic example texture. This will be a dev texture with slight reflectivity (with the environment map tinted with the color); this should hopefully provide enough to demonstrate how to setup folders and VMTs. It does not have a normal map.

## VMT Extras
There are certain lines that can be placed at the top of the VMT that will allow the colorizer to do neat stuff. Currently, these are:
* ColorEnvMap:Strength

  This will tint the environment map with the current color being used. A strength of 1 will be a perfect color replacement, 0.5 will be half-strength envmap tinting, etc.
