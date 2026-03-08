## Spine-leaf Architecture
![PHOTO-2026-02-24-18-08-51](https://github.com/user-attachments/assets/402c0c4b-2bd9-426b-913b-09ea9cbb658d)


 git clone https://github.com/Sudo-BrainBug/sdn-cat
 
### Start Ryu Controller Ubuntu terminal 1
```bash
cd ~/sdn-work
source ryu_env/bin/activate
ryu-manager sdn_lb_controller.py --ofp-tcp-listen-port 6633
```


### Run MiniNet Ubuntu terminal 2
```bash
sudo mn --custom leaf_spine_topo.py --topo leafspine --controller=remote,ip=127.0.0.1,port=6633 --link tc
```
### Check Network Works (Run this command in terminal)
```bash
curl http://localhost:8080/stats/switches
```
#### It should show : [1, 2, 3, 4, 5]

h4 iperf -s -u &
h1 iperf -c 10.0.0.4 -u -b 8M -t 50
