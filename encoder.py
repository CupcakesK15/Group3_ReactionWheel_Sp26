import lgpio
import time
import sys

# --- Configuration ---
PIN_A = 5          # Confirmed by your scanner
PIN_B = 6          # Confirmed by your scanner
TOTAL_CPR = 14     # Standard for REV HD Hex (Raw Shaft)
CHIP = 0           # Standard GPIO chip for Pi 5

# --- Initialization ---
try:
    h = lgpio.gpiochip_open(CHIP)
    lgpio.gpio_claim_input(h, PIN_A)
    lgpio.gpio_claim_input(h, PIN_B)
except Exception as e:
    print(f"Error connecting to GPIO: {e}")
    sys.exit(1)

count = 0
last_a = lgpio.gpio_read(h, PIN_A)

print("--- ENCODER SYSTEM ACTIVE ---")
print(f"Monitoring BCM {PIN_A} & {PIN_B}")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        # Read the current state of Phase A
        current_a = lgpio.gpio_read(h, PIN_A)
        
        # If Phase A has changed state (Rising or Falling edge)
        if current_a != last_a:
            # Read Phase B to determine direction
            current_b = lgpio.gpio_read(h, PIN_B)
            
            # Quadrature Logic: If A and B are different, we're moving one way
            if current_a != current_b:
                count += 1
            else:
                count -= 1
            
            last_a = current_a
        
        # Calculate revolutions based on your motor's CPR
        revolutions = count / TOTAL_CPR
        
        # Display the results
        # \r keeps the print on the same line for a clean dashboard look
        print(f"Count: {count:6d} | Revs: {revolutions:8.2f}", end='\r')
        
        # Tiny sleep to prevent CPU hogging (1ms polling)
        time.sleep(0.0001)

except KeyboardInterrupt:
    print("\n\nStopping System...")

finally:
    # Always clean up the GPIO chip!
    if 'h' in locals():
        lgpio.gpiochip_close(h)
    print("Cleanup complete. Goodbye.")