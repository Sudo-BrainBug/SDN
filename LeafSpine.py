# custom_leafspine.py — run with: sudo mn --custom custom_leafspine.py --topo leafspine --mac --controller remote

from mininet.topo import Topo
from mininet.link import TCLink

class LeafSpineTopo(Topo):
    def build(self):
        # --- 1. SPINES (The Backbone) ---
        s1 = self.addSwitch('s1', dpid='0000000000000001')
        s2 = self.addSwitch('s2', dpid='0000000000000002')
        s3 = self.addSwitch('s3', dpid='0000000000000003')

        # --- 2. LEAVES (The Racks) ---
        # Using 'l' naming for both variables and switch names
        l1 = self.addSwitch('l1', dpid='0000000000000004') 
        l2 = self.addSwitch('l2', dpid='0000000000000005') 

        # --- 3. HOSTS ---
        h1 = self.addHost('h1', mac='00:00:00:00:00:01', ip='10.0.0.1/24')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02', ip='10.0.0.2/24')
        h3 = self.addHost('h3', mac='00:00:00:00:00:03', ip='10.0.0.3/24')
        h4 = self.addHost('h4', mac='00:00:00:00:00:04', ip='10.0.0.4/24')
        h5 = self.addHost('h5', mac='00:00:00:00:00:05', ip='10.0.0.5/24')
        h6 = self.addHost('h6', mac='00:00:00:00:00:06', ip='10.0.0.6/24')

        # --- 4. CORE LINKS (Leaf ↔ Spine Mesh) ---
        # Links from Leaf 1 (l1) to all Spines
        self.addLink(l1, s1, bw=10, cls=TCLink) # Port 1
        self.addLink(l1, s2, bw=10, cls=TCLink) # Port 2
        self.addLink(l1, s3, bw=10, cls=TCLink) # Port 3

        # Links from Leaf 2 (l2) to all Spines
        self.addLink(l2, s1, bw=10, cls=TCLink) # Port 1
        self.addLink(l2, s2, bw=10, cls=TCLink) # Port 2
        self.addLink(l2, s3, bw=10, cls=TCLink) # Port 3

        # --- 5. ACCESS LINKS (Host ↔ Leaf) ---
        # Connections to Leaf 1 (l1)
        self.addLink(h1, l1, bw=100, cls=TCLink) # Port 4
        self.addLink(h2, l1, bw=100, cls=TCLink) # Port 5
        self.addLink(h3, l1, bw=100, cls=TCLink) # Port 6

        # Connections to Leaf 2 (l2)
        self.addLink(h4, l2, bw=100, cls=TCLink) # Port 4
        self.addLink(h5, l2, bw=100, cls=TCLink) # Port 5
        self.addLink(h6, l2, bw=100, cls=TCLink) # Port 6

topos = {'leafspine': LeafSpineTopo}
