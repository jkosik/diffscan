# diffscan

Executes scan of IP ranges using templated configurations in /configs. Results are saved in /history. New scans are reported to Slack directly. Repetitive scans report differences comparing to previous scan only.
  
1) Rename ./vault/vault.py-sample to ./vault/vault.py
2) Place your config `XXX.conf` into `/configs` and a) change output-filename field to `outputs/XXX.out`, b) optionally change target IP range or other params.
3) Define which configs (defined without .conf suffix)  you want to run from the available configs. Set it directly inside diffscan.py: `scan('test')` and `compare('test')`. You can have any amount of configs in `/configs`. Only those defined in diffscan.py are applied.
2) Run as root/sudo. `sudo python3 diffscan.py`
