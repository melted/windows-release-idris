import sys
import os
import shutil
import subprocess
import tempfile


# Configuration
target_dir  = "D:/Niklas/idris-build/"             # Where to build the release
repo_dir    = "D:/Niklas/repo/Idris-dev/"          # Where the idris repo is
msys_dir    = "D:/msys64/"                         # PAth to msys2. make, rsync, ssh, libffi (32/64) and gcc (32/64) needs to be installed
toolchain32 = target_dir+"mingw32/"                # Where the toolchain to be bundled with 32-bit build is
toolchain64 = target_dir+"mingw64/"                # Where the toolchain to be bundled with 64-bit build is
archive_dir = "Z:/idris-build/idris/"              # Not used yet. Where to store the release   
compressor  = "C:/Apps/7-zip/7z.exe"               # The path to the 7-zip executable
web_dir     = "D:/Niklas/repo/xim/neon/idris/"     # Where to copy the archives for web publication locally  
ghc32_posix = "/d/Apps/ghc-7.10.3-i386/bin"        # The path to the 32-bit GHC in msys-format  
upload_path = 'niklas@neon.se:/usr/local/www/neon/idris' # The server dir to rsync to.

if len(sys.argv) < 2:
    print("No version argument")
    exit()

version = sys.argv[1]

def posix_path(path):
    p = subprocess.run([msys_dir+"usr/bin/cygpath", "-u", path], shell=True,
                    stdout = subprocess.PIPE)
    return p.stdout.decode().rstrip()

web_posix = posix_path(web_dir)
repo_posix = posix_path(repo_dir)

bash = msys_dir + 'usr/bin/bash'

def build_docs(target):
    os.putenv("MSYSTEM", "MINGW64")
    print("Building docs in "+ target)
    command = "cd " + repo_posix + " && make user_docs"
    make_cmd = [bash, '-l', '-c', command]
    subprocess.run(make_cmd)
    shutil.copytree(repo_dir+'/docs/_build/html', target+'/html')
    shutil.copyfile(repo_dir+'/docs/_build/latex/idris.pdf', target+'/idris.pdf')

def build(target, rts_dir, shellscript, toolchain, doc_dir, bits):
    os.putenv("MSYSTEM", "MINGW" + str(bits))
    dist_dir = target + "/idris/"
    os.makedirs(dist_dir)
    shutil.copytree(toolchain, dist_dir+"/mingw")
    shutil.copytree(doc_dir, dist_dir+'/doc')
    bin_dir = repo_dir + ".cabal-sandbox/bin/"
    make_cmd = [bash, '-l', '-c', shellscript]
    subprocess.run(make_cmd)
    shutil.copy(bin_dir+"idris.exe", dist_dir)
    shutil.copy(bin_dir+"idris-codegen-c.exe", dist_dir)
    shutil.copy(bin_dir+"idris-codegen-javascript.exe", dist_dir)
    shutil.copy(bin_dir+"idris-codegen-node.exe", dist_dir)
    shutil.copytree(rts_dir, dist_dir + "/libs")
    archive_name  = target + '/idris-'+version+'-win'+ str(bits)
    compress_7z = [compressor, 'a','-r', '-mx9', archive_name + '.7z', dist_dir]
    compress_exe = [compressor, 'a','-r', '-mx9', '-sfx7z.sfx', archive_name + '.exe', dist_dir]
    subprocess.run(compress_7z)
    subprocess.run(compress_exe)
    shutil.copy(archive_name + '.7z', web_dir)
    shutil.copy(archive_name + '.exe', web_dir)
    
rts32 = repo_dir + ".cabal-sandbox/i386-windows-ghc-7.10.3/idris-" + version
rts64 = repo_dir + ".cabal-sandbox/x86_64-windows-ghc-8.0.1/idris-" + version
target32 = target_dir + "idris-" + version + "-win32"
target64 = target_dir + "idris-" + version

shellscript64 = "cd " + repo_posix + " && ./win-release.sh"
shellscript32 = "export PATH=" + ghc32_posix + ":$PATH && " + shellscript64

os.putenv("MSYS2_PATH_TYPE", "inherit")
os.chdir(repo_dir)
temp_doc_dir = tempfile.mkdtemp('', 'idris_doc')
build_docs(temp_doc_dir)
build(target32, rts32, shellscript32, toolchain32, temp_doc_dir, 32)
build(target64, rts64, shellscript64, toolchain64, temp_doc_dir, 64)

shutil.rmtree(temp_doc_dir)
subprocess.run([bash, '-l', '-c', 'rsync -avP ' + web_posix + ' ' + upload_path])
