import argparse
import os
import json

from numpy import genfromtxt

# TODO - Needs a generalization / rewrite / cleanup

parser = argparse.ArgumentParser()

parser.add_argument('--dakota_input',     required=True,
                                          help="Dakota input file")

parser.add_argument('--dakota_output',    required=True,
                                          help="Dakota output file")

parser.add_argument('--acme_output_dir',  required=True,
                                          help="ACME output directory")

args = parser.parse_args()

acme_eval = genfromtxt(os.path.join(args.acme_output_dir, "acme_eval.csv"), delimiter=',')

with open(os.path.join(args.acme_output_dir, "processing_metadata.json")) as json_file:
    runtime_metrics = json.load(json_file)

with open(args.dakota_input) as file:
    input_lines = [line.rstrip() for line in file]
    metrics = [i for i in input_lines if "ASV_" in i]
    metrics = [i.split(":")[1] for i in metrics]

with open(args.dakota_output, "w") as file:
    for metric in metrics:

        if metric == "Minimize_OSIA_RAM":
            file.write(f"{runtime_metrics['ram_max']} Minimize_OSIA_RAM\n")

        if metric == "Minimize_Runtime":
            file.write(f"{runtime_metrics['runtime']} Minimize_Runtime\n")

        if metric == "Minimize_Data_Volume":
            file.write(f"{runtime_metrics['data_volume']} Minimize_Data_Volume\n")

        if metric == "Maximize_Precision":
            file.write(f"{acme_eval[1,1]} Maximize_Precision\n")

        if metric == "Maximize_Recall":
            file.write(f"{acme_eval[1,2]} Maximize_Recall\n")
            
        if metric == "Maximize_F1_Score":
            file.write(f"{acme_eval[1,3]} Maximize_F1_Score\n")

        if metric == "Minimize_False_Positives":
            file.write(f"{acme_eval[1,4]} Minimize_False_Positives\n")