from abc import ABC, abstractmethod

class BaseConnector(ABC):

    _client: None

    @abstractmethod
    def connect():
        raise NotImplementedError


    