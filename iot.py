class Node:
    def __init__(self, hw_type, serial):
        self.hw_type = hw_type
        self.uuid = f"{hw_type}_{serial}"
        self.version = "33"
        self.endpoints = []
        self.ota_channel = f"OTA_{self.uuid}"
        
    def update(self, artifact):
        # make sure it's the right hardware type
        if not artifact.lower().startswith(self.hw_type.lower()):
            print(f"ERROR: mismatch for {self.uuid}")
            return False
        
        # extract version number from artifact name
        self.version = artifact.split('_')[1].replace('.swu', '')
        print(f"{self.uuid} updated to {self.version}")
        return True


class Endpoint:
    def __init__(self, hw_type, serial, battery):
        self.hw_type = hw_type
        self.serial_number = serial
        self.battery = battery
        self.version = "10"
        self.backlog = 0
        self.uuid = None
        # different battery thresholds for different types
        self.threshold = 3600 if hw_type == "Canary" else 2500
        
    def update(self, artifact):
        # check backlog first
        if self.backlog > 0:
            print(f"{self.serial_number} deferred: backlog={self.backlog}")
            return False
        
        # then check battery
        if self.battery < self.threshold:
            print(f"{self.serial_number} deferred: battery={self.battery}")
            return False
        
        # make sure hardware type matches
        if not artifact.lower().startswith(self.hw_type.lower()):
            print(f"ERROR: mismatch for {self.serial_number}")
            return False
        
        self.version = artifact.split('_')[1].replace('.swu', '')
        print(f"{self.serial_number} updated to {self.version}")
        return True


class IoTAPI:
    def __init__(self):
        self.nodes = {}
        self.endpoints = {}
        self.ota_channels = {}
        self.setup_environment()
        
    def setup_environment(self):
        # create the 3 nodes
        node_configs = [
            ("AHN2", "ABC123"),
            ("Cassia", "XYZ789"),
            ("Moxa", "TBCDB1045001")
        ]
        
        for hw_type, serial in node_configs:
            node = Node(hw_type, serial)
            self.nodes[node.uuid] = node
            
            # each node gets 3 endpoints
            ep_configs = [
                ("EP1", f"{hw_type}_EP1_001", 3000),
                ("EP2", f"{hw_type}_EP2_001", 3000),
                ("Canary", f"{hw_type}_Canary_001", 4000)
            ]
            
            for ep_type, ep_serial, battery in ep_configs:
                ep = Endpoint(ep_type, ep_serial, battery)
                ep.uuid = node.uuid
                node.endpoints.append(ep)
                self.endpoints[ep_serial] = ep
    
    def api_get_endpoint_by_serial(self, serial_number: str) -> dict:
        if serial_number not in self.endpoints:
            return None
        
        e = self.endpoints[serial_number]
        return {
            "serial_number": e.serial_number,
            "battery": e.battery,
            "hardware_type": e.hw_type,
            "uuid": e.uuid,
            "version": e.version
        }
    
    def api_get_node_by_uuid(self, uuid: str) -> dict:
        if uuid not in self.nodes:
            return None
        
        n = self.nodes[uuid]
        return {
            "uuid": n.uuid,
            "ota_channel": n.ota_channel,
            "version": n.version,
            "Endpoints": n.endpoints
        }
    
    def api_post_version_to_ota_channel(self, ota_channel: str, version_artifact: str) -> int:
        # Adds new version to channel
        self.ota_channels[ota_channel] = version_artifact
        return 200  # success
    
    def api_clear_ota_channel(self, ota_channel: str, version_artifact: str) -> int:
        # Clear an artifact from the OTA channel
        if ota_channel in self.ota_channels and self.ota_channels[ota_channel] == version_artifact:
            del self.ota_channels[ota_channel]
            return 200  # success
        return 400  # fail
    
    def trigger_update(self, uuid):
        if uuid not in self.nodes:
            return False
        
        node = self.nodes[uuid]
        if node.ota_channel in self.ota_channels:
            return node.update(self.ota_channels[node.ota_channel])
        return False
    
    def update_endpoint(self, serial, artifact):
        if serial not in self.endpoints:
            return False
        return self.endpoints[serial].update(artifact)
    
    def set_backlog(self, serial, value):
        if serial in self.endpoints:
            self.endpoints[serial].backlog = value
    
    def set_battery(self, serial, value):
        if serial in self.endpoints:
            self.endpoints[serial].battery = value

 
 
api = IoTAPI()
