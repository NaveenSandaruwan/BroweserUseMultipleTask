# ElevenLabs TTS Integration

This extension now supports high-quality text-to-speech using ElevenLabs API.

## Features

- **Dual TTS System**: Uses ElevenLabs when configured, falls back to browser TTS
- **Chunked Processing**: Converts 2 sentences at a time for optimal performance
- **Progress Tracking**: Shows generation and playback progress
- **Voice Selection**: Choose from default voices or your custom cloned voices
- **Markdown Support**: Automatically strips markdown formatting for cleaner speech

## Setup Instructions

### 1. Get ElevenLabs API Key

1. Visit [ElevenLabs.io](https://elevenlabs.io)
2. Create an account or sign in
3. Go to your profile settings
4. Copy your API key

### 2. Configure the Extension

1. Load the extension in Chrome
2. Navigate to any webpage
3. Click the 🎵 (music note) button in the avatar UI
4. Paste your API key
5. Select your preferred voice
6. Click "Test TTS" to verify setup
7. Click "Save & Use ElevenLabs"

### 3. Usage

Once configured, all AI responses will automatically use ElevenLabs TTS:

- **AI Chat**: Speak to the avatar - responses will be spoken using ElevenLabs
- **Text Display**: The text will still appear in the speech bubble (unchanged)
- **Emotion Detection**: Avatar emotions still work normally (unchanged)
- **Progress**: Watch the status for "Generating audio" and "Speaking" updates

## Buttons

- 🎤 **Microphone**: Start voice input
- 🔊 **Test TTS**: Test current TTS system (browser or ElevenLabs)
- 🎵 **ElevenLabs Config**: Configure ElevenLabs API and voice settings
- 🎭 **Emotion Test**: Test avatar emotion detection
- 📌 **Save Position**: Save current avatar position

## Technical Details

### Text Processing

1. **Markdown Removal**: Bold, italic, code blocks, and links are stripped
2. **Sentence Splitting**: Text is split at sentence boundaries (., !, ?)
3. **Chunking**: Sentences are grouped in pairs for processing
4. **Sequential Playback**: Audio chunks play in order without overlap

### Error Handling

- If ElevenLabs fails, automatically falls back to browser TTS
- API errors are displayed in the status area
- Network issues are handled gracefully

### Storage

- API key is stored locally in browser storage
- Voice preference is remembered
- Configuration persists across browser sessions

## Troubleshooting

### Common Issues

1. **"API key missing"**: Click 🎵 button to configure your ElevenLabs API key
2. **"TTS Error"**: Check your API key and internet connection
3. **No sound**: Check browser audio permissions and volume
4. **Slow generation**: Large texts take longer - watch the progress indicators

### Fallback Behavior

If ElevenLabs is unavailable:

- Extension automatically uses browser TTS
- All other features continue working normally
- You can reconfigure ElevenLabs anytime using the 🎵 button

### Voice Quality

- ElevenLabs provides higher quality, more natural-sounding speech
- Browser TTS is faster but lower quality
- Custom cloned voices (if available) provide personalized speech

## API Limits

Be aware of ElevenLabs API limits:

- Free tier: Limited characters per month
- Paid tiers: Higher limits and more features
- Check your usage at [ElevenLabs.io](https://elevenlabs.io)

## Privacy

- API key is stored locally only
- Text is sent to ElevenLabs for speech generation
- No other data is transmitted
- You can disable ElevenLabs anytime by removing the API key
