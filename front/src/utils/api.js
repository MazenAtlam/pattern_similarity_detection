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