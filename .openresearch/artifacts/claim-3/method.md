# Method

For

```text
A = 1 + exp(C(alpha-s))
F(p) = A / (alpha * (1 + exp(C(p-s))))
```

the verifier reconstructs:

```text
F'(p) = -C*A*exp(C(p-s)) / (alpha*(1+exp(C(p-s)))^2) < 0
F^-1(e) = s + log(A/(alpha*e)-1)/C
```

All factors establish smoothness, strict monotonicity, invertibility, and
positivity analytically. Exact expectation and inverse round trips are checked
in stable log space across 18 theorem-domain `(n,alpha)` cells, up to `n=200`.
The maximum permitted errors are `1e-11` for expectation and `1e-10` for the
inverse.

The direct aggregation comparison uses the full released CCP protocol:
11,700 raw rows, three datasets, three regressors, and 100 seeds per
dataset-model-method cell. P2E is compared directly to `ECCP(ind)`, the
released AoN implementation, in all nine dataset-model cells.

Controls set `C=0` (not decreasing/invertible), `C<0` (increasing), and scale
an exact calibrator by 0.99 (breaks exactness and AoN equality at alpha).
