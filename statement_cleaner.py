#!/usr/bin/env python3

import argparse
import datetime
import os
import shutil
import subprocess
import glob
import re
import docker

# Using QPDF to decrypt file
QPDF_PATH = "/usr/local/bin/qpdf"


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
    if account == "201":
        account = "8201"
    return parts[0] + "_" + account + "_" + d + ".pdf"


def process_file(file, password=None, out_dir=None, qpdf_path=None):
    in_file = os.path.basename(file)
    in_dir = os.path.dirname(file)

    out_file = ''
    if re.match("\\w{4}-\\w{4}-\\w{4}-\\w{4}", in_file):
        out_file = credit_card_formatter(in_file)
    if in_file.startswith("E-STATEMENT"):
        out_file = account_formatter(in_file)

    if out_dir:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    else:
        out_dir = in_dir

    if password:
        # decrypt PDF
        print("Decrypting {}...".format(file), sep="", end="", flush=True)
        exec_qpdf(in_dir, in_file, out_dir, out_file, password, qpdf_path)
        print("\rDecrypted {}{}".format(out_file, " " * 20))
    else:
        shutil.copyfile(file, os.path.join(out_dir, out_file))


def exec_qpdf(in_dir, in_file, out_dir, out_file, password, qpdf_path):
    if not qpdf_path:
        qpdf_path = QPDF_PATH

    if qpdf_path.startswith("/"):
        print("QPDF: local execution")
        ifile = os.path.join(in_dir, in_file)
        ofile = os.path.join(out_dir, out_file)
        proc = subprocess.run([QPDF_PATH, "--password={}".format(password), "--decrypt", ifile, ofile],
                              universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 3 and proc.returncode != 0:
            print(proc.stderr)
    else:
        print("QPDF: docker execution")
        try:
            client = docker.from_env()
            in_dir = os.path.abspath(in_dir)
            out_dir = os.path.abspath(out_dir)
            volumes = [{in_dir: {'bind': '/pdf/input', 'mode': 'ro'}},
                       {out_dir: {'bind': '/pdf/output', 'mode': 'rw'}}]

            c = client.containers.create(volumes=[in_dir + ':/pdf/input', out_dir + ':/pdf/output'],
                                         image=qpdf_path,
                                         command='/usr/bin/qpdf --password={} --decrypt {} {}'
                                         .format(password,
                                                 os.path.join('/pdf/input', in_file),
                                                 os.path.join('/pdf/output', out_file)))
            c.start()
        except docker.errors.ContainerError as ce:
            # catch qpdf code different from 0
            print(ce)
            pass

def main():
    parser = argparse.ArgumentParser(prog="statement_cleaner",
                                     description="Cleanup bank statements PDF files, formatting dates with ISO format "
                                                 "and removing encryption")

    source = parser.add_mutually_exclusive_group()
    source.required = True
    source.add_argument("-f", "--file", help="PDF filename to be cleaned")
    source.add_argument("-i", "--indir", help="Process all PDF files in this directory")
    parser.add_argument("-p", "--password", help="Password to decrypt PDF file, if encrypted")
    parser.add_argument("-o", "--outdir", help="Alternative directory to save files")
    qpdf = parser.add_mutually_exclusive_group()
    qpdf.add_argument("--qpdf-path", help="Absolute path to qpdf executable, eg: /usr/local/bin/qpdf", default=QPDF_PATH)
    qpdf.add_argument("--qpdf-docker-image", help="Docker image containing qpdf")

    args = parser.parse_args()

    qpdf_path = args.qpdf_docker_image if args.qpdf_docker_image else args.qpdf_path
    print(args)
    if args.indir:
        # process all PDF files in the directory
        for file in glob.glob(os.path.join(args.indir, "*.pdf")):
            process_file(file, args.password, args.outdir, qpdf_path)
    else:
        # process one single file
        process_file(args.file, args.password, args.outdir, qpdf_path)



if __name__ == "__main__":
    main()