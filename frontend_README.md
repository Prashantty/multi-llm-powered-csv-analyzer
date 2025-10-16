# CSV Q&A Maker - Frontend

A simple, modern web interface for uploading CSV files and asking questions about your data using AI.

## Features

- **Drag & Drop File Upload**: Easily upload CSV files by dragging and dropping or clicking to select
- **Real-time Validation**: Validates file type (CSV only) and size (16MB limit)
- **Question Input**: Large text area for asking detailed questions about your data
- **Modern UI**: Clean, responsive design that works on desktop and mobile
- **Loading States**: Visual feedback during processing
- **Error Handling**: Clear error messages for various scenarios
- **Success Display**: Formatted results showing your question, answer, and data info

## How to Use

1. **Start the Backend**: Make sure your Flask backend is running on `localhost:5000`
   ```bash
   python app.py
   ```

2. **Open the Frontend**: Open `index.html` in your web browser

3. **Upload CSV File**: 
   - Click the upload area or drag and drop your CSV file
   - File must be in CSV format and under 16MB

4. **Ask Your Question**: 
   - Type your question in the text area
   - Examples:
     - "What is the total sales for last month?"
     - "Show me the top 5 customers by revenue"
     - "What trends do you see in the data?"

5. **Get Results**: Click "Analyze Data" and wait for the AI response

## Technical Details

- **Pure HTML/CSS/JS**: No frameworks required
- **Modern ES6**: Uses modern JavaScript features like classes and async/await
- **Responsive Design**: Works on mobile and desktop
- **CORS Enabled**: Communicates with Flask backend on localhost:5000
- **File Validation**: Client-side validation for better user experience

## API Integration

The frontend communicates with these backend endpoints:

- `POST /chat`: Uploads file and question, returns AI analysis
- `GET /health`: Health check (used for connection testing)
- `GET /upload-info`: File upload limitations and info

## Browser Compatibility

Works with all modern browsers that support:
- ES6 classes
- Fetch API
- FormData
- File API
- CSS Grid/Flexbox

## Styling

The interface features:
- Gradient backgrounds and modern design
- Smooth transitions and hover effects
- Loading animations
- Responsive layout
- Color-coded success/error states
- Clean typography using system fonts