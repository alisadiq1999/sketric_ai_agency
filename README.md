# Realtime API Async Python Assistant

This project demonstrates the use of OpenAI's Realtime API to create an AI assistant capable of handling voice input, performing various tasks, and providing audio responses. It showcases the integration of tools, structured output responses, and real-time interaction.

## Features

### Core Functionality
- Real-time voice interaction with an AI assistant
- Asynchronous audio input and output handling
- Custom tools execution based on user requests

### Task Delegation & Communication
- **Synchronous Communication**: Direct, immediate interaction with agents for quick tasks
- **Asynchronous Task Delegation**: Long-running task delegation to agencies/agents
  - Send messages to agency CEOs without waiting for responses
  - Send messages to subordinate agents on behalf of CEOs
- **Task Status Monitoring**: Check completion status and retrieve responses
- Multiple specialized AI agent teams working collaboratively

### Integration Services
- Google Calendar integration for meeting schedule management
- Gmail integration for email handling and drafting
- Browser interaction for web-related tasks
- File system operations (create, update, delete)

## Available Tools

### Agency Communication Tools
- **SendMessage**: Synchronous communication with agencies/agents for quick tasks
  - Direct interaction with immediate response
  - Suitable for simple, fast-completing tasks

- **SendMessageAsync**: Asynchronous task delegation
  - Initiates long-running tasks without waiting
  - Returns immediately to allow other operations

- **GetResponse**: Task status and response retrieval
  - Checks completion status of async tasks
  - Retrieves agent responses when tasks complete

### Google Workspace Integration
- **FetchDailyMeetingSchedule**: Fetches and formats the user's daily meeting schedule from Google Calendar
- **GetGmailSummary**: Provides a concise summary of unread Gmail messages from the past 48 hours
- **DraftGmail**: Composes email drafts, either as a reply to an email from GetGmailSummary, or as a new message

### System Tools
- **GetScreenDescription**: Captures and analyzes the current screen content for the assistant
- **FileOps**:
   - **CreateFile**: Generates new files with user-specified content
   - **UpdateFile**: Modifies existing files with new content
   - **DeleteFile**: Removes specified files from the system
- **OpenBrowser**: Launches a web browser with a given URL
- **GetCurrentDateTime**: Retrieves and reports the current date and time

## Setup

### MacOS Installation

1. Install [Python 3.12](https://www.python.org/downloads/macos/).
2. Install [uv](https://docs.astral.sh/uv/), a modern Python package manager
3. Clone this repository to your local machine
4. Create a local environment file `.env` based on `.env.sample`
5. Customize `personalization.json` and `config.py` to your preferences
6. Install the required audio library: `brew install portaudio`
7. Install project dependencies: `uv sync`
8. Launch the assistant: `uv run main`

### Google Cloud API Configuration

To enable Google Cloud API integration, follow these steps:

1. Create OAuth 2.0 Client IDs in the Google Cloud Console
2. Place the `credentials.json` file in the project's root directory
3. Configure `http://localhost:8080/` as an Authorized Redirect URI in your Google Cloud project settings
4. Set the OAuth consent screen to "Internal" user type
5. Enable the following APIs and scopes in your Google Cloud project:
   - Gmail API
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.compose`
     - `https://www.googleapis.com/auth/gmail.modify`
   - Google Calendar API
     - `https://www.googleapis.com/auth/calendar.readonly`

## Configuration

The project relies on environment variables and a `personalization.json` file for configuration. Ensure you have set up:

- `OPENAI_API_KEY`: Your personal OpenAI API key
- `PERSONALIZATION_FILE`: Path to your customized personalization JSON file
- `SCRATCH_PAD_DIR`: Directory for temporary file storage

## Usage

After launching the assistant, interact using voice commands. Example interactions:

1. "What do I have on my schedule for today? Tell me only most important meetings."
2. "Do I have any important emails?"
3. "Open ChatGPT in my browser."
4. "Create a new file named user_data.txt with some example content."
5. "Update the user_data.txt file by adding more information."
6. "Delete the user_data.txt file."
7. "Ask the research team to write a detailed market analysis report."
8. "Check if the research team has completed the market analysis report."

## Code Structure

### Core Components

- `main.py`: Application entry point
- `agencies/`: Agency-Swarm teams of specialized agents
- `tools/`: Standalone tools for various functions
- `config.py`: Configuration settings and environment variable management
- `visual_interface.py`: Visual interface for audio energy visualization
- `websocket_handler.py`: WebSocket event and message processing

### Key Features

1. **Asynchronous WebSocket Communication**:
   Utilizes `websockets` for asynchronous connection with the OpenAI Realtime API

2. **Audio Input/Output Handling**:
   Manages real-time audio capture and playback with PCM16 format support and VAD (Voice Activity Detection)

3. **Function Execution**:
   Standalone tools in `tools/` are invoked by the AI assistant based on user requests

4. **Structured Output Processing**:
   OpenAI's Structured Outputs are used to generate precise, structured responses

5. **Visual Interface**:
   PyGame-based interface provides real-time visualization of audio volume

## Extending Functionality

### Adding Standalone Tools

Standalone tools are independent functions not associated with specific agents or agencies.

To add a new standalone tool:
1. Create a new file in the `tools/` directory
2. Implement the `run` method using async syntax, utilizing `asyncio.to_thread` for blocking operations
3. Install any necessary dependencies: `uv add <package_name>`

### Adding New Agencies

Agencies are Agency-Swarm style teams of specialized agents working together on complex tasks.

To add a new agency:
1. Drag-and-drop your agency folder into the `agencies/` directory
2. Set `async_mode="threading"` in agency configuration to enable async messaging (SendMessageAsync and GetResponse)
3. Install any required dependencies: `uv add <package_name>`

## Development Roadmap

- [x] Implement standalone tools
- [x] Complete agency integration
- [ ] Develop interruption handling for smoother conversations
- [ ] Implement transcript logging for conversation tracking
- [ ] Convert `personalization.json` to a Pydantic model for improved type safety
- [ ] Enable parallel execution of tools for increased efficiency
- [ ] Resolve audio cutoff issues at the end of responses

## Additional Resources

- [OpenAI Realtime API Documentation](https://platform.openai.com/docs/guides/realtime)
- [OpenAI Structured Outputs Guide](https://platform.openai.com/docs/guides/structured-outputs)
- [WebSockets Library for Python](https://websockets.readthedocs.io/)
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/docs/)
- [Pygame Documentation](https://www.pygame.org/docs/)
