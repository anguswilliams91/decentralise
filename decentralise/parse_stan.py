from argparse import ArgumentParser
import re


def strip_comment(line):
    return line.split(";")[0]


def get_parameter_names_and_types(stan_code):
    # find the names of parameters in a stan program
    param_block = re.search(r"parameters\s+{([\S\s]*?)\}", stan_code).groups()[0]
    return {
        strip_comment(line)
        .strip()
        .split()[-1]
        .strip(): strip_comment(line)
        .strip()
        .split()[0]
        .strip()
        for line in param_block.splitlines()[1:]
    }


def get_parameter_dists(parameter_names, stan_code):
    # find the distribution of parameters in a stan program
    model_block = re.search(r"model\s+{([\S\s]*?)\}", stan_code).groups()[0]
    param_to_dist = {}
    for line in model_block.splitlines()[1:]:
        if re.search(r"[^.;~]+~.*;", line):
            param, dist = line.strip().split("~")
            param = param.strip()
            dist = dist.strip(";").strip()
            if param in parameter_names:
                param_to_dist[param] = dist
    return param_to_dist


def is_normal(dist):
    return (
        ("normal" in dist)
        and ("lognormal" not in dist)
        and ("multi_normal" not in dist)
    )


def get_mu_sigma(dist):
    mu, sigma = re.search(r"normal\s*\((.+)\,\s+(.+)\)", dist).groups()
    return mu, sigma


def modify_transformed_parameters_block(name_to_type, param_to_dist, stan_code):
    # create a new transformed parameters block
    try:
        transformed_param_block = re.search(
            r"(transformed parameters\s+{[\S\s]*?\})", stan_code
        ).groups()[0]
    except AttributeError:
        transformed_param_block = None
        final_string = "\n}\n"

    transformed_params_lines = []
    for param_name, dist in param_to_dist.items():
        mu, sigma = get_mu_sigma(dist)
        transformed_param_line = (
            "  "
            + name_to_type[param_name]
            + " "
            + param_name
            + " = "
            + mu
            + " + "
            + param_name
            + "_std * "
            + sigma
            + ";"
        )
        transformed_params_lines.append(transformed_param_line)

    if transformed_param_block is None:
        return (
            "transformed parameters {\n"
            + "\n".join(transformed_params_lines)
            + final_string
        )
    else:
        original_lines = transformed_param_block.splitlines()
        new_lines = (
            [original_lines[0]]
            + transformed_params_lines
            + original_lines[1:-1]
            + ["}"]
        )
        return "\n".join(new_lines)


def modify_parameters_block(name_to_type, norm_params, stan_code):
    param_block = re.search(
        r"(?<!transformed )(parameters\s+{[\S\s]*?\})", stan_code
    ).groups()[0]

    new_lines = []
    for line in param_block.splitlines():
        found_param = False
        for param_name, param_type in {
            k: v for k, v in name_to_type.items() if k in norm_params.keys()
        }.items():
            if (param_type + " " + param_name + ";") in line:
                new_lines.append("  " + param_type + " " + param_name + "_std;")
                found_param = True
        if not found_param:
            new_lines.append(line)

    return "\n".join(new_lines)


def modify_model_block(norm_params, param_to_dist, stan_code):
    model_block = re.search(r"(model\s+{[\S\s]*?\})", stan_code).groups()[0]
    new_lines = []
    for line in model_block.splitlines():
        found_param = False
        for param, dist in norm_params.items():
            if (param + " ~ " + dist) in line:
                non_cent_line = "  " + param + "_std ~ normal(0, 1);"
                new_lines.append(non_cent_line)
                found_param = True
        if not found_param:
            new_lines.append(line)
    return "\n".join(new_lines)


def make_non_centered(stan_code: str) -> str:
    """Convert a stan program to non-centered.

    Convert all normally distributed parameters in a stan program into a 
    non-centered parameterisation and return the new stan program as a string.
    
    Args:
        stan_code: the original stan program.
    
    Returns:
        the new stan program.
    """
    name_to_type = get_parameter_names_and_types(stan_code)
    param_to_dist = get_parameter_dists(name_to_type.keys(), stan_code)
    norm_params = {
        param_name: dist
        for param_name, dist in param_to_dist.items()
        if (is_normal(dist) and (get_mu_sigma(dist)[1] in name_to_type.keys()))
    }

    transformed_params_block = modify_transformed_parameters_block(
        name_to_type, norm_params, stan_code
    )
    param_block = modify_parameters_block(name_to_type, norm_params, stan_code)
    model_block = modify_model_block(norm_params, param_to_dist, stan_code)

    if re.search(r"(transformed parameters\s+{[\S\s]*?\})", stan_code) is None:
        new_stan_code = re.sub(
            r"model\s+{([\S\s]*?)\}", transformed_params_block + model_block, stan_code
        )
    else:
        new_stan_code = re.sub(r"model\s+{([\S\s]*?)\}", model_block, stan_code)
        new_stan_code = re.sub(
            r"(transformed parameters\s+{[\S\s]*?\})",
            transformed_params_block,
            new_stan_code,
        )

    new_stan_code = re.sub(
        r"(?<!transformed )(parameters\s+{[\S\s]*?\})", param_block, new_stan_code
    )

    return new_stan_code


def cli(code_path: str, output_path: str) -> None:
    """
    Automatically use the non-centered parameterisation in Stan programs.
    """
    with open(code_path, "r") as f:
        centered_code = f.read()

    non_centered_code = make_non_centered(centered_code)

    with open(output_path, "w") as f:
        f.write(non_centered_code)


def main():
    parser = ArgumentParser(
        description="Reparameterise normally distributed parameters in a stan program."
    )
    parser.add_argument("input_file", metavar="input_file", help="The input stan code.")
    parser.add_argument(
        "output_file",
        metavar="output_file",
        help="Destination for transformed stan code.",
    )
    args = parser.parse_args()

    cli(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
