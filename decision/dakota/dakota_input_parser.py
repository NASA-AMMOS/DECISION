import argparse

# TODO - Needs a generalization / rewrite / cleanup

parser = argparse.ArgumentParser()

parser.add_argument('--dakota_input',  required=True,
                                       help="")

args = parser.parse_args()

with open(args.dakota_input) as file:
    lines = [line.rstrip() for line in file]

# TODO - this will vary based on dakota config / optimization problem.
#           Should write a more comprehensive Dakota input/output file parser.
variables = lines[1:10]

variables_dict = {}
for variable in variables:
    variables_dict[variable.split()[1]] = variable.split()[0]

# Enforce ACME expectations
if not int(variables_dict['center_x']) % 2 == 1:
    variables_dict['center_x'] = int(variables_dict['center_x']) + 1

if not int(variables_dict['window_x']) % 2 == 1:
    variables_dict['window_x'] = int(variables_dict['window_x']) + 1

if not int(variables_dict['window_y']) % 2 == 1:
    variables_dict['window_y'] = int(variables_dict['window_y']) + 1


with open("OSIA/OWLS-Autonomy/src/cli/configs/dakota_acme_config.yml", "w") as file:
    
    file.write("# Parameter for ACME analyser\n")
    file.write("\n")
    file.write("# Peak Window Definitions\n")
    file.write(f"center_x: {variables_dict['center_x']}  # window width in x to consider peak (should roughly equal max peak width in time) (must be odd) (needs to be less than window_x)\n")
    file.write(f"window_x: {variables_dict['window_x']}  # window width in x to consider peak background (needs to be bigger than center) (must be odd)\n")
    file.write(f"window_y: {variables_dict['window_y']}  # window width in y to consider peak (should rougly corresbond to max peak width in mass)  (must be odd)\n")
    file.write(f"denoise_x: {variables_dict['denoise_x']}  # window width used to median denoise the data prior to any peak detection\n")
    file.write("\n")
    file.write("# Peak Identification Configuration\n")
    sigma = float(variables_dict['sigma'])
    file.write(f'sigma: {sigma:.1f}  # [3 - 6] standard deviation of gausian filter\n')
    sigma_ratio = float(variables_dict['sigma_ratio'])
    file.write(f'sigma_ratio: {sigma_ratio:.1f}  # [2 - 3] ratio of standard deviations for filter\n')
    file.write(f"min_filtered_threshold: {variables_dict['min_filtered_threshold']} # threshold after convolutional filter is applied\n")
    file.write(f"min_SNR_conv: {variables_dict['min_SNR_conv']}  # threshold for filtering found peaks by their SNR after background subtraction and convolution\n")
    file.write("masses_dist_max: 0.5  # maximum difference between mass of known compound and found peak in [amu]\n")
    file.write("\n")
    file.write("# Peak Properties and Filters\n")
    file.write("x_sigmas: 3.0 # number of standard deviations around the peak center to define peak start/stop\n")
    file.write(f"min_peak_volume: {variables_dict['min_peak_volume']}  # minimum volume (Ion counts) of a peak to be detected\n")
    file.write("\n")
    file.write("# SUE and DD Configuration\n")
    file.write("mass_resolution: 1.0      # Resolution to use when calculating number of unique masses (m/z)\n")
    file.write("dd_mass_resolution: 10.0  # Resolution to use when calculating vector of unique masses (m/z)\n")
    file.write("time_resolution: 0.6      # Resolution to use when calculating number of unique times (minutes)\n")
