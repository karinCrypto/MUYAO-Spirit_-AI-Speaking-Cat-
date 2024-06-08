import requests
import json
import os
import pyaudio
import wave
import whisper

# 환경 변수에서 API 키 가져오기
api_key = os.getenv("TYPECAST_API_KEY")
if not api_key:
    raise ValueError("API 키가 설정되지 않았습니다. 환경 변수 'TYPECAST_API_KEY'를 설정하세요.")

# Typecast API 호출을 위한 함수
def call_typecast_api():
    url = "https://typecast.ai/api/speak"  # Typecast API 엔드포인트 URL
    payload = json.dumps({
        "actor_id": "66596206b7bd6e89c3a2c54e",  # Typecast에서 사용할 배우 ID
        "text": "나는 화가가 되고 싶었어. 우리 집사는 자기 팔레트를 왜 그렇게 못 건드리게 했는지. 집사가 그림 그리고 있을 때마다 나도 같이 하고 싶었는데! 한 번 나도 그림 그려보는 게 소원이야. 내 억울함을 풀기 위해 그림을 완성시켜줘.",  # 음성으로 변환할 텍스트
        "lang": "ko",  # 한국어 설정
        "tempo": 1,  # 말하는 속도 설정
        "volume": 130,  # 볼륨 설정
        "pitch": 0,  # 음성의 높낮이 설정
        "xapi_hd": True,  # 고해상도 오디오 사용 여부
        "max_seconds": 60,  # 최대 음성 길이
        "model_version": "latest",  # 모델 버전 설정
        "xapi_audio_format": "wav",  # 오디오 포맷 설정
        "emotion_tone_preset": "normal-4"  # 감정 톤 설정
    })

    headers = {
        'Content-Type': 'application/json',  # 요청의 콘텐츠 타입 설정
        'Authorization': f'Bearer {api_key}'  # API 키를 포함한 인증 헤더
    }

    # POST 요청을 보내고 응답을 저장
    response = requests.request("POST", url, headers=headers, data=payload)

    # 응답 출력 (디버깅 또는 정보 확인용)
    print(response.text)

    # 응답의 내용을 음성 파일로 저장합니다.
    with open("response.wav", "wb") as audio_file:
        audio_file.write(response.content)

# Whisper 모델 로드
model = whisper.load_model("medium")

# 오디오 녹음 및 변환 함수
def transcribe_directly():
    # 오디오 녹음을 위한 설정
    sample_rate = 16000  # 샘플링 레이트 (Hz)
    bits_per_sample = 16  # 샘플 당 비트 수
    chunk_size = 1024  # 버퍼 크기
    audio_format = pyaudio.paInt16  # 오디오 포맷
    channels = 1  # 채널 수 (모노)

    # 오디오 스트림에서 데이터를 받아 파일에 쓰는 콜백 함수
    def callback(in_data, frame_count, time_info, status):
        wav_file.writeframes(in_data)  # 받은 오디오 데이터를 파일에 쓰기
        return None, pyaudio.paContinue

    # wave 파일 열기 (쓰기 모드)
    wav_file = wave.open('./output.wav', 'wb')
    wav_file.setnchannels(channels)  # 채널 설정
    wav_file.setsampwidth(bits_per_sample // 8)  # 샘플 너비 설정
    wav_file.setframerate(sample_rate)  # 샘플링 레이트 설정

    # PyAudio 초기화
    audio = pyaudio.PyAudio()

    # 오디오 스트림 열기
    stream = audio.open(format=audio_format,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk_size,
                        stream_callback=callback)

    # 사용자가 엔터를 누를 때까지 녹음
    input("Press Enter to stop recording...")

    # 오디오 스트림 정지 및 종료
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # wave 파일 닫기
    wav_file.close()

    # 녹음된 오디오 파일을 텍스트로 변환 (한국어)
    result = model.transcribe("./output.wav", language="ko")  # 한국어로 설정
    return result['text']  # 변환된 텍스트 반환

# Typecast API 호출
call_typecast_api()

# 오디오 녹음 및 텍스트 변환
text = transcribe_directly()
print("Transcribed Text:", text)  # 변환된 텍스트 출력
