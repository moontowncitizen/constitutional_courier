import gi
import os
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, Adw, GLib, Gdk

class ConstitutionalCourier(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.example.constitutionalcourier",
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.window = None
        self.constitution_text = ""

        # Set up dark theme
        self.style_manager = Adw.StyleManager.get_default()
        self.style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data("""
            /* Base colors - Gruvbox Dark with Patriotic touches */
            @define-color bg_dark #1d2021;
            @define-color bg_main #282828;
            @define-color fg_main #ebdbb2;
            @define-color red_deep #cc241d;
            @define-color blue_deep #458588;
            @define-color white_pure #ffffff;
            @define-color cream_accent #d5c4a1;

            /* Sidebar styling */
            .sidebar-list {
                background-color: @bg_dark;
                color: @fg_main;
            }

            .sidebar-list row {
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px 4px;
                transition: all 200ms ease;
            }

            .sidebar-list row:hover {
                background-color: alpha(@blue_deep, 0.3);
            }

            .sidebar-list row:selected {
                background: linear-gradient(45deg, @red_deep, @blue_deep);
                color: @white_pure;
                font-weight: bold;
            }

            .sidebar-list row label {
                color: @fg_main;
            }

            .sidebar-list row:selected label {
                color: @white_pure;
            }

            /* Content area styling */
            .content-area {
                background-color: @bg_main;
                color: @fg_main;
                padding: 8px;
            }

            .content-area selection {
                background-color: @blue_deep;
                color: @white_pure;
            }

            /* Search entry styling */
            .search-entry {
                background-color: @bg_dark;
                border: 2px solid @blue_deep;
                border-radius: 6px;
                color: @fg_main;
                margin: 6px;
                padding: 6px 12px;
                caret-color: @red_deep;
            }

            .search-entry:focus {
                border-color: @red_deep;
                box-shadow: 0 0 0 1px alpha(@red_deep, 0.3);
            }

            /* Window styling */
            window {
                background-color: @bg_main;
            }

            /* Scrollbar styling */
            scrollbar {
                background-color: transparent;
                border-radius: 8px;
            }

            scrollbar slider {
                background-color: alpha(@blue_deep, 0.7);
                border-radius: 6px;
                min-width: 8px;
                min-height: 8px;
            }

            scrollbar slider:hover {
                background-color: @blue_deep;
            }
        """.encode())

        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def do_activate(self):
        if not self.window:
            # Create window with proper sizing constraints
            self.window = Adw.ApplicationWindow(application=self)
            self.window.set_default_size(1000, 700)
            self.window.set_size_request(600, 400)  # Minimum window size

            # Main vertical box
            main_vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.window.set_content(main_vertical_box)

            # Header bar
            header = Adw.HeaderBar()
            title = Adw.WindowTitle.new("Constitutional Courier", "United States Constitution Reader")
            header.set_title_widget(title)

            # Menu button
            menu_button = Gtk.MenuButton()
            menu_button.set_icon_name("open-menu-symbolic")

            menu = Gio.Menu.new()
            menu.append("About", "app.about")
            menu.append("Quit", "app.quit")

            menu_button.set_menu_model(menu)
            header.pack_end(menu_button)
            main_vertical_box.append(header)

            # Content paned (for resizable sidebar)
            paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
            main_vertical_box.append(paned)
            paned.set_resize_start_child(False)  # Don't resize sidebar
            paned.set_shrink_start_child(False)  # Don't shrink sidebar
            paned.set_resize_end_child(True)     # Allow content area to resize

            # Sidebar with scrolling
            sidebar_scroll = Gtk.ScrolledWindow()
            sidebar_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            sidebar_scroll.set_size_request(250, -1)

            self.sidebar = Gtk.ListBox()
            self.sidebar.set_vexpand(True)
            sidebar_scroll.set_child(self.sidebar)
            paned.set_start_child(sidebar_scroll)

            # Content area
            content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            content_box.set_hexpand(True)
            paned.set_end_child(content_box)

            # Search box
            search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            search_box.set_margin_start(8)
            search_box.set_margin_end(8)
            search_box.set_margin_top(8)
            search_box.set_margin_bottom(8)

            self.search_entry = Gtk.SearchEntry()
            self.search_entry.set_hexpand(True)
            self.search_entry.add_css_class("search-entry")
            self.search_entry.connect("activate", self.on_search_activated)  # Add Enter key support
            search_box.append(self.search_entry)

            search_button = Gtk.Button(label="Search")
            search_button.connect("clicked", self.on_search_clicked)
            search_box.append(search_button)

            content_box.append(search_box)

            # Text view with scrolling
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_hexpand(True)
            scrolled.set_vexpand(True)
            content_box.append(scrolled)

            self.text_view = Gtk.TextView()
            self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
            self.text_view.set_editable(False)
            self.text_view.add_css_class("content-area")
            scrolled.set_child(self.text_view)

            # Statusbar
            self.statusbar = Gtk.Label()
            self.statusbar.set_halign(Gtk.Align.START)
            self.statusbar.set_margin_start(8)
            self.statusbar.set_margin_end(8)
            self.statusbar.set_margin_top(4)
            self.statusbar.set_margin_bottom(4)
            content_box.append(self.statusbar)

            # Keyboard shortcuts
            self.window.add_controller(self.create_keybinding())

            # Actions
            quit_action = Gio.SimpleAction.new("quit", None)
            quit_action.connect("activate", self.on_quit)
            self.add_action(quit_action)

            about_action = Gio.SimpleAction.new("about", None)
            about_action.connect("activate", self.on_about)
            self.add_action(about_action)

            # Load content
            self.load_constitution()
            self.populate_sidebar()

        self.window.present()

    def on_search_activated(self, entry):
        """Handle Enter key in search entry"""
        self.on_search_clicked(None)

    def on_quit(self, action, param):
        self.quit()

    def on_about(self, action, param):
        about = Adw.AboutWindow(
            transient_for=self.window,
            application_name="Constitutional Courier",
            application_icon="text-editor-symbolic",
            developer_name="Your Name",
            version="1.0",
            developers=["Your Name"],
            copyright="© 2024 Your Name",
            website="https://github.com/yourusername/constitutional-courier",
            issue_url="https://github.com/yourusername/constitutional-courier/issues"
        )
        about.present()

    def create_keybinding(self):
        controller = Gtk.EventControllerKey()
        controller.connect("key-pressed", self.on_key_pressed)
        return controller

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_f and state & Gdk.ModifierType.CONTROL_MASK:
            self.search_entry.grab_focus()
            return True
        return False

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

        constitution_row = Gtk.ListBoxRow()
        constitution_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        constitution_box.set_margin_start(8)
        constitution_box.set_margin_end(8)
        constitution_box.set_margin_top(6)
        constitution_box.set_margin_bottom(6)

        constitution_label = Gtk.Label(label="The U.S. Constitution")
        constitution_label.set_halign(Gtk.Align.START)
        constitution_label.set_hexpand(True)
        constitution_box.append(constitution_label)
        constitution_row.set_child(constitution_box)
        self.sidebar.append(constitution_row)

        for title in self.articles:
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            box.set_margin_start(8)
            box.set_margin_end(8)
            box.set_margin_top(6)
            box.set_margin_bottom(6)

            label = Gtk.Label(label=title)
            label.set_halign(Gtk.Align.START)
            label.set_hexpand(True)
            box.append(label)
            row.set_child(box)
            self.sidebar.append(row)

        self.sidebar.connect("row-selected", self.on_sidebar_selection)
        self.sidebar.add_css_class("sidebar-list")
        self.sidebar.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar.set_activate_on_single_click(True)

    def on_search_clicked(self, button):
        search_text = self.search_entry.get_text().strip()
        if search_text:
            self.highlight_search_results(search_text)

    def highlight_search_results(self, search_text):
        self.text_buffer.remove_all_tags(
            self.text_buffer.get_start_iter(),
            self.text_buffer.get_end_iter()
        )

        search_tag = self.text_buffer.create_tag("search_highlight", background="#cc241d")
        start_iter = self.text_buffer.get_start_iter()
        match_count = 0

        while True:
            match = start_iter.forward_search(
                search_text,
                Gtk.TextSearchFlags.CASE_INSENSITIVE,
                None
            )
            if match:
                match_start, match_end = match
                self.text_buffer.apply_tag(search_tag, match_start, match_end)
                start_iter = match_end
                match_count += 1
            else:
                break

        if match_count > 0:
            self.statusbar.set_text(f"{match_count} results found for '{search_text}'")
            # Scroll to first match
            first_match = self.text_buffer.get_start_iter().forward_search(
                search_text,
                Gtk.TextSearchFlags.CASE_INSENSITIVE,
                None
            )
            if first_match:
                self.text_view.scroll_to_iter(first_match[0], 0.0, True, 0.0, 0.2)
        else:
            self.statusbar.set_text("No results found")

    def get_articles_and_amendments(self):
        articles = {}
        if self.constitution_text:
            lines = self.constitution_text.splitlines()
            for i, line in enumerate(lines):
                if line.startswith("Article") or line.startswith("Amendment") or line.endswith("Amendment"):
                    articles[line] = self.constitution_text.find(line)
        return articles

    def on_sidebar_selection(self, listbox, row):
        if row:
            label = row.get_child().get_first_child()
            if isinstance(label, Gtk.Label):
                selected_title = label.get_text()
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
