from abc import ABC, abstractmethod


class BaseCheck(ABC):
    @abstractmethod
    def run(self):
        """
        Return a tuple of: (status, latency_ms, message).
        """
        raise NotImplementedError
