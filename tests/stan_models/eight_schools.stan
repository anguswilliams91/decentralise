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