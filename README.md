# diffscan

Executes scan of IP ranges using templated configurations in /configs. Results are saved in /history. New scans are reported to Slack directly. Repetitive scans report differences comparing to previous scan only.
  
1)Rename ./vault/vault.py-sample to ./vault/vault.py

2)Run as root/sudo. `sudo python3 diffscan.py`
