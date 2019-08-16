"""Just run against a few stan programs and check that the output is as expected."""
from pathlib import Path

import pytest

from decentralise.parse_stan import make_non_centered


@pytest.mark.parametrize(
    "model",
    ["eight_schools", "bpl", "lognormal_eight_schools", "multi_normal_eight_schools"],
)
def test_decentralise(model):
    code_path = Path(__file__).parent / f"stan_models/{model}.stan"
    with open(code_path, "r") as f:
        centered_stan_code = f.read()

    transformed_path = Path(__file__).parent / f"stan_models/noncentered_{model}.stan"
    with open(transformed_path, "r") as f:
        transformed_stan_code = f.read()

    assert make_non_centered(centered_stan_code) == transformed_stan_code
