import re


def get_parameter_names_and_types(stan_code):
    # find the names of parameters in a stan program
    param_block = re.search(r"parameters\s+{([\S\s]*?)\}", stan_code).groups()[0]
    return {
        line.split()[-1].strip(";"): line.split()[0].strip()
        for line in param_block.splitlines()[1:]
    }


def get_parameter_dists(parameter_names, stan_code):
    # find the distribution of parameters in a stan program
    model_block = re.search(r"model\s+{([\S\s]*?)\}", stan_code).groups()[0]
    param_to_dist = {}
    for line in model_block.splitlines()[1:]:
        param, dist = line.strip().split("~")
        param = param.strip()
        dist = dist.strip(";").strip()
        if param in parameter_names:
            param_to_dist[param] = dist
    return param_to_dist


def is_normal(dist):
    return ("normal" in dist) and ("lognormal" not in dist)


def get_mu_sigma(dist):
    mu, sigma = re.search(r"normal\((.+)\,\s+(.+)\)", dist).groups()
    return mu, sigma


def modify_transformed_parameters_block(name_to_type, param_to_dist, stan_code):
    # create a new transformed parameters block
    try:
        transformed_param_block = re.search(
            r"(transformed parameters\s+{[\S\s]*?\})", stan_code
        ).groups()[0]
    except AttributeError:
        transformed_param_block = None

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
            + ";\n"
        )
        transformed_params_lines.append(transformed_param_line)

    if transformed_param_block is None:
        return (
            "transformed parameters {\n" + "\n".join(transformed_params_lines) + "}\n"
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


def modify_parameters_block(param_names, stan_code):
    param_block = re.search(
        r"(?<!transformed )(parameters\s+{[\S\s]*?\})", stan_code
    ).groups()[0]
    for param in param_names:
        param_block = param_block.replace(param, param + "_std")
    return param_block


def modify_model_block(param_names, stan_code):
    model_block = re.search(r"(model\s+{[\S\s]*?\})", stan_code).groups()[0]
    new_lines = []
    for line in model_block.splitlines():
        found_param = False
        for param in param_names:
            if param in line.split("~")[0]:
                non_cent_line = "  " + param + "_std ~ normal(0, 1);"
                new_lines.append(non_cent_line)
                found_param = True
        if not found_param:
            new_lines.append(line)
    return "\n".join(new_lines)


def make_non_centered(stan_code: str) -> str:
    """Convert a stan program to non-centered.

    Convert *any* normally distributed parameter in a stan program into a non-centered parameterisation and return the new 
    stan program as a string.
    
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
        if is_normal(dist)
    }

    transformed_params_block = modify_transformed_parameters_block(
        name_to_type, norm_params, stan_code
    )
    param_block = modify_parameters_block(norm_params.keys(), stan_code)
    model_block = modify_model_block(norm_params.keys(), stan_code)

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
