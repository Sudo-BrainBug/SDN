## Spine-leaf Architecture
![PHOTO-2026-02-24-18-08-51](https://github.com/user-attachments/assets/402c0c4b-2bd9-426b-913b-09ea9cbb658d)

### Start Ryu Controller Ubuntu terminal 1
```bash
cd ~/sdn-work
source ryu_env/bin/activate
 ryu-manager --wsapi-host 0.0.0.0 leaf_spine_controller.py ryu.app.ofctl_rest
```


### Run MiniNet Ubuntu terminal 2
```bash
sudo mn --custom ~/sdn-work/LeafSpine.py \
        --topo leafspine \
        --mac \
        --switch ovsk,protocols=OpenFlow13 \
        --controller remote,ip=127.0.0.1,port=6633
```
### Check Network Works (Run this command in terminal)
```bash
curl http://localhost:8080/stats/switches
```
#### It should show : [1, 2, 3, 4, 5]
