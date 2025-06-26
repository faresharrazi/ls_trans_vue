<template>
  <div class="transcription-app">
    <div class="main-flex">
      <div class="left-panel">
        <!-- API Config Card -->
        <div class="card config-card">
          <h3>🔑 API Configuration</h3>
          <div class="input-group">
            <label for="apiKey">ElevenLabs API Key</label>
            <input
              id="apiKey"
              v-model="apiKey"
              type="password"
              placeholder="Enter your ElevenLabs API key"
              class="api-input"
              :class="{ error: apiKeyError }"
            />
            <span v-if="apiKeyError" class="error-text">{{ apiKeyError }}</span>
          </div>
          <button @click="saveApiKey" class="btn save-btn" :disabled="!apiKey.trim()">
            💾 Save API Key
          </button>
        </div>

        <!-- Upload Card -->
        <div class="card upload-card">
          <h3>📁 Upload Media File</h3>
          <label class="upload-area" @drop="handleDrop" @dragover.prevent>
            <input
              ref="fileInput"
              type="file"
              accept="audio/*,video/*"
              @change="handleFileSelect"
              class="file-input"
            />
            <div class="upload-content">
              <div class="upload-icon">📁</div>
              <p>Click to select or drag & drop your audio/video file</p>
              <p class="file-types">Supported: MP3, WAV, M4A, MP4, AVI, MOV, etc.</p>
            </div>
          </label>
          <div v-if="selectedFile" class="file-info">
            <div class="file-details">
              <span class="file-name">{{ selectedFile.name }}</span>
              <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
            </div>
            <button @click="clearFile" class="btn clear-btn">❌ Clear</button>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <!-- Media Player Card -->
        <div v-if="mediaUrl" class="card media-card">
          <h3>Media Player</h3>
          <div class="media-player">
            <video
              v-if="isVideo"
              ref="mediaRef"
              :src="mediaUrl"
              controls
              class="video-player"
              @timeupdate="onTimeUpdate"
            ></video>
            <audio
              v-else
              ref="mediaRef"
              :src="mediaUrl"
              controls
              class="audio-player"
              @timeupdate="onTimeUpdate"
            ></audio>
          </div>
        </div>

        <!-- Transcription Card -->
        <div class="card transcription-card">
          <div class="transcription-header">
            <h3>Transcription</h3>
            <button
              @click="generateTranscript"
              class="btn generate-btn"
              :disabled="!canGenerate || isGenerating"
            >
              <span v-if="isGenerating" class="loading-spinner">⏳</span>
              {{ isGenerating ? "Generating..." : "Generate Transcript" }}
            </button>
          </div>

          <!-- Progress Bar -->
          <div v-if="isGenerating" class="progress-container">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progress + '%' }"></div>
            </div>
            <p class="progress-text">Processing your media file... {{ progress }}%</p>
          </div>

          <!-- Transcript Display -->
          <div v-if="transcript" class="transcript-display">
            <div class="transcript-header">
              <div class="transcript-info">
                <span class="language"
                  >🌍 Language: {{ transcript.language_code }} ({{
                    (transcript.language_probability * 100).toFixed(1)
                  }}% confidence)</span
                >
              </div>
              <div class="transcript-actions">
                <button @click="downloadTranscript('json')" class="btn download-btn">
                  📥 JSON
                </button>
                <button @click="downloadTranscript('txt')" class="btn download-btn">📥 TXT</button>
                <button @click="downloadTranscript('srt')" class="btn download-btn">📥 SRT</button>
              </div>
            </div>
            <div class="transcript-content scrollable-transcript">
              <h4>Full Transcript:</h4>
              <div v-if="sentences.length > 0">
                <span
                  v-for="(sentence, idx) in sentences"
                  :key="idx"
                  :class="['transcript-sentence', { active: idx === activeSentenceIdx }]"
                  @click="seekTo(sentence.start)"
                  :tabindex="0"
                  role="button"
                >
                  {{ sentence.text }}
                </span>
              </div>
              <p v-else>{{ transcript.text }}</p>
            </div>
          </div>

          <!-- Error Display -->
          <div v-if="error" class="error-display">
            <p class="error-message">❌ {{ error }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from "vue";
import axios from "axios";

// Reactive data
const apiKey = ref("");
const apiKeyError = ref("");
const selectedFile = ref<File | null>(null);
const mediaUrl = ref("");
const isVideo = ref(false);
const transcript = ref<any>(null);
const isGenerating = ref(false);
const progress = ref(0);
const error = ref("");
const fileInput = ref<HTMLInputElement>();
const mediaRef = ref<HTMLVideoElement | HTMLAudioElement | null>(null);
const currentTime = ref(0);

// Sentence segmentation and highlighting
const sentences = ref<{ text: string; start: number; end: number }[]>([]);
const activeSentenceIdx = ref(-1);

// Parse transcript into sentences with timing
const parseSentences = () => {
  sentences.value = [];
  if (!transcript.value || !transcript.value.words) return;
  const words = transcript.value.words;
  let sentenceWords: any[] = [];
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    if (word.type !== "word") continue;
    sentenceWords.push(word);
    if (word.text.endsWith(".")) {
      if (sentenceWords.length > 0) {
        sentences.value.push({
          text: sentenceWords.map((w) => w.text).join(" "),
          start: sentenceWords[0].start,
          end: sentenceWords[sentenceWords.length - 1].end,
        });
        sentenceWords = [];
      }
    }
  }
  // Add any trailing sentence
  if (sentenceWords.length > 0) {
    sentences.value.push({
      text: sentenceWords.map((w) => w.text).join(" "),
      start: sentenceWords[0].start,
      end: sentenceWords[sentenceWords.length - 1].end,
    });
  }
};

