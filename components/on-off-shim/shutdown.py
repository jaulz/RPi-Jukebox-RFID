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
        print(f"Waiting for GPIO {INPUT_PIN} to go LOW...")

        # Wait for a falling edge (transition from HIGH to LOW) on INPUT_PIN
        # bouncetime helps debounce the signal, preventing multiple triggers from one press
        GPIO.wait_for_edge(INPUT_PIN, GPIO.FALLING, bouncetime=200)
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