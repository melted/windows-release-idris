import sys
import os
import shutil
import subprocess

target_dir="D:/Niklas/idris-build/"
repo_dir="D:/Niklas/repo/Idris-dev/"
msys_dir="D:/msys64/"
toolchain32=target_dir+"mingw32/"
toolchain64=target_dir+"mingw64/"
archive_dir="Z:/idris-build/idris/"

if len(sys.argv) < 2:
    print("No version argument")
    exit()

version = sys.argv[1]

rts32 = repo_dir+".cabal-sandbox/i386-windows-ghc-7.10.3/idris-"+version
rts64 = repo_dir+".cabal-sandbox/x86_64-windows-ghc-7.10.3/idris-"+version
target32 = target_dir + "idris-" + version + "-win32/idris"
target64 = target_dir + "idris-" + version + "/idris"

os.makedirs(target32)
os.makedirs(target64)

shutil.copytree(toolchain32, target32+"/mingw")
shutil.copytree(toolchain64, target64+"/mingw")

p = subprocess.run([msys_dir+"usr/bin/cygpath", "-u", repo_dir], shell=True,
                    stdout = subprocess.PIPE)

posix_repo = p.stdout

shellscript64 = "cd " + posix_repo.decode().rstrip() + " && ./win-release.sh"
shellscript32 = "PATH=/d/Apps/ghc-7.10.3-i386/bin:$PATH && " + shellscript64

def build(target, rts_dir, shellscript):
    bin_dir = repo_dir+".cabal-sandbox/bin/"
    make_cmd = [msys_dir + 'usr/bin/bash', '-l', '-c', shellscript]
    print(make_cmd)
    subprocess.run(make_cmd)
    shutil.copy(bin_dir+"idris.exe", target)
    shutil.copy(bin_dir+"idris-codegen-c.exe", target)
    shutil.copy(bin_dir+"idris-codegen-javascript.exe", target)
    shutil.copy(bin_dir+"idris-codegen-node.exe", target)
    shutil.copytree(rts_dir, target+"/libs")

os.chdir(repo_dir)
os.putenv("MSYSTEM", "MINGW32")
build(target32, rts32, shellscript32)

os.putenv("MSYSTEM", "MINGW64")
build(target64, rts64, shellscript64)