watch(transcript, () => {
  parseSentences();
  activeSentenceIdx.value = -1;
});

// Track media playback time and highlight
const onTimeUpdate = () => {
  if (!mediaRef.value) return;
  currentTime.value = mediaRef.value.currentTime;
  // Find the active sentence
  for (let i = 0; i < sentences.value.length; i++) {
    const s = sentences.value[i];
    if (currentTime.value >= s.start && currentTime.value <= s.end) {
      activeSentenceIdx.value = i;
      return;
    }
  }
  activeSentenceIdx.value = -1;
};

// Click to seek
const seekTo = (time: number) => {
  if (mediaRef.value) {
    mediaRef.value.currentTime = time;
    mediaRef.value.play();
  }
};

// Computed properties
const canGenerate = computed(() => {
  return selectedFile.value && apiKey.value.trim() && !isGenerating.value;
});

// Methods
const saveApiKey = () => {
  if (!apiKey.value.trim()) {
    apiKeyError.value = "Please enter a valid API key";
    return;
  }

  // Save to localStorage
  localStorage.setItem("elevenlabs_api_key", apiKey.value);
  apiKeyError.value = "";

  // Show success feedback
  const saveBtn = document.querySelector(".save-btn") as HTMLButtonElement;
  if (saveBtn) {
    const originalText = saveBtn.textContent;
    saveBtn.textContent = "✅ Saved!";
    saveBtn.disabled = true;
    setTimeout(() => {
      saveBtn.textContent = originalText;
      saveBtn.disabled = false;
    }, 2000);
  }
};

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    handleFile(target.files[0]);
  }
};

const handleDrop = (event: DragEvent) => {
  event.preventDefault();
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    handleFile(event.dataTransfer.files[0]);
  }
};

const handleFile = (file: File) => {
  // Validate file type
  const validTypes = [
    "audio/mpeg",
    "audio/wav",
    "audio/mp4",
    "audio/aac",
    "audio/ogg",
    "video/mp4",
    "video/avi",
    "video/mov",
    "video/webm",
    "video/flv",
  ];

  if (!validTypes.includes(file.type)) {
    error.value = "Please select a valid audio or video file";
    return;
  }

  selectedFile.value = file;
  isVideo.value = file.type.startsWith("video/");
  mediaUrl.value = URL.createObjectURL(file);
  transcript.value = null;
  error.value = "";
};

