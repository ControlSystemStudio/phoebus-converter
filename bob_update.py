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

import xml.etree.ElementTree as ET
import logging
import os

def bob_updating(bob_file, bob_dirname):
    tree = ET.parse(bob_file)
    root = tree.getroot()

    format = '%(asctime)s -  %(levelname)-8s - %(message)s'
    logfile = bob_dirname + os.sep + "Conversion_opi_to_bob.log"
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    logging.basicConfig(format=format, level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S', force=True, handlers=[logging.FileHandler(logfile, mode='a'), stream_handler])
    
    bob_file_name = os.path.basename(bob_file)  
    logging.info(f"Updating: {bob_file_name} ")

    i = 0
    j = 0
    k = 0
    l = 0
    same_bob = ""

    #update the link to other Phoebus bob
    for file in root.iter('file'):
        if file is not None:
            opi = str(file.text)
            bob = str(opi.replace("opi","bob"))
            file.text = bob
            if same_bob == bob:
                i += 1
                same_bob = bob
            elif same_bob != "":
                if i == 0 or i == 1:
                    logging.debug(f"the link to the graphical interface: {same_bob} has been updated")
                else:
                    logging.debug(f"the link to the graphical interface: {same_bob} have been updated {i} times")
                same_bob = bob
                i = 0
            else:
                i += 1
                same_bob = bob

    if same_bob != "":
        if i == 0 or i == 1:
            logging.debug(f"the link to the graphical interface: {same_bob} has been updated")
        else:
            logging.debug(f"the link to the graphical interface: {same_bob} have been updated {i} times")  

    #Delete gridLayout widget
    for gridLayout in root.findall('widget'):
        if gridLayout is not None and gridLayout.get('typeId') == "org.csstudio.opibuilder.widgets.gridLayout":
            root.remove(gridLayout)
            i += 1
    for widget in root.iter('widget'):
        for gridLayout in widget.findall('widget'):
            if gridLayout is not None and gridLayout.get('typeId') == "org.csstudio.opibuilder.widgets.gridLayout":
                widget.remove(gridLayout)
                i += 1
        #update the color property name of polyline widget
        if widget.get('type') == "polyline":
            for rule in widget.findall('./rules/rule'):
                if rule is not None:
                    rule.set('prop_id', 'line_color')
                    k += 1

        if widget.get('type') == "xyplot":
            l += 1
    

    for script in root.iter('script'):
        if script is not None:
            script = script.get('file')
            if "changeMacroValue.js" in script:
                logging.warning(f"the script: {script} can be remplaced by a simpler embedded script")
            else:
                logging.warning(f"the script: {script} may not work")
        
        
    if j !=0:
        logging.debug(f"{i} gridLayout widgets have been removed")
    
    if k !=0:
        logging.debug(f"{k} polyline widgets have been updated")

    if l !=0:
        if l ==1:
            logging.warning(f"there is 1 xyplot that might have a different behavior")
        else:
            logging.warning(f"there are {l} xyplot that might have a different behavior")

    tree.write(bob_file, xml_declaration=True, method='xml', encoding='UTF-8')

    while True:
        try:
            tree = ET.parse(bob_file)
            break
        except Exception:
            print("Error:", {bob_file}, "is corrupted")
            break