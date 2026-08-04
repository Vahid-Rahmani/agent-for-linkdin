# LinkedIn AI Agent

Automate your LinkedIn presence with AI-powered content generation, comment replies, message responses, and activity reporting.

## Features

- **LinkedIn Authentication** - Secure session persistence (login once, use forever)
- **Profile Monitoring** - Track profile views, search appearances, connections
- **Post Tracking** - Monitor likes, comments, shares on your posts
- **Comment Detection** - Automatically detect new comments on your posts
- **Message Monitoring** - Check for new messages in your inbox
- **AI Post Generation** - Generate professional LinkedIn posts using Google Gemini AI
- **Post Improvement** - Enhance existing posts for better engagement
- **Auto Replies** - AI-draft replies to comments and messages
- **Activity Reports** - Generate detailed reports on your LinkedIn activity

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.14 |
| Browser Automation | Playwright |
| AI Provider | Google Gemini (free tier) |
| Database | SQLite |
| CLI | Click + Rich |

## Installation

### 1. Clone the repository

```bash
git clone git@github.com:Vahid-Rahmani/agent-for-linkdin.git
cd agent-for-linkdin
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure API key

Edit the `.env` file and add your Google Gemini API key:

```env
GOOGLE_GEMINI_API_KEY=your_api_key_here
LINKEDIN_PROFILE_URL=https://www.linkedin.com/in/vahid-rahmani-699944417
```

> **Get a free API key:** Go to [Google AI Studio](https://aistudio.google.com/apikey), sign in with your Google account, and create an API key. No credit card required. Free tier includes 500+ requests/day.

### 4. First-time login

```bash
python main.py login
```

A browser window will open. Log in to LinkedIn manually. After logging in, press Enter in the terminal. Your session will be saved for future use.

## Usage

### CLI Commands

```bash
# First-time login
python main.py login

# Check LinkedIn activity (profile, posts, comments, messages)
python main.py monitor

# Generate and publish a LinkedIn post
python main.py post
python main.py post "AI and Machine Learning"

# Reply to pending comments and messages
python main.py reply

# Improve an existing post
python cli.py improve <post_url>

# Generate activity report
python main.py report

# Run full automation cycle (monitor -> reply -> report)
python main.py run
```

### Using Click CLI

```bash
# Alternative CLI interface
python cli.py login
python cli.py monitor
python cli.py post "topic" --auto
python cli.py reply --auto
python cli.py improve <url> --focus engagement
python cli.py report
python cli.py run --auto
```

## Project Structure

```
agent/
├── config/
│   ├── settings.py          # API keys, credentials, config
│   └── constants.py         # LinkedIn selectors, URLs
├── auth/
│   ├── session_manager.py   # Playwright session persistence
│   └── login_handler.py     # LinkedIn login flow
├── monitor/
│   ├── profile_monitor.py   # Profile views, connections
│   ├── post_monitor.py      # Post metrics tracking
│   ├── comment_monitor.py   # New comments detection
│   └── message_monitor.py   # New messages detection
├── models/
│   ├── comment.py
│   ├── message.py
│   └── post.py
├── database/
│   └── local_db.py          # SQLite storage
├── ai/
│   ├── client.py            # Google Gemini API wrapper
│   ├── post_generator.py    # Generate LinkedIn posts
│   ├── post_improver.py     # Improve existing posts
│   ├── reply_drafter.py     # Draft replies
│   └── prompts.py           # AI prompts
├── automation/
│   ├── publisher.py         # Publish posts
│   ├── comment_responder.py # Reply to comments
│   ├── message_responder.py # Reply to messages
│   └── post_upgrader.py     # Edit existing posts
├── reports/
│   └── report_generator.py  # Activity reports
├── cli.py                   # Click CLI interface
├── main.py                  # Main entry point
├── requirements.txt
├── .env                     # API keys (gitignored)
└── .gitignore
```

## Development Plan

### Phase 1: Setup and LinkedIn Authentication
- [x] Install Python and Playwright
- [x] Session storage with user_data_dir (bypass CAPTCHAs/2FA)
- [x] Manual login test

### Phase 2: Code and Project Monitoring Module
- [x] Profile monitor (views, search appearances, connections)
- [x] Post monitor (likes, comments, shares)
- [x] Comment monitor (detect new comments)
- [x] Message monitor (detect new messages)
- [x] SQLite database for local storage

### Phase 3: AI Brain (Professional Content Generation)
- [x] Google Gemini API integration (free tier, 500 req/day)
- [x] Post generator with engineered prompts
- [x] Post improver (engagement, algorithm optimization)
- [x] Reply drafter for comments and messages
- [x] Human-in-the-loop approval step

### Phase 4: Publishing and Interaction Automation
- [x] Playwright post publishing
- [x] Comment auto-reply with AI drafts
- [x] Message auto-reply with AI drafts
- [x] Post editing/upgrading

### Phase 5: Final Integration and Orchestration
- [x] CLI tool with multiple commands
- [x] Full automation cycle (`python main.py run`)
- [x] Activity report generation

## Safety Features

- **Session Persistence** - Login once, reuse cookies (avoids repeated logins)
- **Human-in-the-Loop** - Approve AI drafts before sending
- **Rate Limiting** - Max 10 comments/hour, 20 messages/hour
- **Random Delays** - 2-5 second delays between actions
- **Anti-Detection** - Custom user agent, disabled automation flags
- **Local Database** - All data stored locally (no external servers)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_GEMINI_API_KEY` | Your Google Gemini API key | (required) |
| `LINKEDIN_PROFILE_URL` | Your LinkedIn profile URL | Vahid Rahmani's profile |

## License

MIT License

## Author

**Vahid Rahmani** - [LinkedIn](https://www.linkedin.com/in/vahid-rahmani-699944417)
