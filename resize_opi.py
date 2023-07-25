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

def opi_resizing(opi_file):
	while True:
		try:
			tree = ET.parse(opi_file)
			break
		except Exception:
			print('Error:', {opi_file}, 'is corrupted')
			break
			
	X = []
	Y = []
	absc = []
	ordo = []

	tree = ET.parse(opi_file)
	root = tree.getroot()
	for widget in root.findall('widget'):
		if widget.find('x') is not None:
			x = int(widget.find('x').text)
			X.append(x)
			y = int(widget.find('y').text)
			Y.append(y)		
	X.sort()
	Y.sort()		
	for widget in root.findall('widget'):
		if widget.find('x') is not None:
			new_absc = int(widget.find('x').text) - X[0]
			new_ordo = int(widget.find('y').text) - Y[0]
			widget.find('x').text = str(new_absc)
			widget.find('y').text = str(new_ordo)
			width = int(widget.find('width').text)
			height = int(widget.find('height').text)
			abscissa_max = int(widget.find('x').text) + width
			absc.append(abscissa_max)
			ordinate_max = int(widget.find('y').text) + height
			ordo.append(ordinate_max)
	ordo.sort()
	absc.sort()
	for height in root.findall("height"):
		height.text = str(ordo[-1])
	for width in root.findall("width"):
		width.text = str(absc[-1]) 
	tree.write(opi_file, xml_declaration=True, method='xml', encoding='UTF-8')