const clearFile = () => {
  selectedFile.value = null;
  mediaUrl.value = "";
  transcript.value = null;
  error.value = "";
  if (fileInput.value) {
    fileInput.value.value = "";
  }
};

const generateTranscript = async () => {
  if (!selectedFile.value || !apiKey.value) return;

  isGenerating.value = true;
  progress.value = 0;
  error.value = "";
  transcript.value = null;

  try {
    // Simulate progress
    const progressInterval = setInterval(() => {
      if (progress.value < 90) {
        progress.value += Math.random() * 10;
      }
    }, 500);

    // Create FormData
    const formData = new FormData();
    formData.append("file", selectedFile.value);

    // Make API request
    const response = await axios.post("/api/transcribe", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${apiKey.value}`,
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          progress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        }
      },
    });

    clearInterval(progressInterval);
    progress.value = 100;

    transcript.value = response.data;

    // Save transcript to backend
    await saveTranscriptToBackend();
  } catch (err: any) {
    error.value =
      err.response?.data?.error ||
      "Failed to generate transcript. Please check your API key and try again.";
  } finally {
    isGenerating.value = false;
    progress.value = 0;
  }
};

const saveTranscriptToBackend = async () => {
  try {
    await axios.post("/api/save-transcript", {
      filename: selectedFile.value?.name,
      transcript: transcript.value,
    });
  } catch (err) {
    console.warn("Failed to save transcript to backend:", err);
  }
};

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const downloadTranscript = (format: string) => {
  if (!transcript.value) return;

  let content = "";
  let filename = selectedFile.value?.name?.replace(/\.[^/.]+$/, "") || "transcript";

  switch (format) {
    case "json":
      content = JSON.stringify(transcript.value, null, 2);
      filename += ".json";
      break;
    case "txt":
      content = `Language: ${transcript.value.language_code}\nConfidence: ${(
        transcript.value.language_probability * 100
      ).toFixed(1)}%\n\n${transcript.value.text}`;
      filename += ".txt";
      break;
    case "srt":
      content = generateSRT(transcript.value);
      filename += ".srt";
      break;
  }

  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

const generateSRT = (transcript: any) => {
  if (!transcript.words) return "";

  let srt = "";
  let subtitleIndex = 1;
  let currentText = "";
  let startTime = 0;
  let endTime = 0;

  transcript.words.forEach((word: any, index: number) => {
    if (word.type === "word") {
      if (currentText === "") {
        startTime = word.start || 0;
      }
      currentText += word.text + " ";
      endTime = word.end || 0;

      // Create subtitle every 5 seconds or when there's a long pause
      const nextWord = transcript.words[index + 1];
      if (!nextWord || (nextWord.start && nextWord.start - endTime > 1.5)) {
        srt += `${subtitleIndex}\n`;
        srt += `${formatSRTTime(startTime)} --> ${formatSRTTime(endTime)}\n`;
        srt += `${currentText.trim()}\n\n`;
        subtitleIndex++;
        currentText = "";
      }
    }
  });

  return srt;
};

const formatSRTTime = (seconds: number) => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  const ms = Math.floor((seconds % 1) * 1000);
  return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${secs
    .toString()
    .padStart(2, "0")},${ms.toString().padStart(3, "0")}`;
};

// Load saved API key on mount
onMounted(() => {
  const savedApiKey = localStorage.getItem("elevenlabs_api_key");
  if (savedApiKey) {
    apiKey.value = savedApiKey;
  }
});
</script>

<style scoped>
.transcription-app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  width: 100%;
  overflow-x: hidden;
}

.main-flex {
  display: flex;
  flex-direction: row;
  gap: 40px;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 16px;
  box-sizing: border-box;
  justify-content: center;
}

.left-panel {
  flex: 1 1 340px;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.right-panel {
  flex: 2 1 700px;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 24px;
  align-items: flex-start;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
  margin-bottom: 12px;
}

h3 {
  margin: 0 0 18px 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.api-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.3s ease;
}
.api-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}
.api-input.error {
  border-color: #e74c3c;
}
.error-text {
  color: #e74c3c;
  font-size: 0.9rem;
  margin-top: 5px;
  display: block;
}

.btn {
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  padding: 10px 22px;
  cursor: pointer;
  transition: all 0.2s;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  margin-top: 8px;
  margin-bottom: 0;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.08);
}
.btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #764ba2 100%);
  transform: translateY(-2px);
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.save-btn {
  width: 100%;
}
.clear-btn {
  background: #e74c3c;
  color: white;
  margin-top: 10px;
  margin-left: 0;
  width: 100%;
}
.clear-btn:hover {
  background: #c0392b;
}
.generate-btn {
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: white;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 8px;
  margin-top: 0;
}
.generate-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #219150 0%, #27ae60 100%);
}
.download-btn {
  background: #667eea;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  margin: 0 2px;
}
.download-btn:hover {
  background: #5a6fd8;
}

