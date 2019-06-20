#! /usr/bin/env python
# Script to copy modified xdce files and put them in the relevant directory
# Also includes the replacement of the Images number attribute to match
# the number of elements in the xdce

import argparse
import glob
import logging
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument(
    'study_path', type=str,
    default='/uod/idr/filesets/idr0061-wolf-spindlepositioning',
    help='Path of the study filesets')
parser.add_argument(
    '--overwrite', action='store_true',
    help='Whether to overwrite existing files')
parser.add_argument(
    '--dry-run', action='store_true',
    help='Whether to run the script in dry-run mode')
parser.add_argument('--verbose', '-v', action='count', default=0)
args = parser.parse_args()

logging.basicConfig(level=logging.WARN - 10 * args.verbose)

# Read mapping for new files
with open("%s/20190529-ftp/readme.txt" % args.study_path, 'r') as f:
    logging.info("Reading %s" % f)
    lines = f.readlines()[3:]
    xdce_map = {}
    for line in lines:
        (xdce_filename, directory) = line.split('\t')
        xdce_path = "%s/20190403-ftp/%s" % (
                    args.study_path, directory.replace('\\', '/').rstrip())
        assert os.path.exists(xdce_path), 'Cannot find %s' % xdce_path
        xdce_map[xdce_filename] = xdce_path

# Corrected metadata xdce files were resubmitted in two uploads
# BSF013076.xdce was still invalid (1 field of view instead of 2) in the first
# upload
xdce_files_1 = glob.glob("%s/20190529-ftp/*.xdce" % args.study_path)
xdce_files_1 = [x for x in xdce_files_1 if not x.endswith('BSF013076.xdce')]
xdce_files_2 = glob.glob("%s/20190619-ftp/*.xdce" % args.study_path)
xdce_files = xdce_files_1 + xdce_files_2

for infile in xdce_files:
    xdce_filename = os.path.basename(infile)
    assert xdce_filename in xdce_map.keys()

    logging.info("Reading %s" % infile)
    with open(infile, 'r') as fin:
        # Compute the number of images in the fileset using the Image element
        # as the ground truth
        images_count = len(
            [l for l in fin.readlines() if l.lstrip().startswith('<Image ')])
        logging.debug("Found %g images" % images_count)

    outfile = "%s/%s" % (xdce_map[xdce_filename], xdce_filename)

    logging.info("Writing %s" % outfile)
    if args.dry_run:
        continue
    if os.path.exists(outfile) and not args.overwrite:
        raise Exception("Cannot overwrite %s" % outfile)
    with open(infile, 'r') as fin:
        with open(outfile, 'w') as fout:
            for line in fin:
                if not line.lstrip().startswith('<Images '):
                    fout.write(line)
                    continue
                # Update the Images number
                new_line = re.sub(
                    r'number=\"\d+\"', 'number=\"%s\"' % images_count, line)
                fout.write(new_line)
