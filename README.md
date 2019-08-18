# decentralise
[![Build Status](https://travis-ci.org/anguswilliams91/decentralise.svg?branch=master)](https://travis-ci.org/anguswilliams91/decentralise)
[![codecov](https://codecov.io/gh/anguswilliams91/decentralise/branch/master/graph/badge.svg)](https://codecov.io/gh/anguswilliams91/decentralise)



Make (some) Stan programs non-centered automatically.

Inspired by reading [this paper](https://arxiv.org/abs/1906.03028).

## Installation

Requires python 3.6+.
Install with `pip`:

```bash
pip install decentralise
```

## Example

This package provides a command line tool: `decentralise`, which is used as follows:

```bash
decentralise <input-file> <output-destination>
```

It will take any normally distributed parameters that have variances that are themselves parameters, and reparameterise them to make them non-centered.
For example, the canonical eight schools code is:

```
data {
  int<lower=0> J; // number of schools
  vector[J] y; // estimated treatment effects
  vector<lower=0>[J] sigma; // s.e. of effect estimates
}
parameters {
  real mu;
  real<lower=0> tau;
  vector[J] theta;
}
model {
  theta ~ normal(mu, tau);
  y ~ normal(theta, sigma);
}
```

Once `decentralise` is applied, this program becomes

```
data {
  int<lower=0> J; // number of schools
  vector[J] y; // estimated treatment effects
  vector<lower=0>[J] sigma; // s.e. of effect estimates
}
parameters {
  real mu;
  real<lower=0> tau;
  vector[J] theta_std;
}
transformed parameters {
  vector[J] theta = mu + theta_std * tau;
}
model {
  theta_std ~ normal(0, 1);
  y ~ normal(theta, sigma);
}
```

I wrote this tool for fun, and have not thoroughly tested it.
For example, it will fail for any parameters whose sampling statements are not vectorised.
e.g.:
```
x ~ normal(mu, tau);
```
will work, but 
```
for i in (1:n) {
    x[i] ~ normal(mu, tau);
}
```
will not.
There are probably a ton of other cases where it will break that I have not anticipated, as well!
