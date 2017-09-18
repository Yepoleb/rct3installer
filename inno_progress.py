import tempfile
import subprocess
import re

FILENAME_RE = re.compile(r'^ - "(.+?)"')
PROGRESS_RE = re.compile(r'^\[.*?(\d{1,3}.\d)% +(.+B/s)')

FILTERED_STRINGS = [b"\x1b[K", b"\r", b"\n"]

def extract_gui():
    with tempfile.TemporaryDirectory() as tempdir:
        innoextract_cmd = [INNOEXTRACT_BIN, "-e", "-q", "--color=0", "--progress=1",
            "-d", tempdir, installer_path]
        error_log = open("error_log.txt", "w")
        process = subprocess.Popen(innoextract_cmd, bufsize=-1, 
            stdout=subprocess.PIPE, stderr=error_log)
        
        out_buffer = b""
        cur_filename = ""
        cur_progress = ""
        cur_speed = ""
        while True:
            char = process.stdout.read(1)
            if not char:
                break
            if char in (b"\n", b"\r"):
                line = out_buffer
                out_buffer = b""
                for filterstring in FILTERED_STRINGS:
                    line = line.replace(filterstring, b"")
                if not line:
                    continue
                line_str = line.decode("utf-8")
                #print(line_str)
                filename_match = FILENAME_RE.match(line_str)
                progress_match = PROGRESS_RE.match(line_str)
                if (filename_match):
                    cur_filename = filename_match.group(1)
                if (progress_match):
                    cur_progress = float(progress_match.group(1))
                    cur_speed = progress_match.group(2)
                print(cur_filename, cur_progress, cur_speed)
            else:
                out_buffer += char

        process.poll()
        error_log.close()

        if process.returncode != 0:
            print("Unpacking failed, check error log at ...")
        else:
            print("Success!")
