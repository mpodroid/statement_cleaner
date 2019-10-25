Introduction
============
A simple and small utility to help managing statements from bank and credit card accounts.

My bank send me statements via email, but there are two issues I am not confortable with:
* filename: it includes statement date, but not in ISO format, so there is no way to sort them
* encryption: PDF files are procted with a password, that I do not want to keep after I opened on my computer

This python utility rename the file to use date in ISO format, so name sorting overlaps with date sorting.
It also remote password protection, using qpdf utility.

Examples
========

Here some examples of filename transformation:

    5432-XXXX-XXXX-1234_10022018.pdf -> 5432-XXXX-XXXX-1234_2018-02-10.pdf
    4567-XXXX-XXXX-5678_10052018.pdf -> 4567-XXXX-XXXX-5678_2018-05-10.pdf
    E-STATEMENT_01 APR 2019_9876.pdf -> E-STATEMENT_2019-04-01_9876.pdf



Getting started
===============

    usage: statement_cleaner [-h] (-f FILE | -i INDIR) [-p PASSWORD] [-o OUTDIR]
    
    Cleanup bank statements PDF files, formatting dates with ISO format and removing encryption
    
    optional arguments:
      -h, --help                           show this help message and exit
      -f FILE, --file FILE                 PDF filename to be cleaned
      -i INDIR, --indir INDIR              Process all PDF files in this directory
      -p PASSWORD, --password PASSWORD     Password to decrypt PDF file, if encrypted
      -o OUTDIR, --outdir OUTDIR           Alternative directory to save files
