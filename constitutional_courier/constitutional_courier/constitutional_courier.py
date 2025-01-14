import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex
from kivy.graphics import RoundedRectangle, Color, Rectangle
from kivy.core.window import Keyboard

class GruvboxTheme:
    """Gruvbox color palette with patriotic theme"""
    # Background colors
    DARK_0 = '#282828'    # Dark background for all text
    DARK_1 = '#282828'    # Changed to match DARK_0 for consistency
    DARK_2 = '#282828'    # Changed to match DARK_0 for consistency

    # Text color
    CREAM = '#fbf1c7'     # Universal text color

    # Accent colors
    RED = '#cc241d'       # Deep red for highlights
    BLUE = '#458588'      # Navy blue for interactive elements
    GRAY = '#928374'      # Soft gray for borders

    # UI elements
    BORDER_RADIUS = 12
    GRADIENT_START = '#282828'  # Changed to match DARK_0
    GRADIENT_END = '#282828'    # Changed to match DARK_0

class GradientSidebar(BoxLayout):
    """Sidebar with consistent background"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*get_color_from_hex(GruvboxTheme.DARK_0))
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[GruvboxTheme.BORDER_RADIUS]
            )
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class PatrioticButton(Button):
    """Patriotic styled button with consistent text color"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.border = (0, 0, 0, 0)

        with self.canvas.before:
            Color(*get_color_from_hex(GruvboxTheme.BLUE))
            self.rounded_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[GruvboxTheme.BORDER_RADIUS]
            )

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.color = get_color_from_hex(GruvboxTheme.CREAM)

    def update_rect(self, *args):
        self.rounded_rect.pos = self.pos
        self.rounded_rect.size = self.size

