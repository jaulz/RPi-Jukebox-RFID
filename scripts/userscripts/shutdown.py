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
    #GPIO.setup(OUTPUT_PIN, GPIO.OUT)
    #GPIO.output(OUTPUT_PIN, GPIO.HIGH)

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

        subprocess.run(
            ['sudo', 'shutdown', '-h', 'now'],
            capture_output=True,
            text=True,
            check=True
        )

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