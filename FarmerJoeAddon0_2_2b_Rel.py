# $Id: farmerjoe_addon.py,v0.2.2 2021/1/9$
#
# --------------------------------------------------------------------------
# For use with Farmerjoe by Mitch Hughes (AKA lobo_nz)
# This script by Laurence Weedy FJ@weedyworld.co.uk
# is based on the Farmer Joe submit script by Mitch Hughes (AKA lobo_nz)
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------
bl_info = {
    "name" : "Farmer Joe Render Farm 0.2.2",
    "author" : "Mitch, Hughs, Laurence Weedy",
    "version": (0, 2, 2),
    "description" : "Farmer Joe add-on for 2.8 - version 0.2.2",
    "blender" : (2, 80, 0),
    "warning" : "",
    "category" : "Render"
}
# Render imgformatVersion
import bpy
import string
import os
import platform
import time
import sys
import shutil
from bpy.types import (Operator, AddonPreferences, PropertyGroup)
from bpy.props import ( PointerProperty,StringProperty,BoolProperty,EnumProperty)
platform = sys.platform

#Global variables and their defaults

prog_state = 0                  # used for program flow
    #0 = idling
    #1 = settings stage
    #2 = submit stage
    #3 = finished stage
failsafe = 0                      # if failsafe = 1 the blend file has never been saved and script should not let you do anything else.
  
oldframesdir = ""               # stores the original render directory as set in the output panel
resultsbmt = ""                 # did submit work for dialogue box?
extradirs = ''                  # directories to be copied and used in text field 
fjpath = "/media/renders"       # <--- LINUX PATH HERE !!!!!!!!!!!!
fjname = "Farmerjoe.linux"    # Linux Default Farmer Joe .linux or Perl script 
fjos = "linux"                  # os name - changed in FJAddonPreferences
chunkframes = 1                 # Set the default number of frames rendered by each renderer at a time
dir_count = 0                   # counts the number of top level subdirectories copied
movdir = "job_directory"        # directory AVIs FFMPEGs will be rendered to - blank for default job directory
render_by_parts = "0"           # if 1 we are doing a render by parts
timeoutf = 120
threads = 1                     # number of threads controller will use to render AVI/FFMPEG files.
extra_avi = 'none'              # Format if an extra AVI/FFMPEG is to be rendered from stills
prefix =''                      # this will be the jobname prefix
prefixdo = 0                    # logic for prefix
prefixname = ''                 # this will be the full file name with prefix
new_prefix = ''                 # Used in creating name prefix
relativep = ''                   # Used to execute the make paths relative command
class FJAddonPreferences(AddonPreferences):

    bl_idname = __name__
    bl_options = {'INTERNAL'}    
    
    global fjpath, fjos, fjname, failsafe
    
    if platform == 'win32':
        fjpath = 'R:'           # <--- WINDOWS PATH HERE !!!!!!!!!!!!
        fjos = 'MSWin32'
        fjname ='Farmerjoe.exe'       #Windows Default Farmer Joe exe or Perl script 
    elif platform == 'darwin':
        fjpath = '/render'
        fjos = 'OSX'            # <--- OSX PATH HERE !!!!!!!!!!!!
        fjname = 'Farmerjoe.osx'        #OSX Default Farmer Joe .osx or Perl script 
        
    #### Define Drive letter/share and Farmer Joe exe/linux/osx/pl defaults in Addon Properties panel
    fjdrive: StringProperty(
        name = 'Share',
        description = 'Choose the mapped drive',
        default = fjpath,
        maxlen = 1024,
        subtype = 'NONE')    
    #### Farmer Joe executable
    fjprog: StringProperty(
        name = 'Name',
        description = 'For Developement: Change the one you want to run',
        default = fjname,
        maxlen = 1024,
        subtype = 'NONE') 
    #### Directory to render AVIs to if not the job directory.    
    moviedir: StringProperty(
        name = 'Name',
        description = 'no slashes in either direction or spaces',
        default = movdir,   # checked for illegal characters later
        maxlen = 1024,
        subtype = 'NONE') 
        
    time_out : bpy.props.IntProperty(
        name = "minutes",
        description = " frame time-out",
        soft_min = 1,
        soft_max = 1200,
        default= 120,
        step = 1,
        )
    avi_thread : bpy.props.IntProperty(
        name = "threads",
        description = " threads used to render AVI/FFMPEG - max 2 as VSE can't use more than 1",
        soft_min = 0,
        soft_max = 2,
        default= 1,
        step = 1,
        )
    
    ####draw these text fields in the Addon properties drop down menu   
    def draw(self, context):

        layout = self.layout
        layout.separator()
        

        
        drivebox = layout.box()
        drivebox.label(text='Farmer Joe drive or Share')
        drivebox.label(text='enter the drive letter with a colon (windows) or share where Farmer Joe is mounted')
        drivebox.prop(self,'fjdrive')

        #layout.separator()
        joebox = layout.box()
        joebox.label(text='Farmer Joe executable or script (for developement)')
        joebox.label(text='Enter the name or script used for Farmer Joe')
        joebox.prop(self,'fjprog')
        
        movbox = layout.box()
        movbox.label(text='Enter name of directory to render AVI/FFMPEG or Parts to in root of share.')
        movbox.label(text='Or set as \'job_directory\' to render into jobs/job directory')
        movbox.prop(self,'moviedir')
        movbox.label(text='Illegal characters will be removed')

        timbox = layout.box()
        timbox.label(text='Enter time to render frame before it times out')
        timbox.prop(self,'time_out')
        
        threabox = layout.box()
        threabox.label(text='Number of processor threads to render extra AVI FFMPEG', icon="ERROR")
        threabox.prop(self,'avi_thread')
        threabox.label(text='This is only used when creating movie in addition to stills')
        threabox.label(text='VSE can only use one thread')
        threabox.label(text='kept option for two as rest of Blender might use one')


