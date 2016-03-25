import sys
import os
import shutil

target_dir="Z:/idris-build/idris/"
repo_dir="D:/Niklas/repo/Idris_dev/"
msys_dir="D:/msys64/"
toolchain32="Z:/idris-build/idris/mingw32/"
toolchain64="Z:/idris-build/idris/mingw64/"

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



def build(target, rts_dir):
    bin_dir = repo_dir+".cabal-sandbox/bin/"
    make_cmd = msys_dir + "usr/bin/bash --login win_release.sh"
    os.system(make_cmd)
    shutil.copy(bin_dir+"idris.exe", target)
    shutil.copy(bin_dir+"idris-codegen-c.exe", target)
    shutil.copy(bin_dir+"idris-codegen-javascript.exe", target)
    shutil.copy(bin_dir+"idris-codegen-node.exe", target)
    shutil.copytree(rts_dir, target+"/libs")
    os.chdir("libs")
    os.system("make clean")
    os.chdir("..")

os.chdir(repo_dir)
os.putenv("MSYSTEM", "MINGW32")
build(target32, rts32)

os.putenv("MSYSTEM", "MINGW64")
build(target64, rts64)
