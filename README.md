# 📚 Resource Saver - Cross-Browser Extension

A browser extension that allows users to save the current tab's URL (articles, YouTube videos, or tools) to a database. Built with WXT for cross-browser compatibility (Manifest V3).

## 🛠 Tech Stack

- **Extension Framework**: [WXT](https://wxt.dev) (Manifest V3 compliant)
- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Python FastAPI
- **Database**: SQLite (easily upgradable to PostgreSQL)

## 📁 Project Structure

```
resource-saver/
├── backend/
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Python dependencies
├── entrypoints/
│   └── popup/
│       ├── App.tsx          # Main React component
│       ├── index.html       # Popup HTML
│       ├── main.tsx         # React entry point
│       └── style.css        # Tailwind CSS styles
├── wxt.config.ts            # WXT configuration with permissions
├── tailwind.config.js       # Tailwind CSS config
└── postcss.config.js        # PostCSS config
```

## 🚀 Getting Started

### 1. Install Extension Dependencies

```bash
cd resource-saver
npm install
```

### 2. Start the Backend Server

```bash
# Create a virtual environment (recommended)
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The API will be available at `http://localhost:8000` with docs at `http://localhost:8000/docs`.

### 3. Run the Extension in Development Mode

```bash
# In a new terminal, from the resource-saver directory
npm run dev           # For Chrome/Edge/Brave
npm run dev:firefox   # For Firefox
```

This will open a browser with the extension loaded in development mode with hot reload.

### 4. Build for Production

```bash
npm run build           # For Chrome/Edge/Brave
npm run build:firefox   # For Firefox

# Create distributable zip files
npm run zip             # For Chrome/Edge/Brave
npm run zip:firefox     # For Firefox
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/save` | Save a new resource |
| GET | `/resources` | Get all saved resources |
| DELETE | `/resources/{id}` | Delete a resource |

### POST /save Request Body

```json
{
  "title": "Article Title",
  "url": "https://example.com/article",
  "type": "article" // or "youtube" or "tool"
}
```

## 🔐 Permissions

The extension uses minimal permissions:

- `activeTab`: Access to the currently active tab's URL and title (only when popup is open)

This approach avoids triggering broad warning messages during installation.

## 📱 Responsive Design

The popup is designed to work at:
- Standard extension width (~350px)
- Scales gracefully for mobile browsers

## 🔄 Upgrading to PostgreSQL

To switch from SQLite to PostgreSQL, update `backend/main.py`:

1. Install `asyncpg` and `databases`:
   ```bash
   pip install asyncpg databases[postgresql]
   ```

2. Replace SQLite connection with PostgreSQL:
   ```python
   DATABASE_URL = "postgresql://user:password@localhost/resource_saver"
   ```

## 📄 License

MIT
