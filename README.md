# CSS - Phoebus converter 

This python scripts resize CSS opi windows, convert all CSS resized opi files to Phoebus bob files, and then update the Phoebus bob files.

The originals opi are not affected by the script, duplicated opi files are being resized, and are deleted after the conversion.

The resizing step usefulness is to prevent phoebus embedded displays to scale with the window size rather than widgets size in the display.

By default, it will place created bob files next to opi files for each folder and subfolder of the user specified folder.

## arguments:
  opi_folder :  
  Path to the folder which contains the CSS opi files to convert ; e.g. C:\path_to_folder\folder

  phoebus_folder :  
  Path to the phoebus installation folder, phoebus folder is required to use the opi2bob converter ; e.g. C:\Software\Phoebus\phoebus-4.7.3

## optional arguments:
  -h, --help :  
  show this help message and exit

  -f FILTER, --filter FILTER :  
  Add a filter for specific folder's files to be converted, * to front and/or back are supported as regex, Warning !! The filter is case sensitive ; e.g. -f opi

  -j JAVA, --java JAVA :  
  Specify the java binary path manually ; e.g. -j C:\Dev\java\windows-jdk-16.0.2\bin\java

  -l, --log :  
  Add log file(s) when conversion is finished

  -o, --override :  
  Override previous converted bob files (but not other bob files).

  -bd, --bobdir :  
  The converted files are placed in a bob directory with  the same content, such as symbolic links, scripts or other documents as the opi folder

### Usage on Windows :
`Python_Bin_Path` `Script_Path` `Opi_folder_Path` `Phoebus_Installation_Path`

e.g. : `D:\python_windows\python` `D:\Phoebus\phoebus-4.7.2\tools\opi2bob_recursive_converter.py` `D:\EPICS\IOC\opi` `D:\Phoebus\phoebus-4.7.2`

### Usage on Linux :
`python` `Script_Path` `Opi_folder_Path` `Phoebus_Installation_Path`

e.g. : `python` `/home/user/phoebus-4.7.2/tools/opi2bob_recursive_converter.py` `/home/epics/ioc/opi` `/home/user/phoebus-4.7.2`



### Example of optional arguments usage :
- The usage : `D:\python_windows\python D:\Phoebus\phoebus-4.7.2\tools\opi2bob_recursive_converter.py -h`  
will display the help for the converter.

- The usage : `D:\python_windows\python D:\Phoebus\phoebus-4.7.2\tools\opi2bob_recursive_converter.py -f *opi D:\EPICS\IOC\opi D:\Phoebus\phoebus-4.7.2`  
will only convert .opi files that are in folders with names ending in "opi" and their subfolders.

- The usage : `D:\python_windows\python D:\Phoebus\phoebus-4.7.2\tools\opi2bob_recursive_converter.py -f test -bd D:\EPICS\IOC\opi D:\Phoebus\phoebus-4.7.2`  
will only convert .opi files that are in folders named "test" and their subfolders and put the bob files in a folder called test_bob.

- The usage : `D:\python_windows\python D:\Phoebus\phoebus-4.7.2\tools\opi2bob_recursive_converter.py -l D:\EPICS\IOC\opi D:\Phoebus\phoebus-4.7.2`  
will only convert .opi files and a Conversion_opi_to_bob.log with log messages (as well as displayed them in the console).

- The usage : `D:\python_windows\python D:\Phoebus\phoebus-4.7.2\tools\opi2bob_recursive_converter.py --java D:\java\windows-jdk-16.0.2\bin\java --filter *llrf* D:\EPICS\IOC\opi D:\Phoebus\phoebus-4.7.2`  
will only convert .opi files that are in folders with names containing "llrf" (case sensitive) and their subfolders. As well as using the java binary in argument to launch the conversion.

