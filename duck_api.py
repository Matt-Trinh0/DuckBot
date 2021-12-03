import random
from PIL import Image
from IPython.display import display
import requests

class DuckFact():
    def __init__(self):
        self.images = "image_links.txt"
        self.num_images = len(open(self.images).readlines())
        self.facts = "duck_facts.txt"
        self.num_facts = len(open(self.facts).readlines())

    def getFact(self):
        fact_num = random.randint(1, self.num_facts) - 1

        with open(self.facts, 'r', encoding='utf8') as file:
            fact = file.readlines()
        
        return fact[fact_num]

    def getImage(self):
        image_num = random.randint(1, self.num_images) - 1

        with open(self.images, 'r', encoding='utf8') as file:
            image = file.readlines()
        
        return image[image_num]

    def addFact(self, fact):
        if fact[-1:] != "\n":
            fact = fact + "\n"
        with open(self.facts, 'a', encoding='utf8') as file:
            file.write(fact)
        return

    def addImage(self, image_link):
        if image_link[-1:] != "\n":
            image_link = image_link + "\n"
        with open(self.images, 'a', encoding='utf8') as file:
            file.write(image_link)
        return