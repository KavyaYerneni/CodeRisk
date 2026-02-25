# Evaluation splits

For realistic PR risk evaluation prefer **repository-time**:

1. Hold out entire repositories for the test set.
2. Within training repositories, take the latest time slice as validation.

This reduces leakage from repeated files/authors within a repo and from future commits informing earlier scores. Random stratified splits are available for debugging only.
