#!/usr/bin/env python3

import argparse
from datetime import datetime
import os
import shutil
import subprocess
import glob
import re
import docker

# Using QPDF to decrypt file
QPDF_PATH = "/usr/local/bin/qpdf"


class Profile:
    def __init__(self, pattern, date_index, date_format, out_format):
        self.pattern = re.compile(pattern)
        self.date_index = date_index
        self.date_format = date_format
        self.out_format = out_format

    def match(self, filename):
        return self.pattern.match(filename)

    def format(self, filename):
        p = self.pattern.match(filename)
        groups = p.groups()
        output = self.out_format
        for i in range(0, len(groups)):
            output = output.replace('\\' + str(i), groups[i])

        date = datetime.strptime(groups[self.date_index], self.date_format).strftime('%Y-%m-%d')
        output = output.replace('\\d', date)
        return output


profiles = {
    'cc_pattern': Profile('(\d{4})-XXXX-XXXX-(\d{4})_(\d{8}).pdf', 2, '%d%m%Y', 'CC-\\1_\\d.pdf'),
    'acc_pattern': Profile('E-STATEMENT_(\d{2} \S{3} \d{4})_(\d{3}).pdf', 0, '%d %b %Y', 'ACC-8\\1_\\d.pdf'),
    'acc2_pattern': Profile('E-STATEMENT_(\d{2} \S{3} \d{4})_(\d{4}).pdf', 0, '%d %b %Y', 'ACC-\\1_\\d.pdf')
}


def process_file(file, password=None, out_dir=None, qpdf_path=None):
    in_file = os.path.basename(file)
    in_dir = os.path.dirname(file)

    out_file = ''
    profile = None
    for p in profiles.keys():
        if profiles[p].match(in_file):
            profile = profiles[p]
            continue
    if not profile:
        print('No profile matching {}. Skip'.format(file))
        return

    out_file = profile.format(in_file)


    if out_dir:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    else:
        out_dir = in_dir

    ofile = os.path.join(out_dir, out_file)
    if password:
        # decrypt PDF
        print("Decrypting {}...".format(file), sep="", end="", flush=True)
        exec_qpdf(in_dir, in_file, out_dir, out_file, password, qpdf_path)
        print("\rDecrypted {}{}".format(ofile, " " * 40))
    else:
        print("Renamed {}".format(ofile))
        shutil.copyfile(file, ofile)


def exec_qpdf(in_dir, in_file, out_dir, out_file, password, qpdf_path):
    if not qpdf_path:
        qpdf_path = QPDF_PATH

    if qpdf_path.startswith("/"):
        ifile = os.path.join(in_dir, in_file)
        ofile = os.path.join(out_dir, out_file)
        proc = subprocess.run([QPDF_PATH, "--password={}".format(password), "--decrypt", ifile, ofile],
                              universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode != 3 and proc.returncode != 0:
            print(proc.stderr)
    else:
        try:
            client = docker.from_env()
            in_dir = os.path.abspath(in_dir)
            out_dir = os.path.abspath(out_dir)

            c = client.containers.create(volumes=[in_dir + ':/pdf/input', out_dir + ':/pdf/output'],
                                         image=qpdf_path,
                                         command='/usr/bin/qpdf --password={} --decrypt "{}" "{}"'
                                         .format(password,
                                                 os.path.join('/pdf/input', in_file),
                                                 os.path.join('/pdf/output', out_file)))
            c.start()
        except Exception as ce:
            # catch qpdf code different from 0
            print(ce)

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