import abc

class BaseWeightClient(abc.ABC):

        @abc.abstractmethod
        def set_tare(self, *args, **kwargs):
            raise NotImplementedError()

        @abc.abstractmethod
        def get_gross_weight(self, *args, **kwargs):
            raise NotImplementedError()

        @abc.abstractmethod
        def get_net_weight(self, *args, **kwargs):
            raise NotImplementedError()

        @abc.abstractmethod
        def close_connection(self, *args, **kwargs):
            raise NotImplementedError()

        @abc.abstractmethod
        def close_all_connections(self, *args, **kwargs):
            raise NotImplementedError()