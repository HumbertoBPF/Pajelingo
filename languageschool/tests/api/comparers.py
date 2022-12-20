from abc import ABC, abstractmethod


class BaseComparer(ABC):
    """
    Abstract class that represents a comparer, i.e. an object that specified how two objects must be compared.
    """
    def __init__(self):
        self.obj_1 = None
        self.obj_2 = None

    @abstractmethod
    def are_equal(self, obj_1, obj_2):
        """
        :param obj_1: one of the objects to be compared
        :param obj_2: the other object to be compared
        """
        pass


class SimpleComparer(BaseComparer):
    """
    Class that specifies the simplest way how a dictionary and an object should be compared, that is when the keys of
    the dictionary and the attributes of the object match.
    """
    def are_equal(self, obj, dictionary):
        self.obj_1 = obj
        self.obj_2 = dictionary
        return self.are_attributes_and_keys_equal()

    def are_attributes_and_keys_equal(self):
        """
        Method that picks the dictionary keys and compares their values with the attributes of the object.
        """
        for key in self.obj_2.keys():
            attribute = getattr(self.obj_1, key)
            value = self.obj_2.get(key)
            if attribute != value:
                self.error_message(key, attribute, value)
                return False
        return True

    def get_sub_attribute(self, attribute_path):
        """
        Method that extracts a sub attribute from the object attribute of the comparer class according to the path
        specified as argument of this method.
        :param attribute_path: list indicating the path to the attribute whose value we want to extract.
        :type attribute_path: list

        :return: value held by the sub attribute specified. None is returned if there is no corresponding sub attribute.
        """
        sub_attribute = self.obj_1
        for attribute in attribute_path:
            if sub_attribute is None:
                break
            sub_attribute = getattr(sub_attribute, attribute)
        return sub_attribute

    def verify_sub_attribute(self, key, attribute_path):
        """
        Method that compares the specified key of the dictionary to the specified attribute of the object.
        :param key: key of the dictionary that we want to compare
        :param attribute_path: attribute of the object that we want to compare
        :type attribute_path: list

        :return: a boolean indicating if the value held by the key of the dictionary and by the attribute of the object
        are the same.
        """
        sub_attribute = self.get_sub_attribute(attribute_path)
        value = self.obj_2.get(key)

        if sub_attribute != value:
            self.error_message(key, sub_attribute, value)
            return False

        if value is not None:
            del self.obj_2[key]

        return True

    def error_message(self, key, attribute, value):
        print("Failed when verifying the key " + str(key))
        print(str(attribute) + " is not equal to " + str(value))


class ArticleComparer(SimpleComparer):
    def are_equal(self, article, dictionary):
        self.obj_1 = article
        self.obj_2 = dictionary

        self.verify_sub_attribute("language", ["language", "language_name"])

        return self.are_attributes_and_keys_equal()


class MeaningComparer(SimpleComparer):
    def are_equal(self, meaning, dictionary):
        self.obj_1 = meaning
        self.obj_2 = dictionary

        self.verify_sub_attribute("word", ["word", "id"])

        return self.are_attributes_and_keys_equal()


class ConjugationComparer(SimpleComparer):
    def are_equal(self, conjugation, dictionary):
        self.obj_1 = conjugation
        self.obj_2 = dictionary

        self.verify_sub_attribute("word", ["word", "id"])

        return self.are_attributes_and_keys_equal()


class WordComparer(SimpleComparer):
    def are_equal(self, word, dictionary):
        self.obj_1 = word
        self.obj_2 = dictionary

        self.verify_sub_attribute("language", ["language", "language_name"])
        self.verify_sub_attribute("category", ["category", "category_name"])
        self.verify_sub_attribute("article", ["article", "id"])

        if list(word.synonyms.all().values_list('id', flat=True)) != self.obj_2.get("synonyms"):
            self.error_message("synonyms", list(word.synonyms.all().values_list('id', flat=True)), self.obj_2.get("synonyms"))
            return False
        del self.obj_2["synonyms"]

        return self.are_attributes_and_keys_equal()


class ListScoresComparer(SimpleComparer):
    def are_equal(self, scores, dictionary):
        self.obj_1 = scores
        self.obj_2 = dictionary

        self.verify_sub_attribute("user", ["user", "username"])
        self.verify_sub_attribute("language", ["language", "language_name"])
        self.verify_sub_attribute("game", ["game", "id"])

        return self.are_attributes_and_keys_equal()

    def new_function(self):
        print("H")