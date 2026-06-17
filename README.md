# VideoStream - Futuristic Video Platform

A modern, futuristic video streaming platform built with Django.

## Features

### Futuristic Design
- Glassmorphism UI with backdrop blur effects
- Animated gradients and glowing elements
- Custom animations and transitions
- Responsive design for all devices

### Video Management
- Add videos from YouTube URLs
- Auto-fetch video metadata (title, description)
- Stream videos in HD
- Download as MP3 or MP4
- Delete videos with confirmation

### Search & Navigation
- Search videos by title
- Browse video library with pagination
- Quick access to all features

## Technology Stack

- **Backend**: Django 6.0.6
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Icons**: Font Awesome 6
- **Dependencies**: requests

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd videosite
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

1. Visit `http://localhost:8000` to browse the video library
2. Click "Add Video" to add new videos
3. Click "Watch" on any video to stream it
4. Use the search bar to find videos by title

## Development

The site includes several futuristic features:

### Glassmorphism UI
- Semi-transparent backgrounds with backdrop blur
- Border effects with subtle glow
- Smooth transitions and animations

### Dynamic Styling
- Custom CSS variables for color scheme
- Responsive grid layouts
- Hover effects and micro-interactions

### Video Player Enhancements
- Auto-play with controls
- HD streaming support
- Keyboard shortcuts (press 'k' to play/pause)

## License

This project is open source and available under the MIT License.
