import gi
import os
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GLib, Gdk

class ConstitutionalCourier(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.example.constitutionalcourier")
        self.window = None

        # Set up dark theme properly using AdwStyleManager
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data("""
            .sidebar-list {
                background-color: #282828;
                color: #ebdbb2;
            }

            .sidebar-list row:selected {
                background-color: #cc241d;
            }

            .content-area {
                background-color: #282828;
                color: #ebdbb2;
            }

            .search-entry {
                background-color: #282828;
                border: 1px solid #458588;
                color: #ebdbb2;
                margin: 6px;
            }

            .search-entry:focus {
                border-color: #cc241d;
            }

            .title-label {
                color: #ebdbb2;
                font-weight: bold;
                font-size: 16px;
            }
        """.encode())

        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        else:
            print("Warning: Could not get default display")

    def do_activate(self):
        if not self.window:
            # Create main window using Adw.ApplicationWindow
            self.window = Adw.ApplicationWindow(application=self)
            self.window.set_default_size(900, 700)

            # Main layout using Gtk.Box
            main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

            # Sidebar
            sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            sidebar_box.set_size_request(200, -1)  # Set initial width

            # Sidebar header
            sidebar_header = Adw.HeaderBar()
            sidebar_header.set_show_end_title_buttons(False)
            title_label = Gtk.Label(label="Contents")
            title_label.add_css_class("title-label")
            sidebar_header.set_title_widget(title_label)
            sidebar_box.append(sidebar_header)

            # Sidebar list
            self.sidebar = Gtk.ListBox()
            self.sidebar.add_css_class("sidebar-list")
            self.sidebar.set_selection_mode(Gtk.SelectionMode.SINGLE)

            sidebar_scroll = Gtk.ScrolledWindow()
            sidebar_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            sidebar_scroll.set_child(self.sidebar)
            sidebar_box.append(sidebar_scroll)

            # Content area
            content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

            # Main content header bar
            header_bar = Adw.HeaderBar()
            title_label = Gtk.Label(label="Constitutional Courier")
            title_label.add_css_class("title-label")
            header_bar.set_title_widget(title_label)
            content_box.append(header_bar)

            # Search bar
            search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            search_box.set_margin_top(10)
            search_box.set_margin_start(10)
            search_box.set_margin_end(10)

            self.search_entry = Gtk.SearchEntry()
            self.search_entry.add_css_class("search-entry")
            self.search_entry.set_placeholder_text("Search (Ctrl+F)...")

            search_button = Gtk.Button(label="Search")
            search_button.add_css_class("accent")
            search_button.connect("clicked", self.on_search_clicked)

            search_box.append(self.search_entry)
            search_box.append(search_button)
            content_box.append(search_box)

            # Text view
            text_scroll = Gtk.ScrolledWindow()
            text_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            text_scroll.set_hexpand(True)
            text_scroll.set_vexpand(True)

            self.text_view = Gtk.TextView()
            self.text_view.add_css_class("content-area")
            self.text_view.set_editable(False)
            self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
            self.text_view.set_margin_start(10)
            self.text_view.set_margin_end(10)
            self.text_view.set_margin_top(10)
            self.text_view.set_margin_bottom(10)

            text_scroll.set_child(self.text_view)
            content_box.append(text_scroll)

            # Status bar
            self.statusbar = Gtk.Statusbar()
            content_box.append(self.statusbar)

            # Add everything to the main box
            main_box.append(sidebar_box)
            main_box.append(content_box)

            # Set the main box as the window content
            self.window.set_content(main_box)

            # Load content
            self.load_constitution()
            self.populate_sidebar()

            # Set up keyboard shortcuts
            self.window.add_controller(self.create_keybinding())

        self.window.present()

    def load_constitution(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "constitution.txt")
        try:
            with open(file_path, "r") as file:
                self.constitution_text = file.read()
        except FileNotFoundError:
            self.constitution_text = "Error: Constitution file not found."

        self.text_buffer = self.text_view.get_buffer()
        self.text_buffer.set_text(self.constitution_text)

    def populate_sidebar(self):
        self.articles = self.get_articles_and_amendments()

        # Add full constitution option
        constitution_row = Gtk.ListBoxRow()
        constitution_label = Gtk.Label(label="The U.S. Constitution")
        constitution_label.set_halign(Gtk.Align.START)
        constitution_label.set_margin_start(10)
        constitution_label.set_margin_top(5)
        constitution_label.set_margin_bottom(5)
        constitution_row.set_child(constitution_label)
        self.sidebar.append(constitution_row)

        # Add articles and amendments
        for title in self.articles:
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=title)
            label.set_halign(Gtk.Align.START)
            label.set_margin_start(10)
            label.set_margin_top(5)
            label.set_margin_bottom(5)
            row.set_child(label)
            self.sidebar.append(row)

        self.sidebar.connect("row-selected", self.on_sidebar_selection)

    def create_keybinding(self):
        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self.on_key_pressed)
        return controller

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_f and state & Gdk.ModifierType.CONTROL_MASK:
            self.search_entry.grab_focus()
            return True
        return False

    def on_search_clicked(self, button):
        search_text = self.search_entry.get_text().strip()
        if search_text:
            self.highlight_search_results(search_text)

    def highlight_search_results(self, search_text):
        # Remove previous tags
        self.text_buffer.remove_all_tags(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter())

        # Add a tag for search results
        search_tag = self.text_buffer.create_tag("search_highlight", background="#cc241d")

        # Start the search from the beginning of the buffer
        start_iter = self.text_buffer.get_start_iter()
        match_count = 0

        while True:
            match = start_iter.forward_search(search_text, Gtk.TextSearchFlags.CASE_INSENSITIVE, None)
            if match:
                match_start, match_end = match
                self.text_buffer.apply_tag(search_tag, match_start, match_end)
                start_iter = match_end
                match_count += 1
            else:
                break

        if match_count > 0:
            self.statusbar.push(0, f"{match_count} results found for '{search_text}'")
        else:
            self.statusbar.push(0, "No results found")

    def get_articles_and_amendments(self):
        articles = {}
        lines = self.constitution_text.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("Article") or line.startswith("Amendment") or line.endswith("Amendment"):
                articles[line] = self.constitution_text.find(line)
        return articles

    def on_sidebar_selection(self, listbox, row):
        if row:
            selected_title = row.get_child().get_text()
            if selected_title == "The U.S. Constitution":
                self.text_buffer.set_text(self.constitution_text)
            else:
                start_index = self.articles[selected_title]
                end_index = self.find_next_article_or_amendment(start_index)
                snippet = self.constitution_text[start_index:end_index].strip()
                self.text_buffer.set_text(snippet)

    def find_next_article_or_amendment(self, start_index):
        next_index = len(self.constitution_text)
        for title, index in self.articles.items():
            if index > start_index and index < next_index:
                next_index = index
        return next_index

if __name__ == "__main__":
    app = ConstitutionalCourier()
    app.run(None)
