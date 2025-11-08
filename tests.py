import unittest
import importlib
import iot


class TestIoT(unittest.TestCase):
   
    def setUp(self):
        importlib.reload(iot)
        self.api = iot.api

    # helper methods
    def _get_node(self, uuid):
        node = self.api.api_get_node_by_uuid(uuid)
        self.assertIsNotNone(node, f"Node {uuid} not found")
        return node

    def _get_ep(self, serial):
        ep = self.api.api_get_endpoint_by_serial(serial)
        self.assertIsNotNone(ep, f"Endpoint {serial} not found")
        return ep

    def _post_ota(self, channel, artifact):
        status = self.api.api_post_version_to_ota_channel(channel, artifact)
        self.assertEqual(status, 200, f"Posting artifact '{artifact}' to '{channel}' failed")
        return status

    def _update_ep(self, serial, artifact):
        return self.api.update_endpoint(serial, artifact)

    # tests
    def test_ota_happy_flow(self):
        node_uuid = "Moxa_TBCDB1045001"
        node = self._get_node(node_uuid)
        self.assertEqual(node["version"], "33", "Initial node version should be 33")

        self._post_ota(node["ota_channel"], "moxa_34.swu")

        updated = self.api.trigger_update(node_uuid)
        self.assertTrue(updated, "Expected node update to succeed")

        node = self._get_node(node_uuid)
        self.assertEqual(node["version"], "34", "Node version should be 34 after OTA")

        print("\n -OTA Happy Flow: Node updated successfully from v33 to v34")

    def test_endpoint_dfu_with_backlog(self):
        ep_serial = "Moxa_EP1_001"

        self.api.set_backlog(ep_serial, 50)
        updated = self._update_ep(ep_serial, "ep1_15.swu")
        self.assertFalse(updated, "EP should not update while backlog > 0")

        ep = self._get_ep(ep_serial)
        self.assertEqual(ep["version"], "10", "EP version must remain 10 after deferred update")

        self.api.set_backlog(ep_serial, 0)
        updated = self._update_ep(ep_serial, "ep1_15.swu")
        self.assertTrue(updated, "EP should update after backlog cleared")

        ep = self._get_ep(ep_serial)
        self.assertEqual(ep["version"], "15", "EP version should be 15 after successful update")

        ep2_serial = "Cassia_EP2_001"
        self.api.set_battery(ep2_serial, 2000)
        self.api.set_backlog(ep2_serial, 0)
        updated = self._update_ep(ep2_serial, "ep2_12.swu")
        self.assertFalse(updated, "EP2 should not update when battery is below threshold")

        print("\n -Endpoint DFU With Backlog: Logic verified for backlog and battery threshold")

    def test_bad_firmware_ota(self):
        node_uuid = "Cassia_XYZ789"
        node = self._get_node(node_uuid)
        self.assertEqual(node["version"], "33", "Initial node version should be 33")

        self._post_ota(node["ota_channel"], "moxa_40.swu")

        updated = self.api.trigger_update(node_uuid)
        self.assertFalse(updated, "Update should be rejected due to HW mismatch")

        node = self._get_node(node_uuid)
        self.assertEqual(node["version"], "33", "Node version must remain 33 after rejected update")

        print("\n -Bad Firmware OTA: Hardware mismatch correctly rejected")


if __name__ == "__main__":
    unittest.main(verbosity=2)