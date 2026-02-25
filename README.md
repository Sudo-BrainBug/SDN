### Start Ryu Controller Ubuntu terminal 1
```bash
cd ~/sdn-work
source ryu_env/bin/activate
ryu-manager leaf_spine_controller.py --observe-links
```

### Run MiniNet Ubuntu terminal 2
```bash
sudo mn --custom ~/sdn-work/LeafSpine.py \
        --topo leafspine \
        --mac \
        --switch ovsk,protocols=OpenFlow13 \
        --controller remote,ip=127.0.0.1,port=6633
```
### Check Network Works Device Terminal
```bash
curl http://localhost:8080/stats/switches
```
#### It should show : [1, 2, 3, 4, 5]
