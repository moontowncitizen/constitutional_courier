use iced::widget::{button, column, container, row, text, text_input};
use iced::{theme, Color, Element, Length, Sandbox, Settings};

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
    content: String,
}

#[derive(Debug, Clone)]
enum Message {
    SearchQueryChanged(String),
    SelectSection(usize),
}

impl Sandbox for ConstitutionalViewer {
    type Message = Message;

    fn new() -> Self {
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
            content: String::new(),
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
            }
            Message::SelectSection(index) => {
                self.selected_section = Some(index);
                self.content = self.sections[index].content.clone();
            }
        }
    }

    fn view(&self) -> Element<Message> {
        let search_bar = text_input("Search articles and amendments...", &self.search_query)
            .on_input(Message::SearchQueryChanged)
            .padding(10);

        let sections_list = self.filtered_sections.iter().map(|&index| {
            let section = &self.sections[index];
            button(text(&section.title).size(16))
                .width(Length::Fill)
                .padding(10)
                .style(if Some(index) == self.selected_section {
                    theme::Button::Primary
                } else {
                    theme::Button::Secondary
                })
                .on_press(Message::SelectSection(index))
        });

        let sections_column = column(sections_list.collect())
            .spacing(5)
            .width(Length::Fixed(200.0));

        let content_area = if let Some(index) = self.selected_section {
            let content = &self.sections[index].content;
            let highlighted_content = if !self.search_query.is_empty() {
                self.highlight_text(content)
            } else {
                text(content).size(16).into()
            };

            container(highlighted_content)
                .width(Length::Fill)
                .height(Length::Fill)
                .padding(20)
                .into()
        } else {
            container(
                text("Select a section to view its content")
                    .width(Length::Fill)
                    .height(Length::Fill)
                    .horizontal_alignment(iced::alignment::Horizontal::Center)
                    .vertical_alignment(iced::alignment::Vertical::Center),
            )
            .into()
        };

        let main_content = row![
            sections_column,
            content_area,
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

    fn highlight_text(&self, content: &str) -> Element<Message> {
        let search_term = self.search_query.to_lowercase();
        let content_lower = content.to_lowercase();

        let mut elements = Vec::new();
        let mut last_idx = 0;

        while let Some(found_idx) = content_lower[last_idx..].find(&search_term) {
            let absolute_idx = last_idx + found_idx;

            // Add non-matching text before the match
            if absolute_idx > last_idx {
                elements.push(
                    text(&content[last_idx..absolute_idx])
                        .size(16)
                        .into()
                );
            }

            // Add highlighted matching text
            elements.push(
                container(
                    text(&content[absolute_idx..absolute_idx + search_term.len()])
                        .size(16)
                )
                .style(theme::Container::Custom(Box::new(HighlightStyle)))
                .into()
            );

            last_idx = absolute_idx + search_term.len();
        }

        // Add remaining text
        if last_idx < content.len() {
            elements.push(
                text(&content[last_idx..])
                    .size(16)
                    .into()
            );
        }

        row(elements).spacing(0).into()
    }
}

struct HighlightStyle;

impl container::StyleSheet for HighlightStyle {
    type Style = theme::Theme;

    fn appearance(&self, _style: &Self::Style) -> container::Appearance {
        container::Appearance {
            background: Some(iced::Background::Color(Color::from_rgb(1.0, 1.0, 0.0))),
            ..Default::default()
        }
    }
}
