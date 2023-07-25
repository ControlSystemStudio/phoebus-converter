# CSS - Phoebus converter 

This python scripts create the same bob folder architecture (with the same content, such as symbolic links, scripts or other documents) as the opi folder, resize CSS opi windows, convert all CSS opi files to Phoebus bob files, and then update the Phoebus bob files.


!!Prerequisit : the opi files have to be stored in a folder named opi

Usage on Windows :
Phoebus_Installation_Path/python_windows/python Phoebus_Installation_Path/tools/opi2bob_recursive_converter.py opi_folder Phoebus_Installation_Path
ex : D:\Phoebus\phoebus-4.7.2\python_windows\python D:\Phoebus\phoebus-4.7.2\tools\opi2bob_recursive_converter.py D:\EPICS\IOC\opi D:\Phoebus\phoebus-4.7.2\

Usage on linux :
python Phoebus_Installation_Path/tools/opi2bob_recursive_converter.py opi_folder Phoebus_Installation_Path
python /home/user/phoebus-4.7.2/tools/opi2bob_recursive_converter.py /home/epics/ioc/opi /home/user/phoebus-4.7.2

