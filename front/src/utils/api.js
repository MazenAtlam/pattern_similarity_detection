// API utility for fetching data

const API_BASE_URL = 'http://localhost:5000/api/v1'; // Update with your backend URL



/**
 * Detects matching songs from hummed audio
 * @param {Blob|File} audioFile - The audio file containing hummed melody
 * @returns {Promise<Object>} - The JSON response from the API
 */
export const detectSong = async (audioFile) => {
  try {
    const formData = new FormData();
    // Check if audioFile is a File (has name) or just a Blob
    const fileName = audioFile.name || 'recording.wav';
    formData.append('audio_data', audioFile, fileName);
    // Optional: Add version if needed, or other metadata
    // formData.append('version', 'v0'); 

    const response = await fetch(`${API_BASE_URL}/songs/detect`, {
      method: 'POST',
      // Content-Type header MUST NOT be set manually for FormData; 
      // the browser sets it with the correct boundary.
      body: formData,
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
    console.error('API Error (Count):', error);
    throw error;
  }
}

/**
 * Sends a request to count the number of sequences in a specific file.
 * @param {string} sequencePath - The path to the sequence file.
 * @returns {Promise<Object>} - The JSON response containing sequence_count.
 */
export const getSequenceCount = async (sequencePath, selectedMatch) => {
  try {
    const response = await fetch(`${API_BASE_URL}/pass_sequences/count`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ sequence_path: sequencePath, match_id: selectedMatch }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error (Count):', error);
    throw error;
  }
};