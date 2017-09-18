import tempfile
import subprocess
import shutil
import shlex
import os
import posixpath as path
import ntpath

import xdg.BaseDirectory
import xdg.DesktopEntry
import PIL.Image

APPNAME = "weingarten"

LAUNCHSCRIPT_TEMPLATE = \
"""#!/bin/sh

export WINEPREFIX='{prefix}'
PREV_DIR="$(pwd)"
cd '{running_dir}'
wine '{exe}'
cd "$PREV_DIR"
"""

INNOEXTRACT_BIN = shutil.which("innoextract")
WINE_BIN = shutil.which("wine")
WRESTOOL_BIN = shutil.which("wrestool")

dirs = {}
dirs["data"] = path.join(xdg.BaseDirectory.xdg_data_home, APPNAME)
dirs["menu"] = path.join(
    xdg.BaseDirectory.xdg_data_home, "applications", APPNAME)
dirs["prefix"] = path.join(dirs["data"], "prefix")
dirs["icons"] = path.join(dirs["data"], "icons")
dirs["scripts"] = path.join(dirs["data"], "scripts")

class WeinGartenError(RuntimeError):
    pass

def extract_innosetup(installer_path, tempdir):
    innoextract_cmd = [INNOEXTRACT_BIN, "-s", "--progress=1", "-d", tempdir, 
        installer_path]
    inno_proc = subprocess.Popen(innoextract_cmd)
    inno_proc.wait()
    if inno_proc.returncode != 0:
        raise WeinGartenError("Unpacking failed")
    else:
        print("Unpacking succeded!")

def create_datadirs():
    for dirname in ["data", "prefix", "icons", "scripts"]:
        os.makedirs(dirs[dirname], exist_ok=True)

class WinePrefix:
    def __init__(self, name, arch="win32"):
        self.name = name
        self.arch = arch
        self.prefix_path = path.join(dirs["prefix"], name)        
    
    def create(self):
        ret = self.run([WINE_BIN, "wineboot"])
        if ret != 0:
            errmsg = "Failed to create wineprefix for {}".format(name)
            raise WeinGartenError(errmsg)

    def exists(self):
        return path.exists(self.prefix_path)

    def delete(self):
        shutil.rmtree(self.prefix_path)

    def run(self, cmd):
        proc_env = os.environ.copy()
        proc_env["WINEPREFIX"] = self.prefix_path
        proc_env["WINEARCH"] = self.arch
        
        wine_proc = subprocess.Popen(cmd, env=proc_env)
        return wine_proc.wait()
    
    def install(self, src, dest):
        # Rstrip slash to make basename behave correctly
        install_path = self.path_for(dest).rstrip("/")
        install_dir = path.dirname(install_path)
        if install_dir:
            os.makedirs(install_dir, exist_ok=True)
        shutil.move(src, install_path)
    
    def path_for(self, local_path):
        drive, tail = ntpath.splitdrive(local_path)
        drive = drive.lower()
        
        if (not drive) or (drive == "c:"):
            drivepath = path.join(self.prefix_path, "drive_c")
        else:
            drivepath = path.join(self.prefix_path, "dosdevice", drive)
        
        # TODO: Is this enough for converting the path?
        tail_unix = tail.lstrip("\\").replace("\\", "/")
        
        return path.join(drivepath, tail_unix)

    def extract_icon(self, name, exe_path):
        full_exe_path = self.path_for(exe_path)

        ico_path = path.join(dirs["icons"], name + ".ico")
        png_path = path.join(dirs["icons"], name + ".png")

        wres_proc = subprocess.Popen([WRESTOOL_BIN, "-x", "-t14", "-o", 
            ico_path, full_exe_path])
        wres_proc.wait()
        if not path.exists(ico_path):
            raise WeinGartenError("Failed to extract icon")
        
        # Convert ico to png
        # TODO: Support multiple sizes
        # TODO: Use system directories
        img = PIL.Image.open(ico_path)
        img.save(png_path)
        return png_path

    def create_startscript(self, name, exe_path):
        full_exe_path = self.path_for(exe_path)
        script_path = path.join(dirs["scripts"], name)
        running_dir = path.dirname(full_exe_path)
        exe_name = path.basename(full_exe_path)
        
        with open(script_path, "w") as script_file:
            script_txt = LAUNCHSCRIPT_TEMPLATE.format(
                prefix=shlex.quote(self.prefix_path),
                running_dir=shlex.quote(running_dir),
                exe=shlex.quote(exe_name))
            script_file.write(script_txt)
        return script_path
    
    def create_starter(self, name, title, exe_path, categories, comment=""):        
        icon_path = self.extract_icon(name, exe_path)
        script_path = self.create_startscript(name, exe_path)
        starter_path = path.join(dirs["menu"], name + ".desktop")
        
        starter = xdg.DesktopEntry.DesktopEntry(starter_path)
        starter.set("Name", title)
        starter.set("Icon", icon_path)
        starter.set("Exec", script_path)
        starter.set("Categories", categories)
        if comment:
            starter.set("Comment", comment)
        starter.write()
    
    def get_path(self):
        return self.prefix_path
    
    def get_arch(self):
        return self.arch
