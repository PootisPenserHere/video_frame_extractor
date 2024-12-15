# Video Frame Extractor

A web application that allows users to upload videos and extract frames from specific time ranges. The application provides a user-friendly interface to:
- Upload videos
- Preview uploaded videos
- Select specific time ranges for frame extraction
- View extracted frames in a responsive gallery
- Download all extracted frames as a ZIP file

The application features a dark/light mode toggle and is fully responsive, working on both desktop and mobile devices.

## Technical Stack

- Frontend: Vanilla JavaScript with libraries loaded from CDN:
  - Bulma CSS for styling
  - Font Awesome for icons
  - Flatpickr for time selection
- Backend: Flask (Python)
- Video Processing: FFmpeg

## Running the Project

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone git@github.com:PootisPenserHere/video_frame_extractor.git
cd video-frame-extractor
```

2. Build and run using docker-compose:
```bash
docker-compose up --build
```

3. Access the application at `http://localhost:5000`

### Using Virtual Environment

1. Clone the repository:
```bash
git clone git@github.com:PootisPenserHere/video_frame_extractor.git
cd video-frame-extractor
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure FFmpeg is installed on your system:
- Ubuntu/Debian: `sudo apt-get install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)

5. Run the application:
```bash
python app.py
```

6. Access the application at `http://localhost:5000`

## API Endpoints

### Main Interface
```
GET /
Returns the main web interface
```

### Upload Video
```
POST /upload
Content-Type: multipart/form-data

Parameters:
- video: Video file (form data)

Response:
{
    "uuid": "14802a8c-c60c-42e8-873b-4f16b83f3aa8",
    "filename": "sample_video.mp4"
}
```

### Serve Video
```
GET /video/<upload_uuid>/<filename>
Parameters:
- upload_uuid: UUID of the uploaded video
- filename: Name of the video file

Response:
Binary video data with appropriate mime type
```

### Extract Frames
```
POST /extract-frames
Content-Type: application/json

Parameters:
{
    "upload_uuid": "14802a8c-c60c-42e8-873b-4f16b83f3aa8",
    "start_time": "00:00:10",
    "end_time": "00:00:15"
}

Response:
{
    "status": "started"
}
```

### Get Extraction Progress
```
GET /<upload_uuid>/progress

Response:
{
    "progress": 75,
    "total_frames": 5,
    "available_frames": [1, 2, 3]
}
```

### Get Single Frame
```
GET /video/<upload_uuid>/frame/<frame_order>
Parameters:
- upload_uuid: UUID of the uploaded video
- frame_order: Numerical order of the frame

Response:
Binary image data (JPEG)
```

### Download Frames
```
GET /<upload_uuid>/frames

Response:
Binary ZIP file containing all extracted frames
```

## File Structure
```
tmp/
└── uploads/
    └── <upload_uuid>/
        ├── video_file.mp4
        └── frames/
            ├── frame_1_of_5_00_00_10.jpg
            ├── frame_2_of_5_00_00_11.jpg
            └── ...
```

## Features

- Async video upload with progress tracking
- Real-time frame extraction progress
- Interactive video player with current time display
- Time range selection with validation
- Responsive frame gallery (up to 20 frames)
- Frame preview modal
- Automatic frame distribution for longer videos
- Downloadable ZIP of all extracted frames
- Dark/Light mode toggle
- Mobile-responsive design

## Notes

- Frames are extracted at a rate of one frame per second within the specified time range
- The gallery shows up to 20 frames, evenly distributed across the extraction range
- For videos longer than 20 seconds, frames are automatically distributed to show a representative sample
- All extracted frames are included in the ZIP download, regardless of gallery display
- Temporary files are stored in the `tmp/uploads` directory
- Previous frames are automatically cleaned up when starting a new extraction
