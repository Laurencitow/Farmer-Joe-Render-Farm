# Farmer-Joe-Render-Farm
A render farm for Blender 3D which includes rendering by parts, frames and render result to AVI

Farmerjoe was a popular Blender render farm software written for Blender 3D versions 2.4x in 2006 by Mitch Hughes. It stopped working in Blender 2.5x and beyond because Blender changed, the Blender python API changed and because Python itself changed. 
You can see the original project [here](https://github.com/lobonz/farmerjoe "lobonz farmerjoe repository")

This new version for Blender 2.8x was born out of frustration that there weren't any simple render farm solutions available and a memory of how good Farmerjoe was when I used it for my master's films in 2010/11. With help from Mitch I have got it going again, fixed some bugs, added some features and written a Blender add-on which submits jobs through the Blender interface.

Features include:
- Rendering frames (any image format blender supports)
- Projects which include subdirectories for textures or baked information
- Rendering the resulting frames to an AVI JPEG, AVI RAW or FFMPEG file
- Rendering a single large image by splitting it into parts, rendering on separete computers and recombining them.
- Specifying a directory in the root of the Farmerjoe share where AVIs or composite images will be rendered. Different people can have different directories.

Farmerjoe works across plaforms and you can have a mixture of OSs in a Farmerjoe system. It is currently tested with Windows, Linux and OSX and will potentially work with any system that supports Blender and Perl. The software isn't really installed: you configure your network, place the Farmerjoe software in the share, place the blender software for each OS in the relevant directory, edit the Farmerjoe.conf and set the Farmerjoe software commant to be run at startup on each of the computers. And that's it, end of instructions (apart from installing the add-on in Blender on your workstation of course).

An example of a Farmerjoe setup.

![alt text](https://github.com/laurencitow/Farmer-Joe-Render-Farm/raw/master/for_readme/FarmerJoeSystem.png "Farmer Joe System Diagram")

