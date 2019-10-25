Introduction
============
A simple and small utility to help managing statements from bank and credit card accounts.

My bank send me statements via email, but there are two issues I am not confortable with:
* filename: it includes statement date, but not in ISO format, so there is no way to sort them
* encryption: PDF files are procted with a password, that I do not want to keep after I opened on my computer

This python utility rename the file to use date in ISO format, so name sorting overlaps with date sorting.
It also remote password protection, using qpdf utility.

In order to remove PDF password, qpdf tool is required:

    apt-get install qpdf # debian based linux
    brew install qpdf    # macOS

Optionally, QPDF can be execute from a docker image


Getting started
===============

usage: statement_cleaner [-h] (-f FILE | -i INDIR) [-p PASSWORD] [-o OUTDIR]
                         [--qpdf-path QPDF_PATH | --qpdf-docker-image QPDF_DOCKER_IMAGE]

Cleanup bank statements PDF files, formatting dates with ISO format and removing encryption

optional arguments:
  -h, --help                                show this help message and exit
  -f FILE, --file FILE                      PDF filename to be cleaned
  -i INDIR, --indir INDIR                   Process all PDF files in this directory
  -p PASSWORD, --password PASSWORD          Password to decrypt PDF file, if encrypted
  -o OUTDIR, --outdir OUTDIR                Alternative directory to save files
  --qpdf-path QPDF_PATH                     Absolute path to qpdf executable, eg: /usr/local/bin/qpdf
  --qpdf-docker-image QPDF_DOCKER_IMAGE     Docker image containing qpdf


Profiles
========

Profiles are supported to define the renaming rule, configurable via JSON file, eg:

    5432-XXXX-XXXX-1234_10022018.pdf -> CC-MSTC-1234_2018-02-10.pdf

    {
        "pattern": "(5\\d{3})-XXXX-XXXX-(\\d{4})_(\\d{8}).pdf",
        "date_index": 2,
        "date_format": "%d%m%Y",
        "output_format": "CC-MSTC-\\1_\\d.pdf",
        "password": "mypdfpawd"
    }

- pattern: In this example the *pattern* defines a regular expression with 3 groups (enclosed between parenthesis):
    * first group: start with '5' followed by 3 digits. It is one of the possible prefix for Mastercard
    * second group: last 4 digit of the credit card
    * third group: this is the date

- date_index: the date to be reformatted is group #2 (counting from 0 ;-) )

- date_format: the original date is formatted as %d%m%Y

- output_format: the new file is renamed, re-using group #1 (\\1) and the new date in ISO format (\\d)

- password: password to be used to decrypt files matching this profiles. Password provided on command line has priority over this

Some sample profiles are provided in the profiles directory
