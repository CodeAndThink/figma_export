# Figma Export Pro

A tool for automatically downloading and splitting Figma data into individual screens (frames), featuring an intuitive web interface for management and previewing.

## 🚀 Key Features

- **Figma Data Fetching**: Utilizes the Figma API to retrieve detailed file information.
- **Automatic Screen Splitting**: Categorizes and stores JSON data and preview images for each screen independently.
- **Web Interface**: Modern, user-friendly UI for executing exports and viewing the list of downloaded screens.
- **Real-time Feedback**: View live export process logs directly in your browser.

## 🛠 System Requirements

- Python 3.8 or higher.
- [Figma Personal Access Token](https://help.figma.com/hc/en-us/articles/360040145913-Authenticate-with-the-Figma-API#Personal_Access_Tokens).

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd figma_export
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # Or: .venv\Scripts\activate  # On Windows
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🖥 Usage Instructions

1. **Launch the application:**
   ```bash
   python main.py
   ```
   The application will automatically start the server and open your browser at `http://127.0.0.1:8001`.

2. **Perform Export:**
   - Enter your **Figma Personal Access Token**.
   - Enter your **Figma File Link** (e.g., `https://www.figma.com/file/ABC123XYZ/My-Project`).
   - Click the **Export** button. The process will complete in a few seconds depending on the file size.

3. **View Results:**
   - Once finished, the list of screens will appear in the **Screens List** section.
   - You can click on each screen to view its preview image and detailed JSON data.

## 📁 Directory Structure

- `main.py`: Entry point of the application, handles opening the browser and running the server.
- `server.py`: Handles backend logic (API) using FastAPI.
- `funcs/`: Contains core processing functions (data fetching, screen splitting).
- `web/`: Contains frontend source code (HTML, CSS, JS).
- `screens/`: Directory for exported results (automatically created).

## 📝 Notes

- Ensure you have a stable internet connection for the application to communicate with the Figma API.
- The `screens/` directory is added to `.gitignore` to avoid pushing personal data to the repository.

---
*Enjoy your experience with Figma Export Pro!*
