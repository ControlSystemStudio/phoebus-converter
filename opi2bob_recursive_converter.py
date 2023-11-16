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
#contributor : Mathis Huriez

import argparse
from ast import arg
from genericpath import exists
import os
import subprocess
import re
import shutil
import platform
from resize_opi import opi_resizing
from bob_update import bob_updating

#This function is like re.sub but replace only the last occurrence
def re_sub_lo(pattern, replacement, text):
    reversed_text = text[::-1]
    reversed_replacement = replacement[::-1]
    result = re.sub(pattern, reversed_replacement, reversed_text, count=1)
    return result[::-1]

#This function return the first re.match() of a folder path for a given filter
def get_match(filter_name, relative_path):
    if filter_name.startswith('*') and filter_name.endswith('*'):
        pattern_str = rf'.*{re.escape(filter_name[1:-1])}.*'
        regex_pattern = re.compile(pattern_str)
    elif filter_name.startswith('*') :
        pattern_str = rf'.*{re.escape(filter_name[1:])}$'
        regex_pattern = re.compile(pattern_str)
    elif filter_name.endswith('*') :
        pattern_str = rf'{re.escape(filter_name[:-1])}.*'
        regex_pattern = re.compile(pattern_str)
    else:
        regex_pattern = filter_name
    
    subfolder_list = relative_path.split(os.sep)

    for subfolder in subfolder_list:
        if re.match(regex_pattern, subfolder):
            return subfolder
    return None

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
    system = platform.system()
    install_path = phoebusFolder
    script_directory = os.path.dirname(os.path.abspath(__file__))
    #Try to get the java binary
    if args.java :
        java_path = args.java
    else :
        java_path = 'java'
    try:
        subprocess.run([java_path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        if system == "Linux" : 
            java_path = os.path.join(script_directory, 'java', 'linux-jdk-16.0.2', 'bin', 'java')
        if system == "Windows" : 
            java_path = os.path.join(script_directory, 'java', 'windows-jdk-16.0.2', 'bin', 'java')
    classpath = os.path.join(install_path, 'lib', '*')
    opi_files = os.path.join (opi_subdir, "*.opi")
    cmd = java_path + " -Dswing.defaultlaf=javax.swing.plaf.nimbus.NimbusLookAndFeel" + " -cp " + classpath + " org.csstudio.display.builder.model.Converter " + "-output " + bob_subdir + " " + opi_files
    subprocess.call(cmd, shell=True)
    return

def main():
    inputFolder = os.path.normpath(args.opi_folder)
    phoebusFolder = os.path.normpath(args.phoebus_folder)
    parentFolder = os.path.abspath(os.path.join(inputFolder, os.pardir))

    if inputFolder.endswith(os.path.sep):
        inputFolder = inputFolder[:-1]

    if phoebusFolder.endswith(os.path.sep):
        phoebusFolder = phoebusFolder[:-1]

    #Delete former resized_opi folder(s) if it exists
    for resized_dir in search_dirs("resized_opi", parentFolder):
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
    previous_bob_dir_list_unique = []
    opi_resized_dir_list = []

    #Check if inputFolder exists and is a folder 
    if not os.path.isdir(inputFolder):
        print(f"Error: {inputFolder} does not exist or is not a folder")
        return
    opi_file_list = search_files(".opi", inputFolder)

    #Resize opi and convert opi in bob
    for opi_file in opi_file_list:
        opi_subdir = os.path.dirname(opi_file)
        basename = os.path.basename(inputFolder)
        folder_relative_path = os.path.relpath(opi_subdir, inputFolder)
        file_relative_path = os.sep + os.path.relpath(opi_file, inputFolder)
        #Match is the input folder basename by default if no filter args
        match = basename

        #Search for match if filter is an argument
        #Separate the path at the matched folder
        if args.filter:
            filter_name = args.filter

            match = get_match(filter_name, folder_relative_path)
            if(match):
                head, sep, tail = file_relative_path.partition(os.sep + match + os.sep)
                head = inputFolder + head

                if filter_name == "opi" :
                    if not "opi" in opi_subdir:
                        print(f"opi files in {opi_subdir} are not converted because they are not in a folder named 'opi' ")
                        continue
            else :
                continue
        else :
            head, sep, tail = opi_file.rpartition(os.sep + match + os.sep)

        #Recreate the paths to the file inside resized_opi and bob folders
        opi_dir = head + sep
        if match == "opi" :
            sep_bob = re.sub(match, "bob", sep)
            sep_resized_opi = re.sub(match, "resized_opi", sep)
        else :
            sep_bob = re.sub(match, match + "_bob", sep)
            sep_resized_opi = re.sub(match, match + "_resized_opi", sep)
        tail_bob = re.sub(r"\.opi$", ".bob", tail)
        path_to_bob_file = head + sep_bob + tail_bob
        path_to_resized_opi_file = head + sep_resized_opi + tail
        bob_dir = head + sep_bob

        if opi_subdir not in opi_dir_list_unique:
            opi_dir_list_unique.append(opi_subdir)
            bob_subdir = os.path.dirname(path_to_bob_file)            

            #Create bob folder or not
            if args.bobdir:
                #Replicate the opi folder in a bob folder  
                if not os.path.exists(bob_subdir):
                    print(f"Creating the folder : {bob_subdir}")
                    shutil.copytree(opi_dir, bob_dir, symlinks = True, ignore=shutil.ignore_patterns('*.opi'))
                elif opi_subdir == opi_dir_list_unique[0]:
                    print(f"{bob_subdir} : the folder already exists and its contents may be different from the equivalent opi folder, you need to rename or delete it to generate a bob folder exactly like the opi folder.")
                
                #Case where a opi/opi/ folder exists
                if match == "opi" :
                    BobOpi_dir_list = search_dirs("opi", bob_subdir)
                    if BobOpi_dir_list:
                        for BobOpi in BobOpi_dir_list:
                            if os.path.exists(BobOpi):
                                shutil.rmtree(BobOpi)

            else :
                bob_subdir = opi_subdir
                bob_dir = opi_dir

            # Delete previous converted bob files (but not other bob files)                 
            if args.override:
                if bob_subdir not in previous_bob_dir_list_unique:
                    previous_bob_dir_list_unique.append(bob_subdir)
                    previous_bob_file_list = search_files(".bob", bob_subdir)
                    sub_opi_file_list = search_files(".opi", opi_subdir)
                    for previous_bob_file in previous_bob_file_list:
                        if os.path.exists(previous_bob_file):
                            for sub_opi_file in sub_opi_file_list:
                                compare = re.sub(r"\.opi$", ".bob", os.path.basename(sub_opi_file))
                                if compare == os.path.basename(previous_bob_file):
                                    os.remove(previous_bob_file)
                                    print(f"Previous bob file : {previous_bob_file} deleted")

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

            #Update bob files
            if bob_subdir not in bob_dir_list_unique:
                bob_dir_list_unique.append(bob_subdir)
                bob_file_list = search_files(".bob", bob_subdir)
                for bob_file in bob_file_list:
                    bob_updating(bob_file, bob_dir, args.log)

        #Recreate symbolic links inside bob dir
        if args.bobdir:
            if os.path.islink(opi_file) :
                path_to_opi = os.path.dirname(opi_file)
                path_to_bob = re.sub(match, "bob", path_to_opi)
                bob_link = re.sub(r"\.opi$", ".bob", opi_file)
                os.remove(bob_link)
                source = os.readlink(opi_file)
                source_bob = re.sub(match, "bob", source)
                os.chdir(path_to_bob)
                os.symlink(source_bob, bob_link)

    #Delete resized_opi folder(s)
    for dir in search_dirs("resized_opi", parentFolder):
        if os.path.exists(dir):
            print(f"Deleting the folder : {dir}")
            shutil.rmtree(dir)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='''
-----------------------------
|     PHOEBUS CONVERTER     |
-----------------------------

Description :                                     
    This python scripts resize CSS opi windows, convert all CSS opi files to Phoebus bob files, and then update the Phoebus bob files.
    ''', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f" , "--filter", help="Add a filter for specific folder's files to be converted, * to front and/or back are supported as regex, Warning !! The filter is case sensitive ; e.g. -f opi")
    parser.add_argument("-j" , "--java", help="Specify the java binary path manually ; e.g. -j C:\\Dev\\java\\windows-jdk-16.0.2\\bin\\java")
    parser.add_argument("-l" , "--log", action="store_true", help="Add log file(s) when conversion is finished")
    parser.add_argument("-o" , "--override", action="store_true", help="Override previous converted bob files (but not other bob files)")
    parser.add_argument("-bd" , "--bobdir", action="store_true", help="The converted files are placed in a bob directory with  the same content, such as symbolic links, scripts or other documents as the opi folder")
    parser.add_argument('opi_folder', help='Path to the folder which contains the CSS opi files to convert ; e.g. C:\\path_to_folder\\folder')
    parser.add_argument('phoebus_folder', help='Path to the phoebus installation folder, phoebus folder is required to use the opi2bob converter ; e.g. C:\\Software\\Phoebus\\phoebus-4.7.3')
    
    args = parser.parse_args()
    
main()
