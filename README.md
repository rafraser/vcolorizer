# vcolorizer
### Automated texture colorizer to help out my workflow

## Preamble
This program is very user-unfriendly. Use this at risk of suffering terrible design decisions.
## VTFLib
For the program to automatically convert files to .vtf; you will need to install VTFCmd from [this page](http://nemesis.thewavelength.net/index.php?c=177#p177). Place VTFCmd.exe and the required .dll files into the root directory of this program.
## Example Texture
This repository includes a basic example texture. This will be a dev texture with slight reflectivity (with the environment map tinted with the color); this should hopefully provide enough to demonstrate how to setup folders and VMTs. It does not have a normal map.
## Folder Setup
This program uses 5 folders for import information; you'll need to create these folders yourself.
* input/

  This is the main directory for converting textures. Any _.png_ files in this folder will be colorized according to the settings and placed into the appropiate location.
  
* vmt/

  This directory handles all the .vmt files. These have a few special settings, but otherwise can be treated as regular vmt files. During processing, the basetexture will be renamed for each color. More information & caveats are covered below.
  
* masks/

  These files are not converted to VTF - they are only used in the process of creating the colorized pngs. If a mask image is in this directory, it will be recolored and then added on top of the original texture. You can use this to mark off only specific regions of a texture for recoloring.
  
* norms/

  This directory has any .png format normal textures. These are converted to normal vtfs; and renamed to filename_norm.vtf.
  
* envmapmasks/

  Similar to the above. These are converted to vtfs, and renamed to filename_envmapmask.vtf
## VMT Extras
There are certain lines that can be placed at the top of the VMT that will allow the colorizer to do neat stuff. Currently, these are:
* ColorEnvMap:Strength

  This will tint the environment map with the current color being used. A strength of 1 will be a perfect color replacement, 0.5 will be half-strength envmap tinting, etc.
## Considerations
As mentioned above, there are a few things to remember when writing VMTs and using this program:
* The filename must be shared across all folders.
* The vmt must use the filename as the basetexture - this will be the part that is renamed for each color
* For normal maps, use filename_norm. If this is an issue, create the normal vtf manually.
* For envmapmasks, use filename_envmapmask. If this is an issue, create the envmapmask vtf manually.
