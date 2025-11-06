# NeoPixel Control System

Raspberry Pi 5에서 네오픽셀 LED 스트립을 TCP를 통해 원격 제어하는 프로그램입니다.

## 기능

- **3가지 LED 모드**
  - 모드 1: 무지개 색상 사이클
  - 모드 2: 추적 효과 (LED가 하나씩 따라가는 효과)
  - 모드 3: 페이드 인/아웃 효과

- **TCP 원격 제어**
  - 외부 PC에서 네트워크를 통해 모드 제어
  - JSON 형식의 명령 프로토콜
  - 멀티 클라이언트 지원

## 요구사항

- Raspberry Pi 5
- Python 3.x
- `pi5neo` 모듈
- 네오픽셀 LED 스트립 (SPI 연결)

## 설치

1. 필요한 Python 패키지가 설치되어 있는지 확인:
```bash
pip install pi5neo
```

2. SPI 인터페이스 활성화:
```bash
sudo raspi-config
# Interface Options > SPI > Enable
```

## 사용법

### 서버 실행

Raspberry Pi에서 서버를 실행합니다:

```bash
python neo_test.py
```

서버는 기본적으로 `0.0.0.0:8888`에서 실행됩니다.

### 클라이언트에서 제어

외부 PC에서 Python 클라이언트를 사용하여 제어할 수 있습니다:

```python
import socket
import json

def send_command(host, port, command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.send(json.dumps(command).encode('utf-8'))
        response = sock.recv(1024).decode('utf-8')
        print(json.loads(response))
    finally:
        sock.close()

# 사용 예시
# Raspberry Pi의 IP 주소로 변경하세요
PI_IP = '192.168.1.100'
PORT = 8888

# 모드 1 시작 (무지개 사이클)
send_command(PI_IP, PORT, {'command': 'mode', 'mode': 1})

# 모드 2 시작 (추적 효과)
send_command(PI_IP, PORT, {'command': 'mode', 'mode': 2})

# 모드 3 시작 (페이드 효과)
send_command(PI_IP, PORT, {'command': 'mode', 'mode': 3})

# 현재 모드 중지
send_command(PI_IP, PORT, {'command': 'stop'})

# LED 끄기
send_command(PI_IP, PORT, {'command': 'off'})

# 상태 확인
send_command(PI_IP, PORT, {'command': 'status'})
```

## 명령어

### 모드 시작
```json
{"command": "mode", "mode": 1}  // 모드 1 (무지개 사이클)
{"command": "mode", "mode": 2}  // 모드 2 (추적 효과)
{"command": "mode", "mode": 3}  // 모드 3 (페이드 효과)
```

### 모드 중지
```json
{"command": "stop"}
```

### LED 끄기
```json
{"command": "off"}
```

### 상태 확인
```json
{"command": "status"}
```

응답 예시:
```json
{
  "status": "success",
  "current_mode": 1,
  "running": true
}
```

## 설정 변경

`neo_test.py` 파일에서 다음 설정을 변경할 수 있습니다:

- `spi_device`: SPI 디바이스 경로 (기본값: `/dev/spidev0.0`)
- `num_leds`: LED 개수 (기본값: 20)
- `frequency`: SPI 주파수 (기본값: 800)
- `host`: 서버 바인딩 주소 (기본값: `0.0.0.0`)
- `port`: 서버 포트 (기본값: 8888)

## 하드웨어 연결

네오픽셀 LED 스트립을 Raspberry Pi의 SPI 인터페이스에 연결하세요:
- VCC → 5V
- GND → GND
- DIN → MOSI (GPIO 10)

## 라이선스

이 프로젝트는 자유롭게 사용할 수 있습니다.