############################################################################
#       Setup and start of main loop            
############################################################################
class FJ_PT_farmerjoemain(bpy.types.Panel):
    bl_label = "Farmer Joe\'s Render Farm 0.2.2"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'EEVEE'}            
# not sure whether we need this as Farmer Joe does not care which renderer used
    
    
    def draw(self, context):
        global extradirs, fjname, prog_state, resultsbmt, fjos, failsafe, chunkframes, oldframesdir, dir_count, movdir, render_by_parts, time_outf, threads, extra_avi, prefix, prefixdo, prefixname, new_prefix, relativep
        
        ###this array is from old submit script and I'm to lazy to get rid of the bits I don't need
        v_ = {
        'blend_filename'        :bpy.path.basename(bpy.context.blend_data.filepath),
        'origRenderPath'        :str(bpy.context.scene.render.filepath),
        'origFileType'          :str(bpy.context.scene.render.image_settings.file_format),
        'startFrame'            :str(bpy.context.scene.frame_start),
        'endFrame'              :str(bpy.context.scene.frame_end),
        'timeout'               :200,
        'submit'                :1,
        'step'                  :1,                     #Old name for chunkframes
        'tile_x'                :4,                     # x for parts rendering
        'tile_y'                :4,                     # y for parts rending
        'fj_root'               :fjpath,                #LINUX PATH IF USED - WINDOWS BELOW
        'linux_farmerjoe'       :fjname,                #'Farmerjoe.linux',
        'windows_farmerjoe'     :fjname,                #'FJ9.exe',
        'osx_farmerjoe'         :fjname,                #'Farmerjoe.osx',
        'copydirs'              :extradirs,             #the extra directories that will be copied eg: 'textures,fluidsimdata',   
        'fj_jobs'               :'jobs',                #the jobs directory name to be used
        'sep'                   :os.path.sep,           #the file path separator used by the os
        'os'                    :fjos                   #os variable handed over Legacy
        }
        
        #### begin the addon panel contents
        layout = self.layout
       
        
        ####Render job been submitted - this calls the finish button - this will also reset the output path and save the blend file
        #### we can not do this in the main prog due to blender python api restrictions so we have to do it in a separate class.
        if prog_state == 3:                     
            row = layout.row()
            row.label(text = resultsbmt)
            row = layout.row()
            row.label(text = str(dir_count)+' toplevel subdirectories copied')
            row = layout.row()
            row.operator("custom.fjfinished", text='Finished - Press to restore output path')    
        
        ####the starting position when the addon is activated by pressing the arrow head by 'Farmer Joe' in Output panel
        if prog_state == 0:                     
            row = layout.row()                  ####this is also the default for the addon
            row.label(text = 'To render a single image by parts')
            row = layout.row() 
            row.label(text = 'set the end frame to equal the start frame')
            row = layout.row() 
            row.operator("custom.fjsetup", text='Prepare your file')
            row = layout.row()
        
        ####Prepare your file button has been pushed and we are collecting information about the job
        if prog_state == 1:                                 
            scene = context.scene.your_properties           ####This line is needed for the text field operator and the framechunks IntProperty both defined in FJProperties
            row = layout.row()
            row.operator("custom.fjcancel", text='Cancel')  #draws a 'cancel' button so you can abort
            if  render_by_parts == 1:
                row = layout.row()
                row.label(text = 'Rendering by Parts') 
                row = layout.row()
                row.label(text = 'choose how the image will be split')
                row = layout.row()
                row.prop(scene,"parts_x_y")
                row = layout.row()
                
                           
            row = layout.row()
            row.label(text = 'File name:')

            row.label(text = v_['blend_filename'])
            if  render_by_parts == 0:
                row = layout.row()
                row.label(text = 'Frame range: ')
                row.label(text = v_['startFrame']+' to '+v_['endFrame'])
                row = layout.row()
                row.label(text = 'Rendering to:')

                if platform == 'win32':
                    row.label(text =  v_['fj_root']+' drive')
                else:
                    row.label(text = v_['fj_root'])
                    
                row = layout.row()
                row.label(text = 'frame chunks:')
                row.prop(scene, "chunks")                       #draws framechunks IntProperty defined in FJProperties
                row = layout.row()

                
            box = layout.box()
            box.prop(scene, "stringdirs")                   #draws the text field for the extra directories defined in FJProperties
            box.label(text = 'Edit out the ones you don\'t want copied')
            box.label(text = 'and keep a comma inbetween, no spaces')     
            if fjos != "MSWin32":
                box.label(text = 'no recursive directories will be copied') #extra message for linux / mac as only the top level of files will be copied due to permission problems.
            extra_avi = 'none'
            if  render_by_parts == 0:            
                row = layout.row()
                row.label(text = 'Output path changed to:    //frames\\')
                box = layout.box()
                row = layout.row()
                ### Active Camera as prefix for Jobname #### PREFIX #####
                row = layout.row()
                row.prop(scene,"prefixcheck")
                row = layout.row()
                if scene.prefixcheck:
                    row = layout.row()
                    new_prefix = prefix
                    if prefix[-1].isdigit():
                        row.prop(scene,"cam_ver_up") # do we version up the camera?
                        row = layout.row()
                        if scene.cam_ver_up:    ############## New camera version !! ################ Thanks Hans Bouwmeester on Stack Overflow
                            cam_pre = prefix.rstrip("0123456789")   #camera name
                            cam_post = prefix[len(prefix.rstrip("0123456789"))] #version no
                            new_cam_post = str(int(cam_post) + 1)
                            new_prefix = cam_pre + new_cam_post

                    prefixdo = 1
                    row.label(text = 'Jobname is now ')
                    row = layout.row()
                    row.label(text = new_prefix + '_' + v_['blend_filename'])
                else:
                    prefixdo = 0
                box = layout.box()
                row = layout.row()
                row.prop(scene,"relativecheck")
                if scene.relativecheck:
                    relativep = True
                row = layout.row()    
                if v_['origFileType'] == 'AVI_JPEG' or v_['origFileType'] == 'AVI_RAW' or v_['origFileType'] == 'FFMPEG':
                    extra_avi = 'concat'
                else:
                
                    
                    row.prop(scene,"moviebool") ######need to remove this if rendering AVI etc directly
                    if scene.moviebool:
                        row = layout.row()
                        row.prop(scene,"movieoptions")
                        row = layout.row()
                        extra_avi = scene.movieoptions
                        if scene.movieoptions == 'AVI_JPEG':
                            row.prop(scene,"aviquality")
                            row = layout.row()
                    else:
                        row = layout.row()
            else:
                row = layout.row()
                #box = layout.box()

            box = layout.box()
            if (movdir != 'job_directory' and scene.moviebool) or extra_avi == 'concat' : #Printing Jobs directory used
                
                row.label(text ="Rendering to the "+movdir+" directory")
            else:
                
                row.label(text ="Rendering to the \\jobs directory ")
            row = layout.row()
                    
            ####Preflight checks####    

            dir_error=0 #resets the 'error in subdirectories entered' flag
            c = bpy.path.abspath("//")
            testdirs=scene.stringdirs   #fetch whats in the text field (subdirectories).
            subdirs = str(testdirs).split(',') # get the individual subdirectory names - split on comma
            for directory in subdirs:   #directory will be the directories specified in the text field.
                if not os.path.isdir(os.path.join(c, directory)): #do the directories exist? if not raise alarm
                    dir_error=1
            
            if not bpy.data.is_saved:       #Checks if blend file has been saved
                box.label(text = 'Press cancel, you can not go on', icon="ERROR")
                failsafe = 1                #failsafe set
                row.operator("custom.fjcancel", text='Sorry start again')
                
            elif render_by_parts == 1 and v_['origFileType'] == 'AVI_JPEG':  
                box.label(text = 'Cannot use AVI JPEG, please change File Format', icon="ERROR")

            elif render_by_parts == 1 and v_['origFileType'] == 'AVI_RAW': 
                box.label(text = 'Cannot use AVI RAW, please change File Format', icon="ERROR")

            elif render_by_parts == 1 and v_['origFileType'] == 'FFMPEG':
                box.label(text = 'Cannot use FFmpeg video, please change File Format', icon="ERROR")

            elif not os.path.exists(os.path.join(v_['fj_root'], 'Farmerjoe.conf')): # Check to see if Farmer Joe drive is mapped
                row = layout.row()
                box.label(text = 'Farmer Joe drive not mapped!', icon="ERROR")
            elif not os.path.exists(os.path.join(v_['fj_root'], fjname)): # Check to see if Farmer Joe executable / script file is there.              
                row = layout.row()
                box.label(text = 'Farmerjoe Exe / script name wrong in prefs', icon="ERROR")
                box.label(text = 'Press \'Cancel\' and change in addon preferences',)
            elif dir_error==1:
                row = layout.row()
                box.label(text = 'Subdirectories: you have made a mistake!', icon="ERROR")  #error entering subdirectories

            else:
                row = layout.row()
                if extra_avi == 'concat':
                    row.label(text = 'Moving Image Format: '+v_['origFileType'])
                    extra_avi = 'none'
                else:
                    row.label(text = 'Still Image Format: '+v_['origFileType'])

                row = layout.row()
                #print('failsafe '+str(failsafe))
                if failsafe==0:
                    row.operator("custom.fjrender", text='Send to Farmer Joe')
                else:
                    row.operator("custom.fjcancel", text='Sorry start again')
        
        ###################################################################################################################
        #### The 'send to farmer joe' button has been pressed. Compile settings, copy files and directories and submit job.
        if prog_state == 2:    
            prog_state=0                        #### Stops this part of the script from looping (and doing things more than once)
            scene = context.scene.your_properties           ####This line is needed for the text field operator and the framechunks IntProperty both defined in FJProperties
            imgformat = v_['origFileType'] 
            if  render_by_parts == 1:
                chunkframes=1                               #chunks if its not 1 it messes things up in render by parts

            moviedir = 'job_directory'; #if it's not render by parts and not creating an extra avi - job_directory is reset.
            if prefixdo == 1:
                prefixname = new_prefix + '_' + v_['blend_filename']     ##Added for Prefix
            else:
                prefixname = v_['blend_filename']
                
            print('and the image format is ',imgformat)
            render_by_parts = 0                     # reset render by parts as only used by GUI
            v_['timeout']=time_outf;
            row = layout.row()
            row.label(text = 'Sending file - Please wait')
            
            #RUN CODE BELOW HERE
            ## SUBMIT
            #########################################
                ## prepare Job directory structure
            #########################################
            # Make new dir for this job using a timestamp
            t = time.localtime()
            #timestamp = "%s-%s-%s_%s-%s-%s" %(t[0],t[1],t[2],t[3],t[4],t[5]) # improve formatting of timestamp
            timestamp = "%s-%02d-%02d_%02d-%02d-%02d" %(t[0],t[1],t[2],t[3],t[4],t[5])
            print('Setting up Farmer Joe job')
            render_dir_name = prefixname + '.' + timestamp    #Job directory name is render_dir_name
            print ("render job directory name " + render_dir_name)
            render_dir = os.path.join(v_['fj_root'] , v_['fj_jobs'] ,render_dir_name) #render_dir is full path on FJ share
            print ("render job directory path " + render_dir)
            frames_dir = os.path.join(render_dir, 'frames')
            
            print ("frames directory path " + frames_dir)
            jobfilename = prefixname + '.job'
            print ("jobfilename " + jobfilename)
            job_path_name = os.path.join(render_dir , jobfilename)
            print ("job file path name " + job_path_name)

            #########################################
                ## Write the job file
            ######################################### 
                
                #filename     # vr.blend
                #startframe   # 1
                #endframe     # 360
                #step         # 5
                #timeout      # 180
                #jobdir       # jobdir
                #jobname      # name
                #image_x      # 800
                #image_y      # 600
                #xparts       # 4
                #yparts       # 4
                #imgformat       # nomovie,AVI_JPEG,AVI_RAW,FFMPEG - now carries image type if rendering parts AKA imgformat
                #moviedir     # movdir
                #aviquality   # avi_qual    AVI_JPEG quality
                #extra_avi    # none #concat
                #threads      # 0-6
            c = bpy.path.abspath("//")      #c is blend file absolute path
            v_['step'] = str(chunkframes) # set it to the value from the float property 
            
            #check characters in AVI job directory are legal as we can't do it in addon properties.
            valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
            filenamev = ''.join(cc for cc in movdir if cc in valid_chars)
            movdir = filenamev.replace(' ','_') # I don't like spaces in filenames.
            
            #imgformat = "nomovie"

            
            parts = scene.parts_x_y.split(',') # split on comma
            v_['tile_x']=parts[0]
            v_['tile_y']=parts[1]

            #data contains the job file
            data = "\n".join([prefixname, v_['startFrame'], v_['endFrame'], v_['step'], str(v_['timeout']*60), render_dir_name, prefixname, str(bpy.context.scene.render.resolution_x), str(bpy.context.scene.render.resolution_y), str(v_['tile_x']), str(v_['tile_y']), imgformat, movdir, str(scene.aviquality), extra_avi, str(threads) ])

            print ("data " + data)   

            #########################################
            ## MAKE THE DIRECTORIES TO STORE THE JOB
            #########################################
            print('-----------------')
            print ('Making ' + str(render_dir))
            os.system('mkdir "' + render_dir +'"')
            print ('Making ' + str(frames_dir))
            os.system('mkdir "' + frames_dir +'"')

            #########################################
            ## Copy the blend file 
            #########################################

            
            print ("copying blend file starts")
            print ('from ',c,v_['blend_filename'], 'to ', render_dir,prefixname)
            fro = os.path.join(c,v_['blend_filename']) #this will need to be different on prefix
            too = os.path.join(render_dir,prefixname)
            #print (fro, too)
            #copyfile used here as shutil.copy had permissions problems in linux.
            shutil.copyfile(fro, too) # Copy that blend file over!

            print ("copying blend file finished")
            c = bpy.path.abspath("//")
            print ("-----------------")
            
            #########################################
            #Extra DIRECTOIRS !!!
            #########################################
            # Due to problems with permissions when linux writes to linux shares, we will not do recursive subdirectories here. just whats in the top level of 'subdirs'
            # this is because shutil copytree checks permissions and fails.
            #But no such restriction for windows
            print('Making subdirectories and copying files')
            subdirs = str(v_['copydirs']).split(',') # split on comma
            #dir_count = 0
            extradirs=v_['copydirs'] # so that copydirs does not get reset
            if extradirs != '':
                for directory in subdirs:   #directory will be the directories specified in the text field.
                    if os.path.isdir(os.path.join(c, directory)):
                        print('directory being copied - ',directory)
                        dir_count = dir_count + 1
                        current_rend_path=os.path.join(render_dir,directory)
                        os.system('mkdir "' + current_rend_path +'"')
                        src_files = os.listdir(os.path.join(c, directory))
                        for file_name in src_files:                            
                            full_file_name = os.path.join(c, directory, file_name)          #so the files are copied for the specified directories.
                            if os.path.isfile(full_file_name):
                                print('copying file ',full_file_name)
                                shutil.copyfile(full_file_name, os.path.join(render_dir,directory,file_name))                              
                        
                        for (current_path, folders, files) in os.walk(os.path.join(c,directory)):#in each of the specified directories look for sub directory structure.
                            
                            for folder in folders:
                                print('New subdirectory ',folder)
                                relapath=os.path.relpath(current_path,os.path.join(c, directory))
                                if relapath == ".":
                                    relapath=""
                                elif relapath =="..":
                                    relapath==""
                                
                                print("abs path", c,"current path ", current_path)

                                print('relative path -',relapath)
                                os.system('mkdir "' + os.path.join(render_dir,directory,relapath,folder) +'"') #makes the subdirectory we need.
                                print('new folder created ',os.path.join(render_dir,directory,relapath,folder))
                                
                                src_files = os.listdir(os.path.join(c, directory,relapath,folder))
                                for file_name in src_files:
                                    full_file_name = os.path.join(c, directory, relapath,folder, file_name)
                                    if os.path.isfile(full_file_name):
                                        print('copying file ',full_file_name)
                                        shutil.copyfile(full_file_name, os.path.join(render_dir,directory,relapath,folder,file_name)) 
       


            #########################################
            ## Submit the job to Farmer Joe
            #########################################
             
            jobFileInst = open(job_path_name, "w+")

            jobFileInst.write(data)
            jobFileInst .close()
            print('--------------------')
            print ("job file", job_path_name)
            time.sleep(5) 
            #print (data)

            submit_cmd = os.path.join(v_['fj_root'], fjname) + ' --submit "%s" "%s"'%(render_dir_name,jobfilename) # the SUBMIT command
                
            print ("SUBMIT COMMAND: ")
            print (submit_cmd)
            
            result = os.system(submit_cmd)
            if result != 0:
                resultsbmt = ("Submit Failed for: " + job_path_name)
                #submit_status = "FAILED"

            else:
                resultsbmt = ("Submit Succeeded for: " + job_path_name)
                #submit_status = "OK"


        
            prog_state = 3  #call the 'Finished' button to the Farmer Joe panel

        # and so it all begins again.... this section loops back to the begining of the def.


