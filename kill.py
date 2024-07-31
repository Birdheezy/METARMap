import os
import subprocess
import board
import neopixel

def kill_processes(process_names):
    for process_name in process_names:
        try:
            # Get the list of processes
            result = subprocess.run(["pgrep", "-f", process_name], capture_output=True, text=True)
            pids = result.stdout.split()
            for pid in pids:
                # Kill each process
                os.kill(int(pid), 9)
                print(f'Killed {process_name} with PID {pid}')
        except Exception as e:
            print(f'Error killing process {process_name}: {e}')

def turn_off_leds():
    pixels = neopixel.NeoPixel(board.D18, 50)
    pixels.deinit()

    print("LEDs off")

def main():
    processes_to_kill = ["metar.py", "led_startup.py"]
    kill_processes(processes_to_kill)
    turn_off_leds()
    print('Killed metar.py and led_startup.py')
    print('Script finished!')

if __name__ == "__main__":
    main()
