import unittest
import os

from modules.docker.docker import setup


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
            containers_str = os.environ["DOCKER_SKIP_CONTAINER_NAME"] = "container0, container1, container2"
            exclude_containers = [container.strip() for container in containers_str.split(",")]

            conf = setup()
            exclude_path = conf[0]["processors"][0]["drop_event"]["when"]["or"]
            for x in range(len(exclude_containers)):
                self.assertEqual(exclude_containers[x], exclude_path[x]["contains"]["docker.container.name"])
        finally:
            del os.environ["DOCKER_SKIP_CONTAINER_NAME"]

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
            containers_str = os.environ["DOCKER_MATCH_CONTAINER_NAME"] = "container0, container1, container2"
            include_containers = [container.strip() for container in containers_str.split(",")]

            conf = setup()
            include_path = conf[0]["processors"][0]["drop_event"]["when"]["and"]
            for x in range(len(include_containers)):
                self.assertEqual(include_containers[x], include_path[x]["not"]["contains"]["docker.container.name"])
        finally:
            del os.environ["DOCKER_MATCH_CONTAINER_NAME"]

    def test_include_and_exclude(self):
        try:
            os.environ["DOCKER_MATCH_CONTAINER_NAME"] = "container0, container1, container2"
            os.environ["DOCKER_SKIP_CONTAINER_NAME"] = "container0, container1, container2"
            self.assertRaises(KeyError, setup)
        finally:
            del os.environ["DOCKER_MATCH_CONTAINER_NAME"]
            del os.environ["DOCKER_SKIP_CONTAINER_NAME"]

    def test_period(self):
        try:
            conf = setup()
            self.assertEqual(conf[0]["period"], "10s")

            period = os.environ["DOCKER_PERIOD"] = "1s"
            conf = setup()
            self.assertEqual(conf[0]["period"], period)
        finally:
            del os.environ["DOCKER_PERIOD"]

    def test_certificate(self):
        try:
            conf = setup()
            self.assertRaises(KeyError, lambda: conf[0]["ssl"])

            certificate_authority = os.environ["DOCKER_CERTIFICATE_AUTHORITY"] = "/etc/pki/root/ca.pem"
            certificate = os.environ["DOCKER_CERTIFICATE"] = "/etc/pki/client/cert.pem"
            key = os.environ["DOCKER_KEY"] = "/etc/pki/client/cert.key"
            conf = setup()
            self.assertEqual(conf[0]["ssl"]["certificate_authority"], certificate_authority)
            self.assertEqual(conf[0]["ssl"]["certificate"], certificate)
            self.assertEqual(conf[0]["ssl"]["key"], key)
        finally:
            del os.environ["DOCKER_CERTIFICATE_AUTHORITY"]
            del os.environ["DOCKER_CERTIFICATE"]
            del os.environ["DOCKER_KEY"]

    def test_cpu_per_core(self):
        try:
            conf = setup()
            self.assertRaises(KeyError, lambda: conf[0]["cpu.cores"])

            os.environ["DOCKER_CPU_PER_CORE"] = "true"
            conf = setup()
            self.assertEqual(conf[0]["cpu.cores"], "true")
        finally:
            del os.environ["DOCKER_CPU_PER_CORE"]


if __name__ == '__main__':
    unittest.main()
