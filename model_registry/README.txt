This directory serves as the artifact store for versioned machine learning models.
Standard MLOps practice dictates separating code (git) from large model binaries (DVC/Artifactory).

Recommended Structure:
- v1.0.0/policy.pt
- v1.0.0/critic.pt
- latest -> v1.0.0

Ensure `.gitignore` is configured to exclude large binaries if not using LFS.
