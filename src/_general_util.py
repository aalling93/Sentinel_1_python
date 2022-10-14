import os, zipfile


def unzip_path(dir_name):
    cuurent_dir = os.getcwd()
    os.chdir(dir_name)
    for file in os.listdir(os.getcwd()):   
        if zipfile.is_zipfile(file): 
            with zipfile.ZipFile(file) as item: 
                item.extractall()  

    os.chdir(cuurent_dir)