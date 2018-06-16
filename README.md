# diffscan

Executes scan of IP ranges using templated configurations in /configs. Results are saved in /history. New scans are reported to Slack directly. Repetitive scans report differences comparing to previous scan only.
  
* Rename `./vault/vault.py-sample` to `./vault/vault.py` and set Slack webhook and Slack channel for receiving notifications
* Place your scan config `target1.conf` into `/configs` directory and  
	a) change output-filename field to `outputs/target1/target1.out`,   
	b) optionally change target IP range or other params.
* Scan outputs are stored in `outputs/targetX/` directory
* Scan history for all targets is saved in `history/` directory
* Define which configs (defined without .conf suffix)  you want to run from the available configs. Set it directly inside `diffscan.py` as array field: 
```
targets_to_use = ['target1'] #add configs to be used
```
4) Run as root/sudo. `sudo python3 diffscan.py`
