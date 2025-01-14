from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListView, ListItemButton
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

class ConstitutionApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.constitution_text = self.load_constitution()
        self.articles = self.get_articles_and_amendments()

    def load_constitution(self):
        try:
            with open("constitution.txt", "r") as file:
                return file.read()
        except FileNotFoundError:
            return "Error: Constitution file not found."

    def get_articles_and_amendments(self):
        articles = []
        lines = self.constitution_text.splitlines()
        for line in lines:
            if line.startswith("Article") or line.startswith("Amendment"):
                articles.append(line)
        return articles

    def build(self):
        self.title = "Constitutional Courier"
        layout = BoxLayout(orientation='vertical')

        # Search input
        self.search_input = TextInput(hint_text='Search...', multiline=False)
        self.search_input.bind(text=self.on_search_text)

        # List view for articles
        self.article_list = ListView(item_strings=self.articles)
        self.article_list.adapter.bind(on_update=self.on_article_selected)

        # Text area for displaying content
        self.text_area = TextInput(text=self.constitution_text, multiline=True, readonly=True)

        layout.add_widget(self.search_input)
        layout.add_widget(self.article_list)
        layout.add_widget(self.text_area)

        return layout

    def on_article_selected(self, adapter, *args):
        selected_index = self.article_list.adapter.get_view_index(args[0])
        article_title = self.articles[selected_index]
        self.highlight_article(article_title)

    def highlight_article(self, article_title):
        start_idx = self.constitution_text.find(article_title)
        end_idx = self.find_next_article_or_amendment(start_idx)
        snippet = self.constitution_text[start_idx:end_idx].strip()
        self.text_area.text = snippet

    def find_next_article_or_amendment(self, start_index):
        next_index = len(self.constitution_text)
        for title in self.articles:
            index = self.constitution_text.find(title)
            if index > start_index and index < next_index:
                next_index = index
        return next_index

    def on_search_text(self, instance, value):
        search_text = value.lower()
        if search_text:
            self.highlight_search_results(search_text)

    def highlight_search_results(self, search_text):
        matches = [i for i in range(len(self.constitution_text)) if self.constitution_text.lower().startswith(search_text, i)]
        if matches:
            self.text_area.text = self.constitution_text
            for match in matches:
                self.text_area.text = self.text_area.text.replace(
                    self.constitution_text[match:match + len(search_text)],
                    f"[color=ff0000]{self.constitution_text[match:match + len(search_text)]}[/color]"
                )
        else:
            self.text_area.text = self.constitution_text

if __name__ == '__main__':
    ConstitutionApp().run()
