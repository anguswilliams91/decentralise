data {
  int<lower=1> nteam;
  int<lower=1> nmatch;
  int home_team[nmatch];
  int away_team[nmatch];
  int home_goals[nmatch];
  int away_goals[nmatch];
}
parameters {
  vector<lower=0>[nteam] a;
  vector<lower=0>[nteam] b;
  real<lower=0> gamma;
  real<lower=0> sigma_a;
  real<lower=0> sigma_b;
  real mu_b;
}
transformed parameters {
  vector[nmatch] home_rate = a[home_team] .* b[away_team] * gamma;
  vector[nmatch] away_rate = a[away_team] .* b[home_team];
}
model {
  gamma ~ lognormal(0, 1);
  sigma_a ~ normal(0, 1);
  sigma_b ~ normal(0, 1);
  mu_b ~ normal(0, 1);
  a ~ normal(0, sigma_a);
  b ~ normal(mu_b, sigma_b);
  home_goals ~ poisson(home_rate);
  away_goals ~ poisson(away_rate);
}
