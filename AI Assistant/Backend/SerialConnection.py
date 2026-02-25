import serial
import time

class ArduinoSerial:
    def __init__(self, port="COM10", baudrate=9600):
        try:
            self.arduino = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # wait for Arduino to reboot
            print(f"[green]Connected to Arduino on {port}[/green]")
        except Exception as e:
            print(f"[red]Failed to connect to Arduino: {e}[/red]")
            self.arduino = None

    def send(self, data: str):
        """Send commands to Arduino"""
        try:
            if self.arduino and self.arduino.is_open:
                self.arduino.write((data + "\n").encode())
                return True
            else:
                print("[red]Arduino not connected.[/red]")
                return False
        except Exception as e:
            print(f"[red]Error sending data to Arduino: {e}[/red]")
            return False

    def read(self):
        """Read data from Arduino"""
        try:
            if self.arduino and self.arduino.is_open:
                if self.arduino.in_waiting > 0:
                    return self.arduino.readline().decode().strip()
            return None
        except Exception as e:
            print(f"[red]Error reading from Arduino: {e}[/red]")
            return None

    def close(self):
        """Close serial connection"""
        try:
            if self.arduino:
                self.arduino.close()
                print("[yellow]Arduino connection closed.[/yellow]")
        except:
            pass