##################################################################################
## this class does initial checks and starts the main routine
##################################################################################
class FJSetup(Operator):
    """get the file ready for the render farm"""
    bl_idname = 'custom.fjsetup'

    bl_label = 'fjsetup'

    bl_options = {'INTERNAL'}

    def execute(self, context):
        user_preferences = bpy.context.preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        


        global fjpath, fjname, extradirs, prog_state, oldframesdir, movdir, render_by_parts,time_outf, threads, prefix
        
        fjpath=addon_prefs.fjdrive  ###collect the values from the addon preferences panel
        fjname=addon_prefs.fjprog
        movdir=addon_prefs.moviedir
        time_outf = addon_prefs.time_out
        threads = addon_prefs.avi_thread
        
        
        ####find what the subdirectories are
        directories = ""    #define and clear variable
        if bpy.data.is_saved:   #test to see if the blend file has been saved. If not we can't go on.
      
            root = bpy.path.abspath("//")
            for item in os.listdir(root):   #list everything in the blend file directory
                if not os.path.isfile(os.path.join(root, item)):    #if it isn't a file it must be a directory
                    if directories != "":
                        directories = directories + ','+ item       #find all the subdirectories and delimit them with a comma
                    else:
                         directories = item
        else:
            directories = 'NEED TO SAVE BLEND FILE FIRST!!'         # this will be displayed in the text field if blend file not saved.
        
        extradirs=directories                       ##Our list of subdirectories handed on to the global variable we are using.
        scene = context.scene.your_properties       ##needed for the subdirectories text field and the chunk integer box.
        scene.stringdirs=extradirs                  ##Sets the text field to the subdirectories or the warning message
        print('--------------------')
        print('Farmer Joe started')
        #print(extradirs)
        
        oldframesdir=str(bpy.context.scene.render.filepath)     #save old render path 
        bpy.context.scene.render.filepath = '//frames\\'        #and replace with the one we need for Farmer Joe
        prefix = str(bpy.context.scene.camera.name)
        if bpy.context.scene.frame_start == bpy.context.scene.frame_end:
            render_by_parts = 1
            print('rendering by parts')
        else:
            print('rendering by frames')
            render_by_parts = 0
        prog_state = 1  # Let the main setting panel of Farmer Joe show

        return {'FINISHED'}
        
