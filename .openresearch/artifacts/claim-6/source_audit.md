# Source audit

The exact source is arXiv `2606.03600v1`, archive SHA-256
`f5124c39036b9107b01439fdbeb5da82331a70b81a3211e3b36887e08109a2db`,
`main.tex` SHA-256
`49058ff8e986f43770936c09cc97360e5cace8802c6304a80d9e153d342ae857`.
Section 5 provides the CA and CCP empirical tables. The released implementation
is pinned at `Nabil-Ala/P2E_calibration@66cb1e1c76d1b1d3d133fe6cb3896c95d48b5974`.
The source audit explicitly reconstructs the paper-defined linear F3
calibrator because the released driver fills its table position with a power
calibrator.
