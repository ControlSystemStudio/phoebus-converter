#
# *******************************************************************************
# Copyright (c) 2020 by CEA.
# The full license specifying the redistribution, modification, usage and other rights
# and obligations is included with the distribution of this project in the file "license.txt"
#
# THIS SOFTWARE IS PROVIDED AS-IS WITHOUT WARRANTY OF ANY KIND, NOT EVEN
#
# THE IMPLIED WARRANTY OF MERCHANTABILITY. THE AUTHOR OF THIS SOFTWARE
# ASSUMES NO RESPONSIBILITY FOR ANY CONSEQUENCE RESULTING FROM THE USE,
# MODIFICATION, OR REDISTRIBUTION OF THIS SOFTWARE.
# ******************************************************************************
# C.E.A. IRFU/DIS/LDISC
#
#
#Script for recursively converting CSS opi files into Phoebus bob files
#Created on 24 May 2023
#
#author: Antoine Choquet 
#email: antoine.choquet@cea.fr
#
#contributor: Lea Perez

import argparse
import os
import subprocess
import re
import shutil
import platform
from resize_opi import opi_resizing
from bob_update import bob_updating

def search_dirs(search_string, rootdir):
    dirs_list=[]
    for rootdir, dirs, files in os.walk(rootdir):           
        for subdir in dirs:
            absolute_path = os.path.join(rootdir, subdir)
            if search_string in absolute_path and search_string not in dirs_list:
                dirs_list.append(absolute_path)
    return(dirs_list)

def search_files(search_string, rootdir):
    files_list=[]
    for rootdir, dirs, files in os.walk(rootdir):           
        for name in files:
            file_path = os.path.join(rootdir, name)
            if search_string in file_path and search_string not in files_list:
                files_list.append(file_path)
    return(files_list)

def conversion(opi_subdir, bob_subdir, phoebusFolder):
    #Check the OS
    system = platform.system()
    install_path = phoebusFolder
    if system == "Linux" : 
        java_path = os.path.join(install_path, 'java', 'linux-jdk-16.0.2', 'bin', 'java')
        classpath1 = os.path.join(install_path, 'javafx', 'linux', '*')
        classpath2 = os.path.join(install_path, 'lib', '*')
        classpath_str = classpath1 + ':' + classpath2
        opi_files = os.path.join (opi_subdir, "*.opi")

    elif system == "Windows":
        java_path = os.path.join(install_path, 'java', 'windows-jdk-16.0.2', 'bin', 'java')
        classpath1  = os.path.join(install_path, 'javafx', 'windows', '*')
        classpath2 = os.path.join(install_path, 'lib', '*')
        classpath_str = classpath1 + ';' + classpath2
        opi_files = os.path.join (opi_subdir, "*.opi")

    cmd = java_path + " -Xms2048m -Xmx2048m" + " -Dswing.defaultlaf=javax.swing.plaf.nimbus.NimbusLookAndFeel" + " -cp " + classpath_str + " org.csstudio.display.builder.model.Converter " + "-output " + bob_subdir + " " + opi_files
    subprocess.call(cmd, shell=True)
    return

