data {
  int<lower=1> nteam;
  int<lower=1> nmatch;
  int home_team[nmatch];
  int away_team[nmatch];
  int home_goals[nmatch];
  int away_goals[nmatch];
}
parameters {
  vector<lower=0>[nteam] a_std;
  vector<lower=0>[nteam] b_std;
  real<lower=0> gamma;
  real<lower=0> sigma_a;
  real<lower=0> sigma_b;
  real mu_b;
}
transformed parameters {
  vector<lower=0>[nteam] a = 0 + a_std * sigma_a;
  vector<lower=0>[nteam] b = mu_b + b_std * sigma_b;
  vector[nmatch] home_rate = a[home_team] .* b[away_team] * gamma;
  vector[nmatch] away_rate = a[away_team] .* b[home_team];
}
model {
  gamma ~ lognormal(0, 1);
  sigma_a ~ normal(0, 1);
  sigma_b ~ normal(0, 1);
  mu_b ~ normal(0, 1);
  a_std ~ normal(0, 1);
  b_std ~ normal(0, 1);
  home_goals ~ poisson(home_rate);
  away_goals ~ poisson(away_rate);
}
