# Farmer-Joe-Render-Farm
UPDATE! added a version of the 0.2.2  addon (0_2_2b_Rel)which has a 'make all paths relative' checkbox. Hoping to make a video of why this can be useful soon!  (211114)

UPDATE! Version 0.2.2 available.

A render farm for Blender 3D which includes rendering by parts, frames and render result to AVI

Farmerjoe was a popular Blender render farm software written for Blender 3D versions 2.4x in 2006 by Mitch Hughes. It stopped working in Blender 2.5x and beyond because Blender changed, the Blender python API changed and because Python itself changed. 
You can see the original project [here](https://github.com/lobonz/farmerjoe "lobonz farmerjoe repository")

This new version for Blender 2.8, 2.9 to 3.x was born out of frustration that there weren't any simple render farm solutions available and also my memory of how good Farmerjoe was when I used it for my master's films in 2010/11. With help from Mitch I have got it going again, fixed some bugs, added some features and written a Blender add-on which submits jobs through the Blender interface.

Features include:
- Rendering frames (any image format blender supports)
- Using project subdirectories for textures or baked information etc.
- Rendering the resulting frames to an AVI JPEG, AVI RAW or FFMPEG file.
- Rendering a single large image by splitting it into parts, rendering on separete computers and recombining them.
- Specifying a directory in the root of the Farmerjoe share where AVIs or composite images will be rendered. Different people can have different directories.

And in version 0.2.2
- Render straight to AVI or FFMPEG 
- Use camera name as prefix to jobname (useful for multi-camera files)
- Independent addon 'Joe's Camera Wizard' for storing some non camera specific data with each camera in a scene (Including start/end frame, whether compositor used, Volume start and end distance and volume desity.

See the readme pdfs in the zip file for more details.

You can use it on a single computer to queue jobs overnight or on a multicomputer system.

An example of a Farmerjoe setup.

![alt text](https://github.com/laurencitow/Farmer-Joe-Render-Farm/raw/master/for_readme/FarmerJoeSystem0_2_2.png "Farmer Joe System Diagram")

Farmerjoe works across plaforms and you can have a mixture of OSs in a Farmerjoe system. It is currently tested with Windows, Linux and OSX and will potentially work with any system that supports Blender and Perl. The software isn't really installed: you configure your network, place the Farmerjoe software in the share, place the blender software for each OS in the relevant directory, edit the Farmerjoe.conf and set the Farmerjoe software command to be run at startup on each of the computers. And that's it, end of instructions (apart from installing the add-on in Blender on your workstation of course).

The 'Controller' service controls all the jobs and is invoked by 'Farmerjoe.xxx --controller' in the command line.
The 'Render Node' service receives the jobs and does the rendering: invoked by 'Farmerjoe.xxx' in the command line.
(Where .xxx is .exe for windows, .linux for linux and .osx for Apple). There is also 'Farmerjoe.xxx --appserver which runs a web server giving you status of all the jobs.

You install the add-on into Blender in the usual way. (Install the .py file included in the zip - not the whole zip)

Rendering by frames - condition: when the start frame and end frame are not equal


![alt text](https://github.com/laurencitow/Farmer-Joe-Render-Farm/raw/master/for_readme/Addondetail.png "Farmerjoe add-on rendering frames")


Rendering by parts - condition: when the start frame and the end frame are the same


![alt text](https://github.com/laurencitow/Farmer-Joe-Render-Farm/raw/master/for_readme/AddonParts.png "Farmer Joe add-on rendering parts")

The 'Farmerjoe.xxx --appserver' command runs a webserver with useful 'retro-style' render information.

![alt text](https://github.com/laurencitow/Farmer-Joe-Render-Farm/raw/master/for_readme/FJ.jpg "Farmer Joe webpage for status monitoring")


Hope you enjoy the software and if you have any questions, in the first instance, please use the BlenderArtists thread.

DISCLAIMER - Farmerjoe is free and made as best we can. We are not liable if you experience any problems while using the software or if it affects any projects you are using it for. Please read the disclaimer in the readme file, FarmerJoe0_2_2.pdf, that comes with Farmerjoe.
