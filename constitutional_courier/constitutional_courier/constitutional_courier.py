import gi
import os
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GtkSource, Gdk

class ConstitutionalCourier(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.constitutionalcourier")
        self.window = None

    def do_activate(self):
        if not self.window:
            self.window = Gtk.ApplicationWindow(application=self)
            self.window.set_default_size(900, 700)

            # Apply dark theme
            settings = Gtk.Settings.get_default()
            settings.set_property("gtk-application-prefer-dark-theme", True)

            # Create header bar
            header_bar = Gtk.HeaderBar()
            header_bar.set_show_title_buttons(True)

            # Add a title label to the header bar
            title_label = Gtk.Label(label="Constitutional Courier")
            header_bar.set_title_widget(title_label)
            self.window.set_titlebar(header_bar)

            # Main Layout
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            main_box.set_margin_top(10)
            main_box.set_margin_bottom(10)
            main_box.set_margin_start(10)
            main_box.set_margin_end(10)
            self.window.set_child(main_box)

            # Search bar
            search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            self.search_entry = Gtk.Entry()
            self.search_entry.set_placeholder_text("Search...")
            search_button = Gtk.Button(label="Search")
            search_button.connect("clicked", self.on_search_clicked)
            search_box.append(self.search_entry)
            search_box.append(search_button)
            main_box.append(search_box)

            # Status bar
            self.statusbar = Gtk.Statusbar()
            main_box.append(self.statusbar)

            # Content area with sidebar and text view
            content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            main_box.append(content_box)

            # Sidebar
            sidebar = Gtk.ListBox()
            sidebar.set_selection_mode(Gtk.SelectionMode.SINGLE)
            sidebar.set_margin_end(10)
            content_box.append(sidebar)

            # Scrollable Text Area
            scrolled_window = Gtk.ScrolledWindow()
            scrolled_window.set_hexpand(True)
            scrolled_window.set_vexpand(True)
            content_box.append(scrolled_window)

            # Text View
            self.text_view = GtkSource.View()
            self.text_view.set_editable(False)
            self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
            scrolled_window.set_child(self.text_view)

            # Load the Constitution
            current_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(current_dir, "constitution.txt")
            with open(file_path, "r") as file:
                self.constitution_text = file.read()

            self.text_buffer = self.text_view.get_buffer()
            self.text_buffer.set_text(self.constitution_text)

            # Populate Sidebar
            self.articles = self.get_articles_and_amendments()
            constitution_row = Gtk.ListBoxRow()
            constitution_label = Gtk.Label(label="The U.S. Constitution")
            constitution_row.set_child(constitution_label)
            sidebar.append(constitution_row)

            for title in self.articles:
                row = Gtk.ListBoxRow()
                label = Gtk.Label(label=title)
                row.set_child(label)
                sidebar.append(row)

            sidebar.connect("row-selected", self.on_sidebar_selection)

            # Keyboard shortcut for search
            self.window.add_controller(self.create_keybinding())

        self.window.present()

    def create_keybinding(self):
        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self.on_key_pressed)
        return controller

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_f and (state & Gdk.ModifierType.CONTROL_MASK):
            self.search_entry.grab_focus()
            return True
        return False

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

    def on_search_clicked(self, button):
        search_text = self.search_entry.get_text().strip()
        if search_text:
            self.highlight_search_results(search_text)

    def highlight_search_results(self, search_text):
        # Remove previous tags
        self.text_buffer.remove_all_tags(self.text_buffer.get_start_iter(), self.text_buffer.get_end_iter())

        # Add a tag for search results
        search_tag = self.text_buffer.create_tag("search_highlight", background="yellow")

        # Start the search from the beginning of the buffer
        start_iter = self.text_buffer.get_start_iter()
        match_count = 0

        while True:
            # Perform case-insensitive search
            match = start_iter.forward_search(search_text, Gtk.TextSearchFlags.CASE_INSENSITIVE, None)
            if match:
                match_start, match_end = match
                # Apply the highlight tag to the found text
                self.text_buffer.apply_tag(search_tag, match_start, match_end)
                start_iter = match_end
                match_count += 1
            else:
                break

        # Update status bar with the number of matches found
        if match_count > 0:
            self.statusbar.push(0, f"{match_count} results found for '{search_text}'")
        else:
            self.statusbar.push(0, "No results found")

    def get_articles_and_amendments(self):
        # Dictionary to hold the title and its starting index in the text
        articles = {}
        lines = self.constitution_text.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("Article") or line.startswith("Amendment") or line.endswith("Amendment"):
                articles[line] = self.constitution_text.find(line)
        return articles

    def find_next_article_or_amendment(self, start_index):
        # Find the next occurrence of "Article" or "Amendment" after the current one
        next_index = len(self.constitution_text)
        for title, index in self.articles.items():
            if index > start_index and index < next_index:
                next_index = index
        return next_index

if __name__ == "__main__":
    app = ConstitutionalCourier()
    app.run()
