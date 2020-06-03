from bson import ObjectId
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.togglebutton import ToggleButton
import csv
from flashcards_test.config import *
from flashcards_test.config import db_x
from flashcards_test.learningWindows import *


class PopupCenter(Popup):
    pass


def show_popup(text, title=""):
    popup = PopupCenter()
    if title:
        popup.separator_height = 0
    else:
        popup.separator_height = 2
    popup.title = title
    popup.ids.label.text = text
    popup.open()


class CreateAccountWindow(Screen):

    font_size_large = NumericProperty(20)

    def submit(self):
        if self.namee.text != "" and self.email.text != "" and self.email.text.count(
                "@") == 1 and self.email.text.count(".") > 0:
            x = db_x.add_user(self.namee.text, self.email.text, self.password.text)
            if x == 1:
                show_popup("Account created\nsuccessfully!")
                # db_u.add_user(self.email.text, self.password.text, self.namee.text)
                # db_x.add_user(self.namee.text, self.email.text, self.password.text)
                self.reset()
                sm.current = "login"
            elif x == -1:
                show_popup("Error!")
                self.reset_pass()
                sm.current = "create"
            elif x == -2:
                show_popup("Error!")
                self.reset()
                sm.current = "create"
        else:
            self.reset()
            show_popup("Password must contain at least 8 characters\nEmail must be valid", "Incorrect data!")
            sm.current = "create"

    def reset_pass(self):
        self.password.text = ""

    def login(self):
        self.reset()
        sm.current = "login"

    def reset(self):
        self.email.text = ""
        self.password.text = ""
        self.namee.text = ""


class HomeScreenWindow(Screen):

    def log_out(self):
        sm.current = "login"

    def create_set(self):
        sm.current = "createSet"

    def searchSet(self):
        sm.current = "searchSet"

    def all_sets(self):
        global current_sets
        current_sets.clear()
        current_sets = db_x.all_sets()
        sm.current = "availableSets"


class LoginWindow(Screen):

    def loginBtn(self):
        # if db_u.validate(self.email.text, self.password.text):
        x = db_x.user_auth(self.email.text, self.password.text)
        if x == 1:
            global mail
            mail = self.email.text
            self.reset()
            sm.current = "homeScreenWindow"
        elif x == -1:
            self.reset()
            self.show_popup("No such user")
            sm.current = "login"
        else:
            self.reset()
            self.show_popup("Wrong password")
            sm.current = "login"

    def createBtn(self):
        self.reset()
        sm.current = "create"

    def reset(self):
        self.email.text = ""
        self.password.text = ""

    def back(self):
        sm.current = "login"


class LearningMethodWindow(Screen):
    def __init__(self, **kwargs):
        super(LearningMethodWindow, self).__init__(**kwargs)

    def reviewBtn(self):
        sm.current = "review"

    def testBtn(self):
        sm.current = "test"

    def quizBtn(self):
        if len(config.flashcard_set.Flashcards) >= 4:
            sm.current = "quiz"
        else:
            show_popup("Too few flashcards in set!")

    def mainMenu(self):
        sm.current = "homeScreenWindow"


class CreateSet(Screen):
    description = ObjectProperty(None)

    def log_out(self):
        sm.current = "login"
        self.reset()

    def mainMenu(self):
        sm.current = "homeScreenWindow"
        self.reset()

    def reset(self):
        self.description.text = ""

    def createSet(self):
        global flashcard_set
        flashcard_set = classes.Set(db_x.get_id(mail), self.description.text)
        # print(flashcard_set.ID)
        # print(flashcard_set.Flashcards)
        self.reset()
        sm.current = "createFlashcard"


class CreateFlashcard(Screen):

    def log_out(self):
        sm.current = "login"

    def mainMenu(self):
        sm.current = "homeScreenWindow"

    def reset(self):
        self.front.text = ""
        self.back.text = ""

    def addFlashcard(self):
        flashcard = classes.Flashcard(self.front.text, self.back.text, db_x.get_id(mail), flashcard_set.ID)
        flashcard_set.addFlashcard(flashcard)
        show_popup("You have created a flashcard!")
        self.reset()

    def uploadSet(self):
        db_x.upload_set(flashcard_set)
        sm.current = "homeScreenWindow"


class SearchSet(Screen):
    keyword = ObjectProperty(None)

    def mainMenu(self):
        sm.current = "homeScreenWindow"
        self.reset()

    def searchSet(self):
        global current_sets
        current_sets.clear()
        current_sets = db_x.sets_list_for_selection(self.keyword.text)

        sm.current = "availableSets"
        self.reset()

    def reset(self):
        self.keyword.text = ""


class AvailableSets(Screen):
    def __init__(self, **kwargs):
        super(AvailableSets, self).__init__(**kwargs)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.sets = dict()

    def on_enter(self, *args):
        for key, cardsSet in current_sets.items():
            button = Button(text=cardsSet.description + "\nby "+str(cardsSet.Creator))
            button.size_hint = (0.8, 0.35)
            button.bind(on_press=self.pressed)
            self.sets[button] = cardsSet.ID
            self.ids.grid.add_widget(button)

    def pressed(self, instance):
        setID = self.sets[instance]
        # global flashcard_set
        # del flashcard_set
        config.flashcard_set = current_sets[ObjectId(setID)]
        current_sets.clear()
        sm.current = "learningMethod"
        self.reset()

    def mainMenu(self):
        sm.current = "homeScreenWindow"
        self.reset()

    def reset(self):
        for button in self.sets.keys():
            self.ids.grid.remove_widget(button)


screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"),
           ReviewWindow(name="review"),
           HomeScreenWindow(name="homeScreenWindow"), CreateFlashcard(name="createFlashcard"),
           CreateSet(name="createSet"), SearchSet(name="searchSet"),
           AvailableSets(name="availableSets"), LearningMethodWindow(name="learningMethod"),
           TestWindow(name="test"), QuizWindow(name="quiz")]

for screen in screens:
    sm.add_widget(screen)

sm.current = "homeScreenWindow"


class MyMainApp(App):

    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()
