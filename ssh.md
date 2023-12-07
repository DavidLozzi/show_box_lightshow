## Some basic SSH commands for my reference when connecting to my pi

`sudo reboot`

**copy from local to pi**

`scp -r [folder-to-copy] [username]@[raspberry-pi-ip]:[destination-folder]`

**running services**

Run this python api `python -m uvicorn main:app --host 0.0.0.0 > output.log 2>&1 &`

Use `tail output.log` to monitor log.

Run `ps -ef | grep <svc name>` to view running processes

Run `kill 1234` to kill a process