.upload-area {
  border: 2px dashed #667eea;
  border-radius: 12px;
  padding: 36px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  display: block;
  margin-bottom: 10px;
}
.upload-area:hover {
  border-color: #764ba2;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}
.file-input {
  display: none;
}
.upload-content {
  pointer-events: none;
}
.upload-icon {
  font-size: 2.2rem;
  margin-bottom: 10px;
}
.upload-content p {
  margin: 8px 0;
  color: #666;
}
.file-types {
  font-size: 0.9rem;
  opacity: 0.7;
}
.file-info {
  margin-top: 10px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.file-details {
  display: flex;
  flex-direction: row;
  gap: 8px;
  align-items: center;
}
.file-name {
  font-weight: 500;
  color: #333;
}
.file-size {
  font-size: 0.9rem;
  color: #666;
}

.media-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.media-card {
  background: white;
  border-radius: 16px;
  padding: 16px 16px 8px 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
  max-width: 480px;
  margin-bottom: 8px;
}
.media-card h3 {
  margin: 0 0 10px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}
.media-player {
  width: 100%;
  display: flex;
  justify-content: center;
}
.video-player {
  width: 100%;
  max-width: 440px;
  max-height: 300px;
  border-radius: 8px;
  background: #000;
}
.audio-player {
  width: 100%;
  max-width: 440px;
  border-radius: 8px;
}

.transcription-section {
  width: 100%;
}
.transcription-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  width: 100%;
  max-width: 700px;
}
.transcription-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}
.progress-container {
  margin-bottom: 20px;
}
.progress-bar {
  width: 100%;
  height: 8px;
  background: #e1e5e9;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}
.progress-text {
  text-align: center;
  color: #666;
  font-size: 0.9rem;
}
.transcript-display {
  border: 1px solid #e1e5e9;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  margin-top: 12px;
}
.transcript-header {
  background: #f8f9fa;
  padding: 16px;
  border-bottom: 1px solid #e1e5e9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.transcript-info {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.language {
  font-size: 0.95rem;
  color: #666;
}
.transcript-actions {
  display: flex;
  gap: 8px;
}
.transcript-content {
  padding: 20px;
  background: #fff;
}
.scrollable-transcript {
  max-height: 400px;
  overflow-y: auto;
  border-radius: 0 0 12px 12px;
}
.transcript-content h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 1.1rem;
}
.transcript-content p {
  line-height: 1.6;
  color: #555;
  margin: 0;
  white-space: pre-line;
}
.error-display {
  background: #f8d7da;
  color: #721c24;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #f5c6cb;
  margin-top: 16px;
}
.error-message {
  margin: 0;
  font-weight: 500;
}
.transcript-sentence {
  display: inline;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 6px;
  transition: background 0.2s, color 0.2s;
  margin-right: 2px;
}
.transcript-sentence.active {
  background: #667eea;
  color: #fff;
}
.transcript-sentence:hover {
  background: #e1e5e9;
}
@media (max-width: 1100px) {
  .main-flex {
    flex-direction: column;
    padding: 24px 4px;
    gap: 24px;
    max-width: 100vw;
  }
  .left-panel,
  .right-panel {
    max-width: 100%;
    width: 100%;
    align-items: stretch;
  }
  .media-card,
  .transcription-card {
    max-width: 100%;
  }
}
</style>

<style>
html,
body {
  overflow-x: hidden !important;
}
</style>
