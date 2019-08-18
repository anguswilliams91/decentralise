data {
  int<lower=0> N; 
  int<lower=0> n_age;
  int<lower=0> n_age_edu;  
  int<lower=0> n_edu; 
  int<lower=0> n_region_full; 
  int<lower=0> n_state; 
  int<lower=0,upper=n_age> age[N];
  int<lower=0,upper=n_age_edu> age_edu[N];
  vector<lower=0,upper=1>[N] black;
  int<lower=0,upper=n_edu> edu[N];
  vector<lower=0,upper=1>[N] female;
  int<lower=0,upper=n_region_full> region_full[N];
  int<lower=0,upper=n_state> state[N];
  vector[N] v_prev_full;
  int<lower=0,upper=1> y[N];
} 
parameters {
  vector[n_age] a_std;
  vector[n_edu] b_std;
  vector[n_age_edu] c_std;
  vector[n_state] d_std;
  vector[n_region_full] e_std;
  vector[5] beta;
  real<lower=0,upper=100> sigma_a;
  real<lower=0,upper=100> sigma_b;
  real<lower=0,upper=100> sigma_c;
  real<lower=0,upper=100> sigma_d;
  real<lower=0,upper=100> sigma_e;
}
transformed parameters {
  vector[n_age] a = 0 + a_std * sigma_a;
  vector[n_edu] b = 0 + b_std * sigma_b;
  vector[n_age_edu] c = 0 + c_std * sigma_c;
  vector[n_state] d = 0 + d_std * sigma_d;
  vector[n_region_full] e = 0 + e_std * sigma_e;
  vector[N] y_hat;

  for (i in 1:N)
    y_hat[i] = beta[1] + beta[2] * black[i] + beta[3] * female[i]
                + beta[5] * female[i] * black[i] 
                + beta[4] * v_prev_full[i] + a[age[i]] + b[edu[i]] 
                + c[age_edu[i]] + d[state[i]] + e[region_full[i]];
} 
model {
  a_std ~ normal(0, 1);
  b_std ~ normal(0, 1);
  c_std ~ normal(0, 1);
  d_std ~ normal(0, 1);
  e_std ~ normal(0, 1);
  beta ~ normal(0, 100);
  y ~ bernoulli_logit(y_hat);
}
