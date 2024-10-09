import argparse
import os
import json
import numpy as np

from numpy import genfromtxt

parser = argparse.ArgumentParser()

parser.add_argument('--dakota_input',     required=True,
                                          help="Dakota input file")

parser.add_argument('--dakota_output',    required=True,
                                          help="Dakota output file")

parser.add_argument('--aegis_output_dir',  required=True,
                                          help="AEGIS output directory")

args = parser.parse_args()

aegis_eval = genfromtxt(os.path.join(args.aegis_output_dir, "aegis_eval.csv"), delimiter=',')

with open(args.dakota_input) as file:
    input_lines = [line.rstrip() for line in file]
    metrics = [i for i in input_lines if "ASV_" in i]
    metrics = [i.split(":")[1] for i in metrics]

with open(args.dakota_output, "w") as file:
    for metric in metrics:
        if metric == 'Maximize_Intersection_over_Union':
            ious = aegis_eval[1:, 1]
            mean_iou = np.mean(ious)
            file.write(f"{mean_iou} Maximize_Intersection_over_Union\n")

        if metric == 'Minimize_Runtime':
            runtimes = aegis_eval[1:, 2]
            mean_runtimes = np.mean(runtimes)
            file.write(f"{mean_runtimes} Minimize_Runtime\n")