class ConstitutionTextInput(TextInput):
    """Custom text input with consistent styling"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.border = (0, 0, 0, 0)

        with self.canvas.before:
            Color(*get_color_from_hex(GruvboxTheme.DARK_0))
            self.rounded_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[GruvboxTheme.BORDER_RADIUS]
            )
            Color(*get_color_from_hex(GruvboxTheme.GRAY), 0.5)
            self.border_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[GruvboxTheme.BORDER_RADIUS]
            )

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.cursor_color = get_color_from_hex(GruvboxTheme.CREAM)
        self.foreground_color = get_color_from_hex(GruvboxTheme.CREAM)

    def update_rect(self, *args):
        self.rounded_rect.pos = self.pos
        self.rounded_rect.size = self.size
        self.border_rect.pos = self.pos
        self.border_rect.size = self.size

class SidebarItem(RecycleDataViewBehavior, Label):
    """Styled sidebar item with consistent text color"""
    text = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = get_color_from_hex(GruvboxTheme.CREAM)
        self.font_size = dp(14)
        self.padding = (dp(16), dp(8))
        self.bind(on_touch_down=self.on_touch_down)
        self.background_color = get_color_from_hex(GruvboxTheme.DARK_0)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.color = get_color_from_hex(GruvboxTheme.RED)
            return True
        return super().on_touch_down(touch)

class ConstitutionalCourierApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Constitutional Courier"
        self.constitution_text = self.load_constitution()
        self.index_items = self.generate_index()
        self.current_search_matches = []
        self.current_match_index = 0

    def load_constitution(self):
        """Load constitution text from file"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, "constitution.txt")
            with open(file_path, "r", encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return "Error: Constitution file not found."
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def generate_index(self):
        """Generate an index of Articles and Amendments"""
        index_items = []
        lines = self.constitution_text.splitlines()
        for line in lines:
            if line.startswith("Article") or line.startswith("Amendment"):
                index_items.append(line.strip())
        return index_items

    def build(self):
        """Build the main application layout"""
        # Set window properties
        Window.size = (1400, 800)
        Window.minimum_width = 800
        Window.minimum_height = 600
        Window.clearcolor = get_color_from_hex(GruvboxTheme.DARK_0)

        # Main container
        main_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(24),
            padding=dp(24)
        )

        # Sidebar
        sidebar = GradientSidebar(
            orientation='vertical',
            size_hint_x=0.25,
            padding=dp(16)
        )

        # Title
        title = Label(
            text="The U.S. Constitution",
            color=get_color_from_hex(GruvboxTheme.CREAM),
            font_size=dp(24),
            size_hint_y=None,
            height=dp(48),
            bold=True
        )
        sidebar.add_widget(title)

        # Index RecycleView
        self.index_view = RecycleView(
            viewclass='SidebarItem',
            bar_width=dp(4),
            bar_color=get_color_from_hex(GruvboxTheme.BLUE),
            bar_inactive_color=get_color_from_hex(GruvboxTheme.GRAY)
        )
        self.index_view.data = [{'text': item} for item in self.index_items]
        sidebar.add_widget(self.index_view)

        # Main content area
        content = BoxLayout(orientation='vertical', spacing=dp(16))

        # Search and navigation container
        search_container = BoxLayout(
            size_hint_y=None,
            height=dp(56),
            spacing=dp(8)
        )

        # Search input
        self.search_input = ConstitutionTextInput(
            hint_text='Search the Constitution... (Ctrl+F)',
            multiline=False,
            size_hint_x=0.7,
            font_size=dp(16),
            padding=(dp(16), dp(12)),
            foreground_color=get_color_from_hex(GruvboxTheme.CREAM)
        )
        self.search_input.bind(text=self.on_search_text)
        search_container.add_widget(self.search_input)

        # Navigation buttons
        nav_buttons = BoxLayout(
            size_hint_x=0.3,
            spacing=dp(8)
        )

        prev_btn = PatrioticButton(
            text='◀',
            size_hint_x=None,
            width=dp(56)
        )
        prev_btn.bind(on_press=self.goto_previous_match)

        next_btn = PatrioticButton(
            text='▶',
            size_hint_x=None,
            width=dp(56)
        )
        next_btn.bind(on_press=self.goto_next_match)

        nav_buttons.add_widget(prev_btn)
        nav_buttons.add_widget(next_btn)
        search_container.add_widget(nav_buttons)

        # Text area
        self.text_area = ConstitutionTextInput(
            text=self.constitution_text,
            multiline=True,
            readonly=True,
            font_size=dp(16),
            foreground_color=get_color_from_hex(GruvboxTheme.CREAM)
        )

        content.add_widget(search_container)
        content.add_widget(self.text_area)

        # Add everything to main layout
        main_layout.add_widget(sidebar)
        main_layout.add_widget(content)

        # Bind Ctrl+F
        Window.bind(on_key_down=self.on_key_down)

        return main_layout

    def on_key_down(self, instance, keyboard, keycode, scancode, text, modifiers):
        """Handle Ctrl+F shortcut"""
        if scancode == 42 and 'ctrl' in modifiers:  # 42 is typically the scancode for 'f'
            self.search_input.focus = True
            return True
        return False

    def on_search_text(self, instance, value):
        """Handle search input changes"""
        search_text = value.lower()
        if search_text:
            self.find_search_matches(search_text)

    def find_search_matches(self, search_text):
        """Find all matches for search text"""
        self.current_search_matches = []
        text_lower = self.constitution_text.lower()
        search_lower = search_text.lower()

        start = 0
        while True:
            index = text_lower.find(search_lower, start)
            if index == -1:
                break
            self.current_search_matches.append(index)
            start = index + 1

        if self.current_search_matches:
            self.current_match_index = 0
            self.highlight_current_match()

    def highlight_current_match(self):
        """Highlight the current search match"""
        if not self.current_search_matches:
            return

        match_index = self.current_search_matches[self.current_match_index]
        search_text = self.search_input.text

        self.text_area.cursor = (match_index, 0)
        self.text_area.select_text(match_index, match_index + len(search_text))

    def goto_next_match(self, instance):
        """Navigate to next search match"""
        if self.current_search_matches:
            self.current_match_index = (self.current_match_index + 1) % len(self.current_search_matches)
            self.highlight_current_match()

    def goto_previous_match(self, instance):
        """Navigate to previous search match"""
        if self.current_search_matches:
            self.current_match_index = (self.current_match_index - 1) % len(self.current_search_matches)
            self.highlight_current_match()

def main():
    """Main application entry point"""
    ConstitutionalCourierApp().run()

if __name__ == '__main__':
    main()
