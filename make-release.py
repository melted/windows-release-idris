import sys
import os
import shutil
import subprocess


# Configuration
target_dir="D:/Niklas/idris-build/"
repo_dir="D:/Niklas/repo/Idris-dev/"
msys_dir="D:/msys64/"
toolchain32=target_dir+"mingw32/"
toolchain64=target_dir+"mingw64/"
archive_dir="Z:/idris-build/idris/"
compressor="C:/Apps/7-zip/7z.exe"
web_dir = "d:/Niklas/repo/xim/neon/idris/"


if len(sys.argv) < 2:
    print("No version argument")
    exit()

version = sys.argv[1]

p = subprocess.run([msys_dir+"usr/bin/cygpath", "-u", repo_dir], shell=True,
                    stdout = subprocess.PIPE)

posix_repo = p.stdout

bash = msys_dir + 'usr/bin/bash'


def build(target, rts_dir, shellscript, toolchain, bits):
    os.putenv("MSYSTEM", "MINGW" + str(bits))
    dist_dir = target+"/idris/"
    os.makedirs(dist_dir)
    shutil.copytree(toolchain, dist_dir+"/mingw")
    bin_dir = repo_dir+".cabal-sandbox/bin/"
    make_cmd = [bash, '-l', '-c', shellscript]
    print(make_cmd)
    subprocess.run(make_cmd)
    shutil.copy(bin_dir+"idris.exe", dist_dir)
    shutil.copy(bin_dir+"idris-codegen-c.exe", dist_dir)
    shutil.copy(bin_dir+"idris-codegen-javascript.exe", dist_dir)
    shutil.copy(bin_dir+"idris-codegen-node.exe", dist_dir)
    shutil.copytree(rts_dir, dist_dir+"/libs")
    archive_7z = target+'/idris-'+version+'-win'+ str(bits) + '.7z'
    archive_exe = target+'/idris-'+version+'-win' + str(bits) + '.exe'
    compress_7z = [compressor, 'a','-r', '-mx9', archive_7z, dist_dir]
    compress_exe = [compressor, 'a','-r', '-mx9', '-sfx7z.sfx', archive_exe, dist_dir]
    subprocess.run(compress_7z)
    subprocess.run(compress_exe)
    shutil.copy(archive_7z, web_dir)
    shutil.copy(archive_exe, web_dir)
    
rts32 = repo_dir+".cabal-sandbox/i386-windows-ghc-7.10.3/idris-"+version
rts64 = repo_dir+".cabal-sandbox/x86_64-windows-ghc-7.10.3/idris-"+version
target32 = target_dir + "idris-" + version + "-win32"
target64 = target_dir + "idris-" + version

shellscript64 = "cd " + posix_repo.decode().rstrip() + " && ./win-release.sh"
shellscript32 = "export PATH=/d/Apps/ghc-7.10.3-i386/bin:$PATH && " + shellscript64

os.putenv("MSYS2_PATH_TYPE", "inherit")
os.chdir(repo_dir)
build(target32, rts32, shellscript32, toolchain32, 32)
build(target64, rts64, shellscript64, toolchain64, 64)

subprocess.run([bash, '-l', '-c', 'rsync -avP /d/Niklas/repo/xim/neon/ niklas@neon.se:/usr/local/www/neon'])