def main():
    inputFolder = args.opi_folder
    phoebusFolder = args.phoebus_folder

    #Delete former resized_opi folder if it exists
    for resized_dir in search_dirs("resized", inputFolder):
        if os.path.exists(resized_dir):
            print(f"Deleting the folder : {resized_dir}")
            shutil.rmtree(resized_dir)

    #Check if there are .opi files in input folder
    opi_file_list = search_files(".opi", inputFolder)
    if opi_file_list == [] :
        print (f"Error: {inputFolder} does not contain .opi files")
        return 

    opi_dir_list_unique = []
    bob_dir_list_unique = []
    opi_resized_dir_list = []

    #Check if inputFolder exists and is a folder 
    if not os.path.isdir(inputFolder):
        print(f"Error: {inputFolder} does not exist or is not a folder")
        return
    opi_file_list = search_files(".opi", inputFolder)

    #Resize opi and convert opi in bob
    for opi_file in opi_file_list:
        opi_subdir = os.path.dirname(opi_file)
        head, sep, tail = opi_file.partition("/opi/")
        opi_dir = head + sep

        #Recreate the paths to the file inside bob and resized_opi folders
        sep_bob = re.sub("opi", "bob", sep)
        tail_bob = re.sub("opi", "bob", tail)
        path_to_bob_file = head + sep_bob + tail_bob 
        sep_resized_opi = re.sub("opi", "resized_opi", sep)  
        path_to_resized_opi_file = head + sep_resized_opi + tail    

        
        if opi_subdir not in opi_dir_list_unique:
            opi_dir_list_unique.append(opi_subdir)
            bob_subdir = os.path.dirname(path_to_bob_file) 

            if not "opi" in opi_subdir:
                print(f"opi files in {opi_subdir} are not converted because they are not in a folder named 'opi' ")
                continue
            
            #Replicate the opi folder in a bob folder          
            if not os.path.exists(bob_subdir):
                shutil.copytree(opi_subdir, bob_subdir, symlinks = True, ignore=shutil.ignore_patterns('*.opi'))
            elif opi_subdir == opi_dir_list_unique[0] :
                print('bob folder already exists')
            
            #Case where a opi/opi/ folder exists
            BobOpi_dir_list = search_dirs("opi", bob_subdir)
            if BobOpi_dir_list:
                for BobOpi in BobOpi_dir_list:
                    if os.path.exists(BobOpi):
                        shutil.rmtree(BobOpi)

            #Resize
            opi_resized_dir = head + sep_resized_opi
            if opi_resized_dir not in opi_resized_dir_list:
                opi_resized_dir_list.append(opi_resized_dir)

                if not os.path.exists(opi_resized_dir):
                    print(f"Creating the folder : {opi_resized_dir}")
                    shutil.copytree(opi_dir, opi_resized_dir, symlinks = True)                   
                
                    opiResized_file_list = search_files(".opi", opi_resized_dir)
                    for opi_to_resize in opiResized_file_list:
                        if not os.path.islink(opi_to_resize):
                            print(f"Resizing : {opi_to_resize}")
                            opi_resizing(opi_to_resize) 
                        else:
                            print(f"{opi_to_resize} is a symbolic link")                           
                            
            #Conversion
            opi_resized_dir = os.path.dirname(path_to_resized_opi_file)
            conversion(opi_resized_dir, bob_subdir, phoebusFolder) 
            
            #Update the bob file
            bob_dir = head + sep_bob
            if bob_subdir not in bob_dir_list_unique:
                bob_dir_list_unique.append(bob_subdir)
                bob_file_list = search_files(".bob", bob_subdir)
                for bob_file in bob_file_list:
                    bob_updating(bob_file, bob_dir)
            
        #Recreate symbolic links inside bob dir
        if os.path.islink(opi_file) :
            path_to_opi = os.path.dirname(opi_file)
            path_to_bob = re.sub("opi", "bob", path_to_opi)
            file_name = os.path.basename (opi_file)
            bob_link = re.sub("opi", "bob", opi_file)
            os.remove(bob_link)
            source = os.readlink(opi_file)
            source_bob = re.sub("opi", "bob", source)
            destination = re.sub("opi", "bob", file_name)
            os.chdir(path_to_bob)
            os.symlink(source_bob, bob_link)

    #Delete resized_opi folder
    for dir in search_dirs("resized_opi", inputFolder):
        if os.path.exists(dir):
            print(f"Deleting the folder : {dir}")  
            shutil.rmtree(dir)
       
    

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='This python scripts create the same bob folder architecture (with the same content, such as symbolic links, scripts or other documents) as the opi folder, resize CSS opi windows, convert all CSS opi files to Phoebus bob files, and then update the Phoebus bob files.')
    parser.add_argument('opi_folder', help='Path to the opi folder which contains the CSS opi files to convert. !!Prerequisit : the opi files have to be stored in a folder named opi')
    parser.add_argument('phoebus_folder', help='Path to the phoebus installation folder')

    args = parser.parse_args()
    
main()
