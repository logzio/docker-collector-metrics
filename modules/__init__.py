from .docker import docker
from .system import system

setups = {
    (docker.name(), docker.setup),
    (system.name(), system.setup)
}
