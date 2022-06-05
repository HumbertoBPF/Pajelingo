from abc import ABC, abstractmethod


class Game(ABC):
    @staticmethod
    @abstractmethod
    def get_tag():
        pass

    @staticmethod
    @abstractmethod
    def setup(request):
        pass

    @staticmethod
    @abstractmethod
    def play(request):
        pass
    
    @staticmethod
    @abstractmethod
    def verify_answer(request):
        pass
