import posixpath as path
import ntpath
import tempfile

import weingarten

PROGRAM_LOCATION = "C:\\Program Files\\Atari\\Roller Coaster Tycoon 3\\"

#~ installer_path = "/home/gabriel/temp/rct3 unpack/setup_rollercoaster_tycoon3_2.1.0.16.exe"

def choose_installer():
    while True:
        inst_input = input("Installer location: ")
        inst_path = path.realpath(path.expanduser(inst_input))
        if path.exists(inst_path):
            return inst_path
        else:
            print("Path doesn't exist or can't be accessed")

def get_bool_answer(text):
    while True:
        answer = input(text + " [y/n]: ")
        if answer.lower() == "y":
            return True
        elif answer.lower() == "n":
            return False
        else:
            print("Invalid input, please enter y or n")

def create_prefix(name, arch="win32"):
    prefix = weingarten.WinePrefix(name, arch)
    if (prefix.exists()):
        should_recreate = get_bool_answer(
            "Prefix already exists, do you want to recreate it?")
        if should_recreate:
            print("Recreating prefix")
            prefix.delete()
            prefix.create()
    else:
        print("Creating prefix")
        prefix.create()
    return prefix

installer_path = choose_installer()
prefix = create_prefix("rct3", "win32")

with tempfile.TemporaryDirectory() as tempdir:
    print("Extracting files")
    weingarten.extract_innosetup(installer_path, tempdir)
    print("Installing files")
    prefix.install(path.join(tempdir, "app"), PROGRAM_LOCATION)

prefix.create_starter(
    name="rct3",
    title="RollerCoaster Tycoon 3",
    exe_path=ntpath.join(PROGRAM_LOCATION, "RCT3plus.exe"),
    categories="Game;Simulation;",
    comment="Amusement park simulator")
