use iced::widget::{button, column, container, row, scrollable, text, text_editor, text_input};
use iced::{alignment, Color, Element, Length, Sandbox, Settings};
use iced::widget::text_editor::{Action, Content, TextEditor};
use iced::advanced::text::Text;

fn main() -> iced::Result {
    ConstitutionalViewer::run(Settings::default())
}

#[derive(Debug, Clone)]
struct Section {
    title: String,
    content: String,
}

struct ConstitutionalViewer {
    sections: Vec<Section>,
    search_query: String,
    filtered_sections: Vec<usize>,
    selected_section: Option<usize>,
    content: Content,
    highlighted_ranges: Vec<(usize, usize)>,  // Start and end positions of highlights
}

#[derive(Debug, Clone)]
enum Message {
    SearchQueryChanged(String),
    SelectSection(usize),
    Edit(Action),
}

impl Sandbox for ConstitutionalViewer {
    type Message = Message;

    fn new() -> Self {
        // Example sections - you can replace these with actual content
        let sections = vec![
            Section {
                title: "Article I".to_string(),
                content: "Section 1. All legislative Powers herein granted shall be vested in a Congress of the United States, which shall consist of a Senate and House of Representatives.".to_string(),
            },
            Section {
                title: "Article II".to_string(),
                content: "Section 1. The executive Power shall be vested in a President of the United States of America.".to_string(),
            },
            Section {
                title: "Amendment I".to_string(),
                content: "Congress shall make no law respecting an establishment of religion, or prohibiting the free exercise thereof; or abridging the freedom of speech, or of the press;".to_string(),
            },
        ];

        let mut viewer = ConstitutionalViewer {
            sections,
            search_query: String::new(),
            filtered_sections: Vec::new(),
            selected_section: None,
            content: Content::new(),
            highlighted_ranges: Vec::new(),
        };

        viewer.update_filtered_sections();
        viewer
    }

    fn title(&self) -> String {
        String::from("Constitutional Text Viewer")
    }

    fn update(&mut self, message: Message) {
        match message {
            Message::SearchQueryChanged(query) => {
                self.search_query = query;
                self.update_filtered_sections();
                self.update_highlights();
            }
            Message::SelectSection(index) => {
                self.selected_section = Some(index);
                self.content = Content::with_text(&self.sections[index].content);
                self.update_highlights();
            }
            Message::Edit(action) => {
                self.content.edit(action);
                if let Some(index) = self.selected_section {
                    self.sections[index].content = self.content.text();
                    self.update_highlights();
                }
            }
        }
    }

    fn view(&self) -> Element<Message> {
        let search_bar = text_input(
            "Search articles and amendments...",
            &self.search_query,
            Message::SearchQueryChanged,
        )
        .padding(10);

        let sections_list = self.filtered_sections.iter().map(|&index| {
            let section = &self.sections[index];
            button(text(&section.title).size(16))
                .width(Length::Fill)
                .padding(10)
                .style(if Some(index) == self.selected_section {
                    iced::theme::Button::Primary
                } else {
                    iced::theme::Button::Secondary
                })
                .on_press(Message::SelectSection(index))
                .into()
        });

        let sections_column = column(sections_list.collect())
            .spacing(5)
            .width(Length::Fixed(200.0));

        // Create a custom styled text editor
        let editor = TextEditor::new(&self.content)
            .on_edit(Message::Edit)
            .highlight_ranges(self.highlighted_ranges.iter().map(|&(start, end)| {
                (start..end, iced::Background::Color(Color::from_rgb(1.0, 1.0, 0.0)))
            }))
            .width(Length::Fill)
            .height(Length::Fill);

        let content_area = if self.selected_section.is_some() {
            editor.into()
        } else {
            text("Select a section to view its content")
                .width(Length::Fill)
                .height(Length::Fill)
                .horizontal_alignment(alignment::Horizontal::Center)
                .vertical_alignment(alignment::Vertical::Center)
                .into()
        };

        let main_content = row![
            sections_column,
            container(content_area)
                .width(Length::Fill)
                .height(Length::Fill)
                .padding(20),
        ]
        .spacing(20);

        container(
            column![
                text("Constitutional Text Viewer").size(24),
                search_bar,
                main_content,
            ]
            .spacing(20)
            .padding(20),
        )
        .width(Length::Fill)
        .height(Length::Fill)
        .into()
    }
}

impl ConstitutionalViewer {
    fn update_filtered_sections(&mut self) {
        self.filtered_sections = self
            .sections
            .iter()
            .enumerate()
            .filter(|(_, section)| {
                let search_lower = self.search_query.to_lowercase();
                section.title.to_lowercase().contains(&search_lower)
                    || section.content.to_lowercase().contains(&search_lower)
            })
            .map(|(index, _)| index)
            .collect();
    }

    fn update_highlights(&mut self) {
        self.highlighted_ranges.clear();

        if self.search_query.is_empty() {
            return;
        }

        let content = self.content.text().to_lowercase();
        let search_term = self.search_query.to_lowercase();

        let mut start_idx = 0;
        while let Some(found_idx) = content[start_idx..].find(&search_term) {
            let absolute_idx = start_idx + found_idx;
            self.highlighted_ranges.push((
                absolute_idx,
                absolute_idx + search_term.len()
            ));
            start_idx = absolute_idx + search_term.len();
        }
    }
}
