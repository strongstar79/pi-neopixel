"""
NeoPixel 제어를 위한 클라이언트 예제
외부 PC에서 이 스크립트를 실행하여 Raspberry Pi의 네오픽셀을 제어할 수 있습니다.
"""

import socket
import json
import sys

class NeoPixelClient:
    def __init__(self, host, port=8888):
        self.host = host
        self.port = port
    
    def send_command(self, command):
        """서버에 명령 전송"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
            sock.send(json.dumps(command).encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        finally:
            sock.close()
    
    def start_mode(self, mode_num):
        """모드 시작"""
        return self.send_command({'command': 'mode', 'mode': mode_num})
    
    def stop(self):
        """모드 중지"""
        return self.send_command({'command': 'stop'})
    
    def off(self):
        """LED 끄기"""
        return self.send_command({'command': 'off'})
    
    def status(self):
        """상태 확인"""
        return self.send_command({'command': 'status'})


def main():
    if len(sys.argv) < 2:
        print("사용법: python client_example.py <Raspberry_Pi_IP> [명령]")
        print("\n명령:")
        print("  mode1  - 무지개 사이클 시작")
        print("  mode2  - 추적 효과 시작")
        print("  mode3  - 페이드 효과 시작")
        print("  stop   - 현재 모드 중지")
        print("  off    - LED 끄기")
        print("  status - 상태 확인")
        print("\n예시:")
        print("  python client_example.py 192.168.1.100 mode1")
        sys.exit(1)
    
    host = sys.argv[1]
    client = NeoPixelClient(host)
    
    if len(sys.argv) >= 3:
        command = sys.argv[2].lower()
        
        if command == 'mode1':
            result = client.start_mode(1)
        elif command == 'mode2':
            result = client.start_mode(2)
        elif command == 'mode3':
            result = client.start_mode(3)
        elif command == 'stop':
            result = client.stop()
        elif command == 'off':
            result = client.off()
        elif command == 'status':
            result = client.status()
        else:
            print(f"알 수 없는 명령: {command}")
            sys.exit(1)
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 대화형 모드
        print(f"NeoPixel 클라이언트 - {host}:8888")
        print("명령을 입력하세요 (mode1, mode2, mode3, stop, off, status, quit)")
        
        while True:
            try:
                cmd = input("> ").strip().lower()
                if cmd == 'quit' or cmd == 'exit':
                    break
                elif cmd == 'mode1':
                    result = client.start_mode(1)
                elif cmd == 'mode2':
                    result = client.start_mode(2)
                elif cmd == 'mode3':
                    result = client.start_mode(3)
                elif cmd == 'stop':
                    result = client.stop()
                elif cmd == 'off':
                    result = client.off()
                elif cmd == 'status':
                    result = client.status()
                else:
                    print("알 수 없는 명령입니다.")
                    continue
                
                print(json.dumps(result, indent=2, ensure_ascii=False))
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"오류: {e}")

if __name__ == '__main__':
    main()

