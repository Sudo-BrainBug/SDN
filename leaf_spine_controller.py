# leaf_spine_controller.py
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet

class LeafSpineController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(LeafSpineController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        
        # Define the topology mapping
        # Spine switches need to know which leaf connects to which hosts
        self.spine_routes = {
            # For spines: if destination MAC belongs to leaf1 hosts, use port connected to leaf1
            # Spine s1 (dpid=1): leaf1 on port 1, leaf2 on port 2
            1: {
                '00:00:00:00:00:01': 1,  # h1 via leaf1
                '00:00:00:00:00:02': 1,  # h2 via leaf1
                '00:00:00:00:00:03': 1,  # h3 via leaf1
                '00:00:00:00:00:04': 2,  # h4 via leaf2
                '00:00:00:00:00:05': 2,  # h5 via leaf2
                '00:00:00:00:00:06': 2,  # h6 via leaf2
            },
            # Spine s2 (dpid=2): leaf1 on port 1, leaf2 on port 2
            2: {
                '00:00:00:00:00:01': 1,
                '00:00:00:00:00:02': 1,
                '00:00:00:00:00:03': 1,
                '00:00:00:00:00:04': 2,
                '00:00:00:00:00:05': 2,
                '00:00:00:00:00:06': 2,
            },
            # Spine s3 (dpid=3): leaf1 on port 1, leaf2 on port 2
            3: {
                '00:00:00:00:00:01': 1,
                '00:00:00:00:00:02': 1,
                '00:00:00:00:00:03': 1,
                '00:00:00:00:00:04': 2,
                '00:00:00:00:00:05': 2,
                '00:00:00:00:00:06': 2,
            }
        }

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id

        self.logger.info("Switch connected: dpid=%s", dpid)

        # Install table-miss flow entry (send to controller)
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        # Install static flows
        self.install_static_flows(datapath)

    def install_static_flows(self, datapath):
        parser = datapath.ofproto_parser
        dpid = datapath.id

        self.logger.info("Installing flows for switch dpid=%s", dpid)

        # Leaf 1 (dpid=4): hosts on ports 4,5,6; spines on ports 1,2,3
        if dpid == 4:
            # Local hosts (directly connected)
            flows = [
                ('00:00:00:00:00:01', 4),  # h1
                ('00:00:00:00:00:02', 5),  # h2
                ('00:00:00:00:00:03', 6),  # h3
            ]
            for mac, port in flows:
                match = parser.OFPMatch(eth_dst=mac)
                actions = [parser.OFPActionOutput(port)]
                self.add_flow(datapath, 10, match, actions)
            
            # Remote hosts (via spine s1 - port 1)
            for mac in ['00:00:00:00:00:04', '00:00:00:00:00:05', '00:00:00:00:00:06']:
                match = parser.OFPMatch(eth_dst=mac)
                actions = [parser.OFPActionOutput(1)]
                self.add_flow(datapath, 10, match, actions)

        # Leaf 2 (dpid=5): hosts on ports 4,5,6; spines on ports 1,2,3
        elif dpid == 5:
            # Local hosts
            flows = [
                ('00:00:00:00:00:04', 4),  # h4
                ('00:00:00:00:00:05', 5),  # h5
                ('00:00:00:00:00:06', 6),  # h6
            ]
            for mac, port in flows:
                match = parser.OFPMatch(eth_dst=mac)
                actions = [parser.OFPActionOutput(port)]
                self.add_flow(datapath, 10, match, actions)
            
            # Remote hosts (via spine s1 - port 1)
            for mac in ['00:00:00:00:00:01', '00:00:00:00:00:02', '00:00:00:00:00:03']:
                match = parser.OFPMatch(eth_dst=mac)
                actions = [parser.OFPActionOutput(1)]
                self.add_flow(datapath, 10, match, actions)

        # Spine switches (dpid=1,2,3)
        elif dpid in [1, 2, 3]:
            if dpid in self.spine_routes:
                for mac, port in self.spine_routes[dpid].items():
                    match = parser.OFPMatch(eth_dst=mac)
                    actions = [parser.OFPActionOutput(port)]
                    self.add_flow(datapath, 10, match, actions)
                    self.logger.info("Spine %s: %s -> port %s", dpid, mac, port)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        dpid = datapath.id

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        self.logger.info("PacketIn: dpid=%s src=%s dst=%s in_port=%s", dpid, src, dst, in_port)

        # Ignore LLDP packets
        if eth.ethertype == 0x88cc:
            return

        # Learn MAC address to avoid flooding next time
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        # Determine output port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        # Send packet out
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                   in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
