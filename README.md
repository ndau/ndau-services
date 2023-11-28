# ndau-services

Utility scripts used by authoritative services to update information on the ndau blockchain:
* vwma.py - Query exchanges supporting ndau to post a 24-hour volume-weighted moving average price via a `RecordPrice` transaction.
* nnr-drand.sh - Post a `NominateNodeReward` transaction using a 64-bit random number from the [DRAND](https://drand.org) network.
