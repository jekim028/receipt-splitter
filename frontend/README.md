# Receipt Splitter Frontend

React frontend for the AI-powered receipt splitter app.

## Features

- 📸 Receipt image upload with drag-and-drop
- 🤖 Conversational AI interface for splitting bills
- 🧾 Thermal receipt-style display with real-time highlighting
- 👥 Per-person breakdown and totals
- 📱 Responsive design (mobile + desktop)

## Tech Stack

- **React** - UI framework
- **Vite** - Build tool
- **Axios** - API client
- **CSS** - Styling (no framework needed!)

## Getting Started

### Prerequisites

- Node.js 20+ (you have v20.2.0)
- Backend API running on `http://localhost:8000`

### Installation

```bash
npm install
```

### Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

The default configuration points to `http://localhost:8000` for the backend API.

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Build

Build for production:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── UploadFlow/         # Receipt upload + people input
│   ├── ReceiptDisplay/     # Thermal receipt display
│   ├── ChatInterface/      # Chat UI components
│   └── AssignmentSummary/  # Per-person breakdown
├── hooks/
│   ├── useConversation.js  # Message management
│   └── useAssignmentState.js # Assignment state with polling
├── utils/
│   └── api.js              # API client
├── App.jsx                 # Main app component
├── App.css                 # App-level styles
└── index.css               # Global styles
```

## Workflow

1. **Upload** - User uploads a receipt image
2. **Processing** - TabScanner parses the receipt (polling)
3. **People** - User enters names of people splitting the bill
4. **Chat** - User chats with AI to assign items
5. **Confirm** - User confirms the split

## API Integration

The frontend communicates with the FastAPI backend via:

- `POST /api/receipt/upload` - Upload receipt
- `GET /api/receipt/result/{token}` - Poll for results
- `POST /api/conversation/start` - Start splitting conversation
- `POST /api/conversation/{id}/message` - Send message to AI
- `GET /api/conversation/{id}/state` - Get assignment state (polled every 2s)
- `POST /api/conversation/{id}/confirm` - Finalize split

## Key Features

### Real-time State Polling

The `useAssignmentState` hook polls the backend every 2 seconds to sync assignment changes.

### Receipt Highlighting

Items mentioned by the AI are highlighted with a pulse animation to help users visually track what's being discussed.

### Thermal Receipt Styling

The receipt display mimics a thermal paper receipt with:
- Monospace font (Courier New)
- Centered layout
- Dashed dividers
- Color-coded assignments

### Conversational UX

Users can say things like:
- "I had the burger"
- "Split the appetizers between everyone"
- "Sarah and I are sharing the pizza"

The AI agent handles the rest!

## Development Notes

- Uses Vite proxy to avoid CORS issues during development
- State management via React hooks (no Redux needed)
- Polling-based updates (WebSockets can be added later)
- All styling done with vanilla CSS (no Tailwind/Material-UI)

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Venmo link generation
- [ ] Receipt manual editing
- [ ] Dark mode
- [ ] PWA support
