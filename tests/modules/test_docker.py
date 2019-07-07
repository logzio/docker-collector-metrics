import unittest
import os

from modules.docker.docker import setup, MODULE_NAME


class TestDockerModule(unittest.TestCase):
    def test_exclude_containers(self):
        # [
        #     {
        #         "enabled": true,
        #         "hosts": [
        #             "unix:///var/run/docker.sock"
        #         ],
        #         "metricsets": [
        #             "container",
        #             "cpu",
        #             "diskio",
        #             "healthcheck",
        #             "info",
        #             "memory",
        #             "network"
        #         ],
        #         "module": "docker",
        #         "period": "10s",
        #         "processors": [
        #             {
        #                 "drop_event": {
        #                     "when": {
        #                         "or": [
        #                             {
        #                                 "contains": {
        #                                     "docker.container.name": "container0"
        #                                 }
        #                             },
        #                             {
        #                                 "contains": {
        #                                     "docker.container.name": "container1"
        #                                 }
        #                             },
        #                             {
        #                                 "contains": {
        #                                     "docker.container.name": "container2"
        #                                 }
        #                             }
        #                         ]
        #                     }
        #                 }
        #             }
        #         ]
        #     }
        # ]
        try:
            containers_str = os.environ["dockerSkipContainerName"] = "container0, container1, container2"
            exclude_containers = [container.strip() for container in containers_str.split(",")]

            conf, name = setup()
            exclude_path = conf[0]["processors"][0]["drop_event"]["when"]["or"]
            for x in range(len(exclude_containers)):
                self.assertEqual(exclude_containers[x], exclude_path[x]["contains"]["docker.container.name"])
        finally:
            del os.environ["dockerSkipContainerName"]

    def test_include_containers(self):
        # [
        #     {
        #         "enabled": true,
        #         "hosts": [
        #             "unix:///var/run/docker.sock"
        #         ],
        #         "metricsets": [
        #             "container",
        #             "cpu",
        #             "diskio",
        #             "healthcheck",
        #             "info",
        #             "memory",
        #             "network"
        #         ],
        #         "module": "docker",
        #         "period": "10s",
        #         "processors": [
        #             {
        #                 "drop_event": {
        #                     "when": {
        #                         "and": [
        #                             {
        #                                 "not": {
        #                                     "contains": {
        #                                         "docker.container.name": "container0"
        #                                     }
        #                                 }
        #                             },
        #                             {
        #                                 "not": {
        #                                     "contains": {
        #                                         "docker.container.name": "container1"
        #                                     }
        #                                 }
        #                             },
        #                             {
        #                                 "not": {
        #                                     "contains": {
        #                                         "docker.container.name": "container2"
        #                                     }
        #                                 }
        #                             }
        #                         ]
        #                     }
        #                 }
        #             }
        #         ]
        #     }
        # ]
        try:
            containers_str = os.environ["dockerMatchContainerName"] = "container0, container1, container2"
            include_containers = [container.strip() for container in containers_str.split(",")]

            conf, name = setup()
            include_path = conf[0]["processors"][0]["drop_event"]["when"]["and"]
            for x in range(len(include_containers)):
                self.assertEqual(include_containers[x], include_path[x]["not"]["contains"]["docker.container.name"])
        finally:
            del os.environ["dockerMatchContainerName"]

    def test_include_and_exclude(self):
        try:
            os.environ["dockerMatchContainerName"] = "container0, container1, container2"
            os.environ["dockerSkipContainerName"] = "container0, container1, container2"
            self.assertRaises(KeyError, setup)
        finally:
            del os.environ["dockerMatchContainerName"]
            del os.environ["dockerSkipContainerName"]

    def test_period(self):
        try:
            conf, name = setup()
            self.assertEqual(conf[0]["period"], "10s")

            period = os.environ["dockerPeriod"] = "1s"
            conf, name = setup()
            self.assertEqual(conf[0]["period"], period)
        finally:
            del os.environ["dockerPeriod"]

    def test_certificate(self):
        try:
            conf, name = setup()
            self.assertRaises(KeyError, lambda: conf[0]["ssl"])

            certificate_authority = os.environ["dockerCertificateAuthority"] = "/etc/pki/root/ca.pem"
            certificate = os.environ["dockerCertificate"] = "/etc/pki/client/cert.pem"
            key = os.environ["dockerKey"] = "/etc/pki/client/cert.key"
            conf, name = setup()
            self.assertEqual(conf[0]["ssl"]["certificate_authority"], certificate_authority)
            self.assertEqual(conf[0]["ssl"]["certificate"], certificate)
            self.assertEqual(conf[0]["ssl"]["key"], key)
        finally:
            del os.environ["dockerCertificateAuthority"]
            del os.environ["dockerCertificate"]
            del os.environ["dockerKey"]

    def test_cpu_per_core(self):
        try:
            conf, name = setup()
            self.assertRaises(KeyError, lambda: conf[0]["cpu.cores"])

            os.environ["dockerCPUPerCore"] = "true"
            conf, name = setup()
            self.assertEqual(conf[0]["cpu.cores"], "true")
        finally:
            del os.environ["dockerCPUPerCore"]


if __name__ == '__main__':
    unittest.main()
