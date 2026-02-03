// API utility for fetching data

const API_BASE_URL = 'http://localhost:5000/api/v1'; // Update with your backend URL

/**
 * Converts audio blob to base64 string
 * @param {Blob|File} audioBlob - The audio file to convert
 * @returns {Promise<string>} - Base64 encoded string
 */
const blobToBase64 = (audioBlob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(audioBlob);
    reader.onloadend = () => {
      // Extract base64 data (remove data URL prefix)
      const base64String = reader.result.split(',')[1];
      resolve(base64String);
    };
    reader.onerror = reject;
  });
};

/**
 * Detects matching songs from hummed audio
 * @param {Blob|File} audioFile - The audio file containing hummed melody
 * @returns {Promise<Object>} - The JSON response from the API
 */
export const detectSong = async (audioFile) => {
  try {
    // Convert audio file to base64
    const base64Audio = await blobToBase64(audioFile);
    
    // Determine audio format from MIME type
    let audioFormat;
    if (audioFile.type.includes('wav')) {
      audioFormat = 'wav';
    } else if (audioFile.type.includes('mp3')) {
      audioFormat = 'mp3';
    } else if (audioFile.type.includes('m4a')) {
      audioFormat = 'm4a';
    } else if (audioFile.type.includes('ogg')) {
      audioFormat = 'ogg';
    } else {
      audioFormat = 'wav'; // Default
    }

    const payload = {
      audio_format: audioFormat,
      sample_rate: 44100, // Standard sample rate
      audio_data: base64Audio
    };

    const response = await fetch(`${API_BASE_URL}/songs/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Song Detection API Error:', error);
    throw error;
  }
};

/**
 * Sends a request to the Pass Sequence Detector endpoint.
 * @param {Object} payload - The data to send (e.g., { sequence_path: "..." } or metadata).
 * @returns {Promise<Object>} - The JSON response from the API.
 */
export const detectPassSequence = async (payload) => {
  try {
    const response = await fetch(`${API_BASE_URL}/pass_sequences/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

/**
 * Detects pass sequence by metadata
 * @param {string[]} players - Array of player names
 * @param {string} stage - Match stage
 * @param {string} group - Group name
 * @param {string} date - Match date
 * @param {string} match - Match teams
 * @returns {Promise<Object>} - API response
 */
export const detectPassSequenceByMetadata = async (players, stage, group, date, match) => {
  const payload = {
    players,
    stage,
    group,
    date,
    match
  };
  return detectPassSequence(payload);
};

/**
 * Detects pass sequence by ID
 * @param {string} sequenceId - The sequence ID
 * @returns {Promise<Object>} - API response
 */
export const detectPassSequenceById = async (sequenceId) => {
  const payload = {
    sequence_id: sequenceId
  };
  return detectPassSequence(payload);
};

/**
 * Submits contact form data
 * @param {Object} formData - Contact form data
 * @returns {Promise<Object>} - API response
 */
export const submitContactForm = async (formData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/contact/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Contact Form API Error:', error);
    throw error;
  }
};

// Mock API functions for development (comment out when using real API)
export const mockDetectSong = async (file) => {
  console.log("Mock API: Analyzing audio file:", file);
  
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        status: "success",
        matched_songs_found: 5,
        results: [
          {
            song_name: "Shape of You",
            artist: "Ed Sheeran",
            similarity_index: 0.89,
            file_url: "/songs_files/shape_of_you.mp3"
          },
          {
            song_name: "Blinding Lights",
            artist: "The Weeknd",
            similarity_index: 0.72,
            file_url: "/songs_files/blinding_lights.mp3"
          },
          {
            song_name: "Bad Guy",
            artist: "Billie Eilish",
            similarity_index: 0.65,
            file_url: "/songs_files/bad_guy.mp3"
          },
          {
            song_name: "Uptown Funk",
            artist: "Mark Ronson ft. Bruno Mars",
            similarity_index: 0.58,
            file_url: "/songs_files/uptown_funk.mp3"
          },
          {
            song_name: "Levitating",
            artist: "Dua Lipa",
            similarity_index: 0.52,
            file_url: "/songs_files/levitating.mp3"
          }
        ]
      });
    }, 2000);
  });
};