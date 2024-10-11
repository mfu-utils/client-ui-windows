import platform
from typing import List


class Machine:
    I386 = 'i386'
    AMD64 = 'AMD64'
    ARM64 = 'arm64'
    ARM32 = 'arm32'

    def __init__(self):
        self.name = platform.machine()

    def list(self) -> List[str]:
        return [self.I386, self.AMD64, self.ARM64, self.ARM32]

    def current(self) -> str:
        return self.name

    def is_i368(self) -> bool:
        return platform.machine() == self.I386

    def is_amd64(self) -> bool:
        return platform.machine() == self.AMD64

    def is_arm32(self) -> bool:
        return platform.machine() == self.ARM32

    def is_arm64(self) -> bool:
        return platform.machine() == self.ARM64
