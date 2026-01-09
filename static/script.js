document.addEventListener('DOMContentLoaded', () => {
    loadVoices();
});

// Load available voices from backend
async function loadVoices() {
    try {
        const response = await fetch('/api/voices');
        const voices = await response.json();

        const select = document.getElementById('voice-select');
        select.innerHTML = ''; // Clear loading

        voices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = voice.label;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load voices:', error);
        document.getElementById('voice-select').innerHTML = '<option>Error loading voices</option>';
    }
}

// Handle conversion process
async function convert() {
    const thaiText = document.getElementById('thai-input').value.trim();
    const voiceChoice = document.getElementById('voice-select').value;
    const btn = document.getElementById('convert-btn');
    const btnText = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.loader');
    const resultSection = document.getElementById('result-section');

    // Validation
    if (!thaiText) {
        alert('Please enter some Thai text.');
        return;
    }

    // UI Loading State
    btn.disabled = true;
    btnText.textContent = 'กำลังประมวลผล...';
    loader.classList.remove('hidden');
    resultSection.classList.add('hidden');

    try {
        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: thaiText,
                voice: voiceChoice
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Conversion failed');
        }

        // Display Results
        document.getElementById('chinese-output').textContent = data.chinese;
        document.getElementById('translator-info').textContent = `Translated via ${data.translator}`;

        const audioPlayer = document.getElementById('audio-player');
        audioPlayer.src = data.audio_url;
        audioPlayer.load();

        // Update download link
        const downloadLink = document.getElementById('download-link');
        downloadLink.href = data.audio_url;
        downloadLink.download = `tts_output_${new Date().getTime()}.mp3`;
        downloadLink.classList.remove('hidden');

        // Show result section with smooth animation
        resultSection.classList.remove('hidden');

        // Auto play audio (optional)
        try {
            await audioPlayer.play();
        } catch (e) {
            console.log("Auto-play blocked, user must click play.");
        }

    } catch (error) {
        alert(error.message);
    } finally {
        // Reset UI State
        btn.disabled = false;
        btnText.textContent = 'แปลงเป็นเสียง';
        loader.classList.add('hidden');
    }
}