#####################################################################################
## this class saves the blend file with the new output path before running the submit 
#####################################################################################
class FJRender(bpy.types.Operator):
    """submit the job and copy the files to Farmer Joe"""
    bl_idname = 'custom.fjrender'
    bl_label = 'fjrender'
    
    def execute(self, context):

        global prog_state, extradirs, chunkframes, new_prefix, relativep

        scene = context.scene.your_properties ##needed for the subdirectories text field and the chunk integer box.
        extradirs=scene.stringdirs
        if relativep:
            bpy.ops.file.make_paths_relative
        relativep = ''
        chunkframes = scene.chunks
        bpy.context.scene.camera.name = new_prefix
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath) #Saving the file with the modified Output render path - and of course any changes that have been made since the last save.
        
        prog_state = 2  #We are preparing to submit the render
 
        return {'FINISHED'}
        
##################################################################################
## this class finishes off, resets the output path and returns to the addon to the default waiting state
##################################################################################    
class FJFinished(bpy.types.Operator):
    """You're all done, reset the output path"""
    bl_idname = 'custom.fjfinished'
    bl_label = 'fjfinished'
    bl_options = {'INTERNAL'}

    def execute(self, context):

        global prog_state, oldframesdir, dir_count
        
        if bpy.data.is_saved:   #test to see if the blend file has been saved. If not we can't go on.
            bpy.context.scene.render.filepath = oldframesdir        #We're done so reset the Output render path to what it was before.
            bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath) #and save the blend file
            
        print(str(dir_count),'  subdirectories copied')
        dir_count = 0
        print('Farmer Joe finished for now')
        print('--------------------')        
        prog_state = 0  #back to the waiting loop
        return {'FINISHED'}

