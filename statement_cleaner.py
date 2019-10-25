#!/usr/bin/env python3

import argparse
import datetime
import os
import shutil
import subprocess
import glob
import re

# Using QPDF to decrypt file
CMD = "/usr/local/bin/qpdf"


def credit_card_formatter(filename):
    parts = filename.split("_")
    dp = parts[1].split(".")[0]
    d = datetime.datetime.strptime(dp, "%d%m%Y").strftime("%Y-%m-%d")
    return parts[0] + "_" + d + ".pdf"


def account_formatter(filename):
    parts = filename.split("_")
    dp = parts[1]
    d = datetime.datetime.strptime(dp, "%d %b %Y").strftime("%Y-%m-%d")
    account = parts[2].split(".")[0]
    return parts[0] + "_" + account + "_" + d + ".pdf"


def process_file(file, password=None, outdir=None):
    basename = os.path.basename(file)
    dirname = os.path.dirname(file)

    new_file = ''
    if re.match("\\w{4}-\\w{4}-\\w{4}-\\w{4}", basename):
        new_file = credit_card_formatter(basename)
    if basename.startswith("E-STATEMENT"):
        new_file = account_formatter(basename)

    if outdir:
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        dirname = outdir
    new_file = os.path.join(dirname, new_file)

    if password:
        # decrypt PDF
        print("Decrypting {}...".format(file), sep="", end="", flush=True)
        proc = subprocess.run([CMD, "--password={}".format(password), "--decrypt", file, new_file],
                              universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 3 and proc.returncode != 0:
            print(proc.stderr)
        print("\rDecrypted {}{}".format(new_file, " " * 20))
    else:
        shutil.copyfile(file, new_file)


def main():
    parser = argparse.ArgumentParser(prog="statement_cleaner",
                                     description="Cleanup bank statements PDF files, formatting dates with ISO format "
                                                 "and removing encryption")

    group = parser.add_mutually_exclusive_group()
    group.required = True
    group.add_argument("-f", "--file", help="PDF filename to be cleaned")
    group.add_argument("-i", "--indir", help="Process all PDF files in this directory")
    parser.add_argument("-p", "--password", help="Password to decrypt PDF file, if encrypted")
    parser.add_argument("-o", "--outdir", help="Alternative directory to save files")

    args = parser.parse_args()

    if args.indir:
        # process all PDF files in the directory
        for file in glob.glob(os.path.join(args.indir, "*.pdf")):
            process_file(file, args.password, args.outdir)
    else:
        # process one single file
        process_file(args.file, args.password, args.outdir)



if __name__ == "__main__":
    main()