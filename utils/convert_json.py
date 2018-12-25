# coding: utf-8

import os
import re
from copy import copy
import argparse

test_json = """
            {
              "CMT_SINGLE_LINE": 1, // this is a single line comment
              /*
              this is a multi-line comment
              */
              "CMD_TEST": 1
            }
            """


class ConvertScript(object):
    def __init__(self, source, target, script=None):
        self.source = source
        self.target = target
        self.script = script if script else ['php', 'py', 'js']
        self.re = re.compile(r'\"[\w_]+\":\s*\d')

    def to_php(self):
        final_file = "<?php\n"
        with open(self.source) as fp:
            for raw_line in fp.readlines():
                line = raw_line.strip()
                if ',' in line:
                    line = line.replace(',', ';')
                if '{' in line:
                    line = line.replace('{', '')
                if '}' in line:
                    line = line.replace('}', '')
                for i in self.re.findall(line):
                    old = copy(i)
                    i = i.replace('"', '$', 1)
                    i = i.replace('"', '', 1)
                    i = i.replace(':', ' =', 1)
                    line = line.replace(old, i)
                    if '\\' not in line:
                        line += ";"
                final_file += line + "\n"
        final_file += "?>"
        with open(os.path.join(self.target, "conf.php"), "w") as fp:
            fp.write(final_file)
        return final_file

    def to_py(self):
        final_file = ""
        with open(self.source) as fp:
            for raw_line in fp.readlines():
                line = raw_line.strip()
                if '{' in line:
                    line = line.replace('{', '')
                if '}' in line:
                    line = line.replace('}', '')
                if '//' in line:
                    line = line.replace('//', '#')
                if '/*' in line:
                    line = line.replace('/*', '"""')
                if '*/' in line:
                    line = line.replace('*/', '"""')
                if ',' in line:
                    line = line.replace(',', '')
                for i in self.re.findall(line):
                    old = copy(i)
                    i = i.replace('"', '')
                    i = i.replace(':', ' =', 1)
                    line = line.replace(old, i)

                final_file += line + "\n"
        with open(os.path.join(self.target, "conf.py"), "w") as fp:
            fp.write(final_file)
        return final_file

    def to_js(self):
        with open(self.source) as fp:
            f = fp.read()
        f = "var CMD = " + f
        with open(os.path.join(self.target, "conf.js"), "w") as fp:
            fp.write(f)
        return f

    def run(self):
        if 'php' in self.script:
            print self.to_php()
            print "-" * 32
        if 'py' in self.script:
            print self.to_py()
            print "-" * 32
        if 'js' in self.script:
            print self.to_js()
            print "-" * 32


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", dest="source", type=str, default="", help=u"要转换的源文件")
    parser.add_argument("-t", "--target", dest="target", type=str, default="", help=u"保存转换后的路径")
    parser.add_argument("-S", "--script", dest="script", type=str, default="py", choices=["php", "py", "js"],
                        nargs="*", help=u"要转换成的语言")
    args = parser.parse_args("".split())
    # parser.print_help()
    c = ConvertScript(args.source, args.target, args.script)
