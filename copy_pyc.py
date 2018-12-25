# coding: utf-8

import os
import compileall
import shutil
import filecmp

root = os.getcwd()

#print root


def copy_pyc():
    compileall.compile_dir(root, ddir=".", force=1, quiet=1)
    svn_root = "D:\dyz\server_out\dlqh"
    basename = os.path.basename(root)
    svn_path = os.path.join(svn_root, basename)
    print "svn_path", svn_path
    for r, d, f_list in os.walk(root):
        # print r
        # print d
        # print f_list
        pyc_list = []
        for f in f_list:
            if f.endswith(".pyc") or f in ("system.conf", "requirements.txt", "readme.md", "start.sh", "web.conf"):
                pyc_list.append(f)

        if not pyc_list:
            continue
        sub_dir = os.path.join(svn_path, r.split(basename)[1].strip('\\'))
        # print "svn_path", svn_path, r.split(basename)[1]
        # print "sub_dir", sub_dir
        if not os.path.exists(sub_dir):
            os.mkdir(sub_dir)
        # print pyc_list
        for pyc in pyc_list:
            src = os.path.join(r, pyc)
            dest = os.path.join(sub_dir, pyc)
            if not os.path.exists(dest) or not filecmp.cmp(src, dest):
                print pyc
            shutil.copyfile(src, dest)
        # print "\n", "-" * 100

if __name__ == '__main__':
    copy_pyc()
