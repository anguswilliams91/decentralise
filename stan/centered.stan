data {
    int n;
    vector[n] y;
    vector<lower=0> sigma;
}
parameters {
    real theta;
}
model {
    y ~ normal(theta, sigma);
}