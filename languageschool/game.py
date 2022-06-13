from abc import ABC, abstractmethod


class GameView(ABC):
    @staticmethod
    @abstractmethod
    def get_game_model():
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