##################################################################################
## this class defines the directories text field and the frame chunks widget
##################################################################################
class FJProperties(PropertyGroup):
    bl_idname = 'fjprops'
    bl_label = 'fjprops'
    bl_options = {'INTERNAL'}
    
    stringdirs : StringProperty(
        name = "Subfolders",
        default=extradirs,
        description="These subdirectories will be copied with the blendfile"
        )
        
    chunks : bpy.props.IntProperty(
        name = "chunks",
        description = "how many frames rendered by each client at a time",
        soft_min = 1,
        soft_max = 100,
        default= 1,
        step = 1,
        )
    moviebool : BoolProperty(
        name=  "Render AVI/FFMPEG as well?", 
        description ='render extra AVI/FFMPEG file afterwards', 
        default=False,
        ) 
    prefixcheck : BoolProperty(
        name=  "Active Camera as prefix?", 
        description ='add Active Camera name as prefix to jobname', 
        default=False,
        ) 
    relativecheck : BoolProperty(
        name=  "Want to make paths relative?", 
        description ='Makes file paths relative before render', 
        default=False,
        )         
    cam_ver_up : BoolProperty(
        name=  "Version - auto-increment last digit of cam name?", 
        description ='increment last digit of camera name', 
        default=False,
        ) 
    
    movieoptions : EnumProperty(
        name="Format ",
        description="Choose the imgformatoutput format",
        items=[
            ("AVI_JPEG","AVI JPEG","AVI MJPEG format"),
            ("AVI_RAW","AVI RAW","Uncompressed AVI format"),
            ("FFMPEG","FFMPEG","FFMPEG format"),
        ],
        default='AVI_JPEG'
        )
    parts_x_y : EnumProperty(
        name="Parts ",
        description="Choose how the image will be split",
        items=[
            ("3,10","3x10","3 by 10"),
            ("4,8","4x8","4 by 8"),
            ("5,6","5x6","5 by 6"),
            ("4,4","4x4","4 by 4"),
            ("3,3","3x3","3 by 3"),
            ("2,2","2x2","2 by 2"),
            ("6,5","6x5","6 by 5"),
            ("8,4","8x4","8 by 4"),
            ("10,3","10x3","10 by 3"),
        ],
        default='4,4'
        )
    aviquality : bpy.props.IntProperty(
        subtype="PERCENTAGE",
        name = "Quality",
        description = "Quality of MJPG compression",
        soft_min = 1,
        soft_max = 100,
        default= 90,
        step = 1,
        )
