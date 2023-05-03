# BookSmith

BookSmith is an open-source command-line tool that enables you to summarize books in PDF or EPUB format. The tool allows you to selectively process pages or entire books, and provides options to include only important sections, handle model token limits, and synthesize content further from the summary. BookSmith leverages the power of OpenAI's ChatGPT for generating summaries.

## Features

- Summarize PDF and EPUB books
- Select specific pages for processing (only supports pdfs for now)
- Output summary in Markdown or JSON format
- Optionally include only important sections in the summary
- Handle model token limits by splitting sections
- Synthesize content further from the summary

## Installation

To install BookSmith, simply clone the repository and install the required packages:

```bash
git clone https://github.com/harigov/BookSmith.git
cd BookSmith
pip install -r requirements.txt
```

## Usage

BookSmith provides a command-line interface for easy usage. The following arguments are available:

- `--input_path`: Path to the input EPUB or PDF file that needs to be processed (required).
- `--pages`: Page numbers to extract from the input file (optional, default: None). Example: 1-10.
- `--output_path`: Path to the output file where the summary will be written (optional, default: None). Can either be a Markdown file or a JSON file.
- `--only_important`: Whether to only include important sections in the summary (optional, default: True).
- `--allow_splitting`: Whether to allow splitting of sections into multiple parts to deal with model token limit (optional, default: True).
- `--synthesize`: Whether to synthesize the content further from the summary (optional, default: True).

### Example

To summarize a book and save the output as a Markdown file, use the following command:

```bash
python booksmith.py --input_path input.pdf --pages 1-10 --output_path output.md
```

## API Key

BookSmith uses OpenAI's ChatGPT API to generate summaries. You will need an API key for the ChatGPT service. Set the environment variable `OPENAI_API_KEY` with your API key:

```bash
export OPENAI_API_KEY="your-api-key"
```

Replace `"your-api-key"` with your actual ChatGPT API key.

## Future Plans

We have several exciting features planned for BookSmith's future development:

1. **Language Conversion**: Enhance BookSmith to translate books from one language to another, providing greater accessibility for readers across different languages.
2. **Audio Book Generation**: Add the ability to convert books or summaries into audio format, allowing users to enjoy their favorite books while on-the-go or multitasking.
3. **Summary from Audio Books**: Extract summaries directly from audio books, offering a convenient way to review key points without reading or listening to the entire book.
4. **Multilingual Audio Book Generation**: Generate audio books in different languages using the book content, making literature more accessible to a global audience.
5. **Enhanced Configurability and Format Support**: Improve BookSmith with more configuration options and support for additional formats, making the tool even more versatile and user-friendly.

These future enhancements will make BookSmith an even more powerful tool for processing and consuming books in various formats and languages, catering to a wider range of users and their unique preferences. Stay tuned for updates and new feature releases!

## Contributing

We welcome contributions to the BookSmith project! If you'd like to contribute, please fork the repository, create a branch with your changes, and submit a pull request. If you find any issues or have feature requests, please open an issue on the GitHub repository.

## License

BookSmith is released under the MIT License. See [LICENSE](LICENSE) for more details.