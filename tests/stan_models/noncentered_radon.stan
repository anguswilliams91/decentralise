data {
  int<lower=1> N;
  int<lower=1> J; # number of counties
  int<lower=1,upper=J> county[N];
  vector[N] y;
}
parameters {
  vector[J] a_std;
  real mu_a;
  real<lower=0> sigma_a;
  real<lower=0> sigma_y;
}
transformed parameters {
  vector[J] a = mu_a + a_std * sigma_a;
}
model {
  vector[N] y_hat;
  for (i in 1:N)
    y_hat[i] = a[county[i]];

  mu_a ~ normal(0, 1);
  sigma_a ~ cauchy(0, 2.5);
  sigma_y ~ cauchy(0, 2.5);
  a_std ~ normal(0, 1);
  y ~ normal(y_hat, sigma_y);
}
