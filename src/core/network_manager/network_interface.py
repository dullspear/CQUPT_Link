from abc import ABC, abstractmethod


class INetwork(ABC):
    """
    网络接口，定义所有平台网络操作的共同接口。
    """

    @abstractmethod
    def connect_to_wifi(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_local_ip(self) -> str:
        raise NotImplementedError
