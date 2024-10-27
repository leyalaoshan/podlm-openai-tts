from flask import Flask, request, send_file
import openai
import os
import io
import wave

app = Flask(__name__)

# 設置您的OpenAI API密鑰
openai.api_key = 'sk-xxx'

# 定義有效的聲音類型
VALID_VOICES = ['nova', 'shimmer', 'echo', 'onyx', 'fable', 'alloy']

@app.route('/tts', methods=['GET'])
def text_to_speech():
    text = request.args.get('text', '')
    language = request.args.get('language', 'en')
    anchor_type = request.args.get('anchor_type', 'alloy')

    # 確保 anchor_type 是有效的聲音類型
    voice = anchor_type if anchor_type in VALID_VOICES else 'alloy'

    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )

        # 將音頻保存為臨時文件
        temp_file = "temp_audio.mp3"
        response.stream_to_file(temp_file)

        # 發送該文件並在發送後刪除
        return_value = send_file(temp_file, mimetype="audio/mpeg", as_attachment=True, download_name="speech.mp3")
        os.remove(temp_file)
        return return_value

    except Exception as e:
        return str(e), 500

@app.route('/merge_audio', methods=['POST'])
def merge_audio():
    if 'audio_files' not in request.files:
        return "No audio files provided", 400

    audio_files = request.files.getlist('audio_files')

    if not audio_files:
        return "No audio files provided", 400

    try:
        # 讀取所有音頻文件
        data = []
        for audio_file in audio_files:
            with wave.open(io.BytesIO(audio_file.read()), 'rb') as wav_file:
                data.append([wav_file.getparams(), wav_file.readframes(wav_file.getnframes())])

        # 合併音頻文件
        output = io.BytesIO()
        output_wav = wave.open(output, 'wb')
        output_wav.setparams(data[0][0])
        for frame in data:
            output_wav.writeframes(frame[1])
        output_wav.close()

        # 將合併後的音頻發送回客戶端
        output.seek(0)
        return send_file(output, mimetype="audio/wav", as_attachment=True, download_name="merged_audio.wav")

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)