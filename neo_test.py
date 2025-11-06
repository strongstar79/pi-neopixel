from pi5neo import Pi5Neo
import time
import socket
import threading
import json

class NeoPixelController:
    def __init__(self, spi_device='/dev/spidev0.0', num_leds=20, frequency=800):
        self.neo = Pi5Neo(spi_device, num_leds, frequency)
        self.num_leds = num_leds
        self.current_mode = None
        self.running = False
        self.mode_thread = None
        
    def mode_1_rainbow_cycle(self, delay=0.5):
        """모드 1: 무지개 색상 사이클 (GRB 순서)"""
        colors = [
            (0, 255, 0),      # Red (GRB: G=0, R=255, B=0)
            (255, 0, 0),      # Red (GRB: G=0, R=255, B=0)
            (0, 0, 255),      # Red (GRB: G=0, R=255, B=0)
            """(94, 255, 0),    # Orange
            (255, 255, 0),    # Yellow
            (255, 0, 0),      # Green (GRB: G=255, R=0, B=0)
            (0, 0, 255),      # Blue (GRB: G=0, R=0, B=255)
            (75, 0, 130),     # Indigo
            (148, 0, 211)     # Violet"""
        ]
        while self.running:
            for color in colors:
                if not self.running:
                    break
                self.neo.fill_strip(*color)
                self.neo.update_strip()
                time.sleep(delay)
    
    def mode_2_chase(self, delay=0.05):
        """모드 2: 추적 효과 (LED가 하나씩 따라가는 효과) (GRB 순서)"""
        while self.running:
            for i in range(self.num_leds):
                if not self.running:
                    break
                # 모든 LED 끄기
                self.neo.clear_strip()
                # 현재 LED 켜기 (청록색: GRB 순서)
                # set_led_color(index, red, green, blue) - fill_strip과 동일하게 GRB 순서로 동작 (파라미터 이름은 RGB지만 실제로는 GRB)
                self.neo.set_led_color(i, 0, 255, 0)  # 청록색 (GRB: G=255, R=0, B=255)
                self.neo.update_strip()
                time.sleep(delay)
    
    def mode_3_fade(self, delay=0.02):
        """모드 3: 페이드 인/아웃 효과 (GRB 순서)"""
        brightness = 0
        direction = 1
        while self.running:
            brightness += direction * 5
            if brightness >= 255:
                brightness = 255
                direction = -1
            elif brightness <= 0:
                brightness = 0
                direction = 1
            
            # GRB 순서로 변환 (RGB에서 GRB로)
            g = int(brightness * 0.5)  # Green
            r = int(brightness)         # Red
            b = int(brightness * 0.8)   # Blue
            
            self.neo.fill_strip(g, r, b)  # GRB 순서
            self.neo.update_strip()
            time.sleep(delay)
    
    def stop_current_mode(self):
        """현재 모드 중지"""
        self.running = False
        if self.mode_thread and self.mode_thread.is_alive():
            self.mode_thread.join(timeout=1.0)
        self.neo.fill_strip(0, 0, 0)  # 모든 LED 끄기
        self.neo.update_strip()
    
    def start_mode(self, mode_num):
        """모드 시작"""
        self.stop_current_mode()
        self.running = True
        self.current_mode = mode_num
        
        if mode_num == 1:
            self.mode_thread = threading.Thread(target=self.mode_1_rainbow_cycle)
        elif mode_num == 2:
            self.mode_thread = threading.Thread(target=self.mode_2_chase)
        elif mode_num == 3:
            self.mode_thread = threading.Thread(target=self.mode_3_fade)
        else:
            self.running = False
            return False
        
        self.mode_thread.daemon = True
        self.mode_thread.start()
        return True
    
    def handle_client(self, client_socket, addr):
        """TCP 클라이언트 요청 처리"""
        print(f"클라이언트 연결: {addr}")
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                try:
                    command = json.loads(data)
                    cmd = command.get('command')
                    
                    if cmd == 'mode':
                        mode_num = command.get('mode', 0)
                        if mode_num in [1, 2, 3]:
                            self.start_mode(mode_num)
                            response = {'status': 'success', 'message': f'모드 {mode_num} 시작'}
                        else:
                            response = {'status': 'error', 'message': '잘못된 모드 번호 (1-3)'}
                    
                    elif cmd == 'stop':
                        self.stop_current_mode()
                        response = {'status': 'success', 'message': '모드 중지'}
                    
                    elif cmd == 'status':
                        response = {
                            'status': 'success',
                            'current_mode': self.current_mode,
                            'running': self.running
                        }
                    
                    elif cmd == 'off':
                        self.stop_current_mode()
                        self.neo.fill_strip(0, 0, 0)
                        self.neo.update_strip()
                        response = {'status': 'success', 'message': 'LED 끄기'}
                    
                    else:
                        response = {'status': 'error', 'message': '알 수 없는 명령'}
                    
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
                except json.JSONDecodeError:
                    response = {'status': 'error', 'message': '잘못된 JSON 형식'}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    
        except Exception as e:
            print(f"클라이언트 처리 오류: {e}")
        finally:
            client_socket.close()
            print(f"클라이언트 연결 종료: {addr}")
    
    def start_server(self, host='0.0.0.0', port=8888):
        """TCP 서버 시작"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        
        print(f"TCP 서버 시작: {host}:{port}")
        print("사용 가능한 명령:")
        print("  {'command': 'mode', 'mode': 1} - 무지개 사이클")
        print("  {'command': 'mode', 'mode': 2} - 추적 효과")
        print("  {'command': 'mode', 'mode': 3} - 페이드 효과")
        print("  {'command': 'stop'} - 현재 모드 중지")
        print("  {'command': 'status'} - 현재 상태 확인")
        print("  {'command': 'off'} - LED 끄기")
        
        try:
            while True:
                client_socket, addr = server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\n서버 종료 중...")
        finally:
            self.stop_current_mode()
            server_socket.close()

if __name__ == '__main__':
    controller = NeoPixelController('/dev/spidev0.0', 20, 800)
    controller.start_server(host='0.0.0.0', port=8888)
