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
  y ~ lognormal(theta, sigma);
}