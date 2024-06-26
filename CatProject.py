# Import required Python libraries
import RPi.GPIO as GPIO
import time
import sys
import RPi.GPIO as GPIO
from hx711 import HX711

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_PIR = 25

in1 = 27 #22
in2 = 23 #25
in3 = 22 #6
in4 = 24 #5

def cleanAndExit():
    print("Cleaning...")
        
    print("Bye!")
    sys.exit()

hx = HX711(5, 6)

hx.set_reading_format("MSB", "MSB")

print("PIR Module Test (CTRL-C to exit)")

# careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
step_sleep = 0.002

# defining stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
step_sequence = [[1,0,0,1],
                 [1,0,0,0],
                 [1,1,0,0],
                 [0,1,0,0],
                 [0,1,1,0],
                 [0,0,1,0],
                 [0,0,1,1],
                 [0,0,0,1]]

# Set pin as input
GPIO.setup(GPIO_PIR,GPIO.IN)      # Echo

# setting up
GPIO.setmode( GPIO.BCM )
GPIO.setup( in1, GPIO.OUT )
GPIO.setup( in2, GPIO.OUT )
GPIO.setup( in3, GPIO.OUT )
GPIO.setup( in4, GPIO.OUT )

# initializing
GPIO.output( in1, GPIO.LOW )
GPIO.output( in2, GPIO.LOW )
GPIO.output( in3, GPIO.LOW )
GPIO.output( in4, GPIO.LOW )

def cleanup():
    GPIO.output( in1, GPIO.LOW )
    GPIO.output( in2, GPIO.LOW )
    GPIO.output( in3, GPIO.LOW )
    GPIO.output( in4, GPIO.LOW )
    GPIO.cleanup()
    
while True:
  
   motor_pins = [in1,in2,in3,in4]
   motor_step_counter = 0

   Current_State  = 0
   Previous_State = 0

   referenceUnit = 114
   #hx.set_reference_unit(referenceUnit)
   
   step_count = 2048 # 5.625*(1/64) per step, 4096 steps is 360
  
   try:
     print("Waiting for PIR to settle ...")

     # Loop until PIR output is 0
     while GPIO.input(GPIO_PIR)==1:
       Current_State  = 0

     print("Ready")

     # Loop until users quits with CTRL-C
     while True :
       # Read PIR state
       Current_State = GPIO.input(GPIO_PIR)
       #print(GPIO.input(GPIO_PIR))

       if Current_State==1 and Previous_State==0:
         # PIR is triggered
         print ("Motion detected!")
         hx.reset()
         hx.tare()
         print("Tare done! Add weight now...")
         try:
            val = hx.get_weight(5)
            print(val)
        
            hx.power_down()
            hx.power_up()
            time.sleep(0.1)

         except (KeyboardInterrupt, SystemExit):
            cleanAndExit()
         if(val > 100000):
            # the meat
            try:
                i = 0
                for i in range(1024):
                    for pin in range(0, len(motor_pins)):
                        GPIO.output( motor_pins[pin], step_sequence[motor_step_counter][pin] )
                    motor_step_counter = (motor_step_counter - 1) % 8
                    time.sleep( step_sleep )
                val_cur = val
                while (val_cur > val-100000):
                    try:        
                        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
                        val_cur = hx.get_weight(5)
                        print(val_cur)
                        hx.power_down()
                        hx.power_up()
                        time.sleep(0.1)
                    except (KeyboardInterrupt, SystemExit):
                        cleanAndExit()
                for i in range(1024):
                    for pin in range(0, len(motor_pins)):
                        GPIO.output( motor_pins[pin], step_sequence[motor_step_counter][pin] )
                    motor_step_counter = (motor_step_counter + 1) % 8
                    time.sleep( step_sleep )
            except KeyboardInterrupt:
                cleanup()
                exit( 1 )
            #cleanup()
            #exit( 0 )
         else:
           print("The cat food is running out!")
         # Record previous state
         Previous_State=1
       elif Current_State==0 and Previous_State==1:
         # PIR has returned to ready state
         print("Ready")
         Previous_State=0

       # Wait for 10 milliseconds
       time.sleep(0.01)

   except KeyboardInterrupt:
     print("Quit")
     # Reset GPIO settings
     GPIO.cleanup()
