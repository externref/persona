# Persona - Behavioral Biometrics Authentication System

A modern continuous authentication system that uses behavioral biometrics (mouse movement patterns) to verify user identity in real-time.

## Overview

Persona is a full-stack application that captures and analyzes user behavioral biometrics during the signup process, then continuously monitors user behavior to detect anomalies that might indicate account compromise or unauthorized access.

## Features

- **Biometric Signature Capture**: Users draw a signature-like pattern during signup to establish their baseline behavior
- **Continuous Monitoring**: Real-time tracking of mouse movements and events while the user is active
- **Anomaly Detection**: Z-score based statistical analysis to detect deviations from baseline behavior
- **Modern UI**: Beautiful, responsive interface with gradient themes and smooth animations
- **Secure Authentication**: Password-protected accounts with localStorage-based session management
- **Real-time Feedback**: Live progress indicators and security status updates

## Tech Stack

### Frontend
- **Framework**: SvelteKit 5 with TypeScript
- **Styling**: Modern CSS with gradient backgrounds and animations
- **State Management**: Svelte 5 `$state` and `$effect` reactivity
- **Build Tool**: Vite

### Backend
- **API Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Database**: MongoDB (local instance)
- **Data Processing**: NumPy for statistical calculations
- **Async**: Motor for non-blocking MongoDB operations

### Database Schema

```
persona (database)
├── biometric_templates (collection)
│   ├── user_id (string, indexed)
│   ├── statistical_profile (object)
│   │   ├── mouse_velocity (object)
│   │   │   ├── mean, std_dev, count, weight
│   │   ├── mouse_acceleration (object)
│   │   │   ├── mean, std_dev, count, weight
│   │   ├── key_dwell (object)
│   │   │   ├── mean, std_dev, count, weight
│   │   └── key_flight (object)
│   │       ├── mean, std_dev, count, weight
│   └── timestamp (date)
│
├── auth (collection)
│   ├── username (string, indexed)
│   ├── password (string, hashed)
│   └── createdAt (date)
│
└── biometric_anamolies (collection)
    ├── user_id (string)
    ├── anomaly_score (float)
    ├── timestamp (date)
    └── details (object)
```

## Project Structure

```
persona/
├── main.py                          # Entry point for backend
├── persona/
│   ├── sever.py                    # FastAPI server and endpoints
│   ├── biometrics.py               # Z-score anomaly detection algorithm
│   ├── database.py                 # MongoDB operations
│   └── types.py                    # Data type definitions
├── persona-frontend/               # SvelteKit frontend
│   ├── src/
│   │   ├── routes/
│   │   │   ├── signup/             # User registration & biometric capture
│   │   │   ├── securedPage/        # Continuous monitoring dashboard
│   │   │   └── api/
│   │   │       ├── createUser/     # User registration API
│   │   │       └── track/          # Anomaly detection API
│   │   └── lib/
│   │       └── index.ts            # TypeScript type definitions
│   └── vite.config.ts              # Vite configuration
└── README2.md                       # This file
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (local instance on `127.0.0.1:27017`)

### Backend Setup

1. **Create and activate virtual environment**
   ```bash
   cd persona
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

2. **Install dependencies**
   ```bash
   pip install fastapi uvicorn motor pymongo numpy
   ```

3. **Start MongoDB**
   ```bash
   mongod
   ```

4. **Run the backend**
   ```bash
   python main.py
   ```
   Server runs on `http://127.0.0.1:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd persona-frontend
   ```

2. **Install dependencies**
   ```bash
   yarn install
   # or
   npm install
   ```

3. **Start development server**
   ```bash
   yarn dev
   # or
   npm run dev
   ```
   Server runs on `http://localhost:5173`

## Usage

### 1. Sign Up
- Navigate to the signup page
- Enter a username and password
- Draw a biometric signature (line from left to right)
- Coverage must be at least 70% of the canvas width
- Successfully signed-up users are redirected to the secured page

### 2. Continuous Monitoring
- On the secured page, your mouse movements are automatically tracked
- Every 10 seconds, movement data is analyzed
- Your current behavior is compared against your baseline signature
- Anomalies are flagged if behavior deviates significantly

### 3. Logout
- Click the "Logout" button to clear your session
- You'll be redirected to the signup page

## API Endpoints

### Backend (Python FastAPI)

#### POST `/api/v0/init`
Create user profile during signup.

