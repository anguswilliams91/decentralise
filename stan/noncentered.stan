data {
    int n;
    vector[n] y;
    vector<lower=0> sigma;
}
parameters {
    vector theta_t;
    real mu;
    real<lower=0> tau;
}
transformed parameters {
    vector theta = theta_t * tau + mu;
}
model {
    y ~ normal(theta, sigma);
    theta_t ~ normal(0, 1);
}