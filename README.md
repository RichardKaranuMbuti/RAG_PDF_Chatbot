# RAG_Chatbot
RAG_Chatbot is a full stack chatbot application built with Django that allows users to upload documents and get answers from those documents using a retrieval-augmented generation (RAG) model. The chatbot also utilizes OpenAI for additional context and responses.
Upload your pdfs and chat with them

# How to Run 



## Prerequisites

Before running the application, make sure you have the following installed:

- Python (version 3.6 or later)
- pip (Python package installer)

## Setting up the Environment

1. Clone the repository: `git clone https://github.com/your-username/RAG_Chatbot.git`
2. Navigate to the project directory: `cd RAG_Chatbot`
3. Create a virtual environment (optional but recommended): `python -m venv env`
   - Activate the virtual environment:
     - On Windows: `env\Scripts\activate`
     - On Unix or macOS: `source env/bin/activate`
4. Install the required packages: `pip install -r requirements.txt`

## Configuration

1. Create a `.env` file in the project root directory and add your OpenAI API key: `OPENAI_API_KEY=your_openai_api_key`
2. Apply Django migrations: `python manage.py migrate`

## Running the Application

1. Start the Django development server: `python manage.py runserver`
2. Open your web browser and navigate to `http://localhost:8000` to access the RAG_Chatbot application.

## Usage

1. Upload documents by clicking the "Upload Documents" button on the homepage.
2. Once documents are uploaded, you can start chatting with the chatbot by typing your queries in the input field.
3. The chatbot will search for relevant information from the uploaded documents using the RAG model and provide responses accordingly. It will also supplement the responses with additional context from OpenAI.

## Contributing

If you'd like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive commit messages.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.

## License

This project is licensed under the [MIT License](LICENSE).