##################################################################################
## this class defines the cancel button and deals with program flow
##################################################################################
class FJCancel(bpy.types.Operator):
    """Cancel render operation"""
    bl_idname = 'custom.fjcancel'
    bl_label = 'fjcancel'
    bl_options = {'INTERNAL'}

    def execute(self, context):

        global prog_state, failsafe, render_by_parts
        
        failsafe = 0    #failsafe and prog_state reset after cancel pressed
        prog_state = 0
        render_by_parts = 0
        return {'FINISHED'}

##################################################################################

        
def register():
    bpy.utils.register_class(FJAddonPreferences)
    bpy.utils.register_class(FJProperties)
    bpy.utils.register_class(FJ_PT_farmerjoemain)
    bpy.utils.register_class(FJSetup)
    bpy.utils.register_class(FJRender)
    bpy.utils.register_class(FJFinished)
    bpy.utils.register_class(FJCancel)
    bpy.types.Scene.your_properties = PointerProperty(type=FJProperties)


def unregister():
    bpy.utils.unregister_class(FJ_PT_farmerjoemain)
    bpy.utils.unregister_class(FJSetup)
    bpy.utils.unregister_class(FJRender)
    bpy.utils.unregister_class(FJFinished)
    bpy.utils.unregister_class(FJCancel)
    bpy.utils.unregister_class(FJAddonPreferences)
    bpy.utils.unregister_class(FJProperties)
    del bpy.types.Scene.your_properties
    
if __name__ == "__main__": register() 
    