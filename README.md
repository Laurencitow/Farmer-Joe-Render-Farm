# Farmer-Joe-Render-Farm
A render farm for Blender 3D which includes rendering by parts, frames and render result to AVI

Farmerjoe was a popular Blender render farm software written for Blender 3D versions 2.4x in 2006 by Mitch Hughes. It stopped working in Blender 2.5x and beyond because Blender changed, the Blender python API changed and because Python itself changed. 
You can see the original project [here](https://github.com/lobonz/farmerjoe "lobonz farmerjoe repository")

This new version for Blender 2.8x was born out of frustration that there weren't any simple render farm solutions available and also my memory of how good Farmerjoe was when I used it for my master's films in 2010/11. With help from Mitch I have got it going again, fixed some bugs, added some features and written a Blender add-on which submits jobs through the Blender interface.

Features include:
- Rendering frames (any image format blender supports)
- using project subdirectories for textures or baked information etc.
- Rendering the resulting frames to an AVI JPEG, AVI RAW or FFMPEG file.
- Rendering a single large image by splitting it into parts, rendering on separete computers and recombining them.
- Specifying a directory in the root of the Farmerjoe share where AVIs or composite images will be rendered. Different people can have different directories.

An example of a Farmerjoe setup.

![alt text](https://github.com/laurencitow/Farmer-Joe-Render-Farm/raw/master/for_readme/FarmerJoeSystem.png "Farmer Joe System Diagram")

Farmerjoe works across plaforms and you can have a mixture of OSs in a Farmerjoe system. It is currently tested with Windows, Linux and OSX and will potentially work with any system that supports Blender and Perl. The software isn't really installed: you configure your network, place the Farmerjoe software in the share, place the blender software for each OS in the relevant directory, edit the Farmerjoe.conf and set the Farmerjoe software command to be run at startup on each of the computers. And that's it, end of instructions (apart from installing the add-on in Blender on your workstation of course).

You install the add-on into Blender in the usual way.

Rendering by frames - condition: when the start frame and end frame are not equal


![alt text](https://github.com/laurencitow/Farmer-Joe-Render-Farm/raw/master/for_readme/Addondetail.png "Farmerjoe add-on rendering frames")


Rendering by parts - condition: when the start frame and the end frame are the same


![alt text](https://github.com/laurencitow/Farmer-Joe-Render-Farm/raw/master/for_readme/AddonParts.png "Farmer Joe add-on rendering parts")

The 'Farmerjoe.xxx --appserver' commmand runs a webserver with useful 'retro-style' render information.

![alt text](https://github.com/laurencitow/Farmer-Joe-Render-Farm/raw/master/for_readme/webpage.png "Farmer Joe webpage for status monitoring")


Hope you enjoy the software and if you have any questions, in the first instance, please use the BlenderArtists thread.