**Request Body**:
```json
{
  "user_id": "string",
  "session_id": "string (UUID)",
  "origin": "string (URL)",
  "is_signup": true,
  "metadata": {
    "sw": number,          // screen width
    "sh": number,          // screen height
    "dpr": number,         // device pixel ratio
    "plt": "string"        // platform
  },
  "events": [
    {
      "t": number,        // timestamp
      "type": "m|d|u",    // move, down, up
      "x": number,        // normalized X (0-1)
      "y": number         // normalized Y (0-1)
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Profile created successfully"
}
```

#### POST `/api/v0/compare`
Compare current behavior against baseline profile.

**Request Body**: Same format as `/api/v0/init` but with `is_signup: false`

**Response**:
```json
{
  "anomaly": boolean,
  "score": float (0-1),
  "details": {
    "feature_name": {
      "db_mean": float,
      "db_std": float,
      "rec_mean": float,
      "z_score": float,
      "is_anomaly": boolean
    }
  }
}
```

### Frontend (SvelteKit)

#### POST `/api/createUser`
Register new user and create biometric profile.

**Request Body**:
```json
{
  "userId": "string",
  "userPasswd": "string",
  "payload": { /* BiometricPayload */ }
}
```

#### POST `/api/track`
Submit tracking data for anomaly detection.

**Request Body**: Same as `/api/v0/compare`

**Response**: `true` (anomaly) or `false` (normal)

## Biometric Features Captured

The system tracks and analyzes:

1. **Mouse Velocity**: Speed of mouse movement
2. **Mouse Acceleration**: Change in speed over time
3. **Keyboard Dwell Time**: How long keys are held down
4. **Keyboard Flight Time**: Time between key releases and presses

For each feature, the system calculates:
- Mean value
- Standard deviation
- Count of samples
- Statistical weight

## Anomaly Detection Algorithm

Persona uses **Z-score based anomaly detection** to compare incoming behavioral samples against stored profiles:

```
Z-score = |received_mean - stored_mean| / stored_std_dev
Anomaly if: average_z_score > threshold (2.5) OR any_feature_z_score > threshold
```

The algorithm produces a normalized score (0-1) using sigmoid normalization for easy interpretation.

## Key Features & Implementation

### Event Throttling
Events are captured at most once every 50ms to balance data richness with network efficiency.

### Coordinate Normalization
All coordinates are normalized to 0-1 range during both signup and tracking to ensure consistency across different screen sizes.

### State Management
- Uses Svelte 5's `$state` for reactive state
- Uses `$effect` for reactive side effects
- Proper cleanup of event listeners when component unmounts

### Storage
- User credentials stored in MongoDB `auth` collection
- Biometric profiles stored in `biometric_templates` collection
- User session stored in browser localStorage as `persona_user`

## Security Considerations

⚠️ **This is a demo/educational project. For production use, consider:**

1. Hash passwords using bcrypt or similar
2. Use JWT tokens instead of localStorage
3. Implement HTTPS/TLS for all communications
4. Add rate limiting on API endpoints
5. Validate and sanitize all user inputs
6. Implement proper error handling without exposing system details
7. Use environment variables for sensitive configuration
8. Add logging and monitoring
9. Implement database backups
10. Add CORS configuration

## Troubleshooting

### Canvas drawing not appearing
- Ensure canvas dimensions are set in HTML attributes, not CSS
- Check browser console for JavaScript errors

### MongoDB connection errors
- Verify MongoDB is running: `mongod`
- Check connection string in `sever.py`

### Vite dev server not starting
- Clear node_modules and reinstall: `rm -r node_modules && yarn install`
- Check for port conflicts (default: 5173)

### Events not being tracked
- Verify `isAuthenticated` state is true
- Check browser console for event listener errors
- Ensure mouse events are firing properly

## Performance Notes

- Event throttling: 50ms minimum between captures
- Payload submission: Every 10 seconds
- Minimum events per payload: 10
- Statistical computation: Real-time in backend

## Contributing

This is an educational project demonstrating behavioral biometrics. Feel free to extend with:
- Keyboard pattern recognition
- Touch gesture tracking
- Eye tracking integration
- Machine learning models
- Advanced fraud detection

## License

MIT - Feel free to use for educational and research purposes.

## Author

Created as a demonstration of behavioral biometrics authentication using SvelteKit and FastAPI.

---

**Last Updated**: April 25, 2026
