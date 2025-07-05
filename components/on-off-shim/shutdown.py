#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import subprocess

# --- Configuration ---
# GPIO pin for input (waiting for low signal)
INPUT_PIN = 17

# GPIO pin for output (setting to low)
OUTPUT_PIN = 4
# CUT_PIN = 27

# Define the minimum press duration in seconds
PRESS_DURATION_SECONDS = 0.5

# --- Setup GPIO ---
def setup_gpio():
    """
    Sets up the GPIO mode, input pin with pull-up resistor,
    and output pin.
    """
    GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme

    # Setup INPUT_PIN as an input with a pull-up resistor.
    # This means the pin will be HIGH by default, and go LOW when connected to ground.
    GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print(f"GPIO {INPUT_PIN} set as input with pull-up.")

    # Setup OUTPUT_PIN as an output and initialize it to HIGH (or any safe state)
    # before we set it to LOW later.
    # GPIO.setup(CUT_PIN, GPIO.OUT)
    GPIO.setup(OUTPUT_PIN, GPIO.OUT)
    GPIO.output(OUTPUT_PIN, GPIO.HIGH) # Ensure it's high initially

# --- Main Logic ---
def main():
    """
    Waits for INPUT_PIN to go low, then echoes "shut down" and sets OUTPUT_PIN low.
    """
    try:
        setup_gpio()

        while True: # Loop indefinitely to wait for valid presses
            # Wait for a falling edge (button press)
            # bouncetime helps debounce the signal, preventing multiple triggers from one press
            GPIO.wait_for_edge(INPUT_PIN, GPIO.FALLING, bouncetime=200)
            press_start_time = time.time()
            print(f"Button pressed at {time.strftime('%H:%M:%S', time.localtime(press_start_time))}. Waiting for release...")

            # Now wait for a rising edge (button release) or timeout
            # We'll use a timeout here in case the button gets stuck or released quickly
            # If the button is released before timeout, wait_for_edge returns the pin number
            # If timeout occurs, it returns None.
            # We need to make sure the pin is still LOW if we hit the timeout.
            channel_detected = GPIO.wait_for_edge(INPUT_PIN, GPIO.RISING, timeout=int(PRESS_DURATION_SECONDS * 1000 * 2)) # Timeout is in milliseconds, double the expected press duration
            
            if channel_detected is None:
                # This means the timeout occurred BEFORE a rising edge was detected.
                # The button might still be held down.
                # Check the current state of the pin. If it's still low, it was held for a long time.
                if GPIO.input(INPUT_PIN) == GPIO.LOW:
                    # Button is still pressed after the (PRESS_DURATION_SECONDS * 2) timeout.
                    # Assume it was pressed long enough.
                    press_end_time = time.time() # Just take current time
                    duration = press_end_time - press_start_time
                    print(f"Button held for an extended period (>{PRESS_DURATION_SECONDS*2}s). Assuming valid press.")
                    
                else:
                    # This case means the button was released *just* after the timeout,
                    # or there was some anomaly. Let's re-evaluate more robustly.
                    # If it's HIGH, it was released before the full duration, but after wait_for_edge timeout.
                    # For safety, let's just re-evaluate based on the initial check logic below.
                    print("Timeout occurred, but button was released. Re-checking duration.")
                    press_end_time = time.time() # Take current time for recalculation
                    duration = press_end_time - press_start_time

            else:
                # Rising edge detected - button was released
                press_end_time = time.time()
                duration = press_end_time - press_start_time
                print(f"Button released at {time.strftime('%H:%M:%S', time.localtime(press_end_time))}. Duration: {duration:.2f} seconds.")

            if duration >= PRESS_DURATION_SECONDS:
                print(f"Valid press detected! Duration: {duration:.2f}s >= {PRESS_DURATION_SECONDS}s.")
                break # Exit the loop, proceed to shutdown logic
            else:
                print(f"Button press too short ({duration:.2f}s). Required: {PRESS_DURATION_SECONDS}s. Waiting for next press...")
                # Continue the loop to wait for another falling edge
                time.sleep(0.1) # Small delay to prevent immediate re-triggering on very fast presses/releases

        print("GPIO signal detected! Stopping services...")

        # Stop services
        services = [
            # "autohotspot-daemon.service", # Never stop this because it seems to restart the machine
            "phoniebox-buttons-usb-encoder.service" 
            "phoniebox-gpio-control.service",
            "phoniebox-rfid-reader.service",
            "phoniebox-startup-scripts.service"
        ]
        print(f"Attempting to stop services: {', '.join(services)}")
        for service in services:
            try:
                print(f"Stopping {service}.")
                # Use subprocess.run to execute the systemctl command
                # capture_output=True to get stdout/stderr, text=True to decode as text
                # check=True will raise CalledProcessError if the command returns a non-zero exit code
                result = subprocess.run(
                    ["sudo", "systemctl", "stop", service],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"Successfully stopped {service}.")
                if result.stdout:
                    print(f"  Stdout: {result.stdout.strip()}")
                if result.stderr:
                    print(f"  Stderr: {result.stderr.strip()}")
            except subprocess.CalledProcessError as e:
                print(f"Error stopping {service}: {e}")
                print(f"  Command: {e.cmd}")
                print(f"  Return Code: {e.returncode}")
                print(f"  Stdout: {e.stdout.strip()}")
                print(f"  Stderr: {e.stderr.strip()}")
            except FileNotFoundError:
                print(f"Error: 'systemctl' command not found. Is systemd installed and in PATH?")
            except Exception as e:
                print(f"An unexpected error occurred while stopping {service}: {e}")
        print("Finished attempting to stop services.")

        # Set CUT_PIN to HIGH
        # GPIO.output(CUT_PIN, GPIO.HIGH)

        # Set OUTPUT_PIN to LOW
        GPIO.output(OUTPUT_PIN, GPIO.LOW)
        subprocess.run(
            ["sudo", "shutdown", "-h", "now"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"GPIO {OUTPUT_PIN} set to LOW.")
        print("Script finished.")

    except KeyboardInterrupt:
        print("\nScript terminated by user (Ctrl+C).")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up GPIO settings to release the pins
        GPIO.cleanup()
        print("GPIO cleanup complete.")

# --- Run the script ---
if __name__ == "__main__":
    main()