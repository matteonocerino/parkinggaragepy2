from datetime import datetime

try:
    import RPi.GPIO as GPIO
except:
    import mock.GPIO as GPIO

try:
    import SDL_DS3231
except:
    import mock.SDL_DS3231 as SDL_DS3231

class ParkingGarage:

    # Pin number declarations
    INFRARED_PIN1 = 11
    INFRARED_PIN2 = 12
    INFRARED_PIN3 = 13
    SERVO_PIN = 16
    LED_PIN = 18

    def __init__(self):
        # See User Stories #1, #3-5
        GPIO.setmode(GPIO.BOARD) # Set the numbering schema to bord mode
        GPIO.setwarnings(False)
        self.rtc = SDL_DS3231.SDL_DS3231()
        self.servo = GPIO.PWM(self.SERVO_PIN, 50)
        self.servo.start(5)
        self.door_open = False
        self.red_light_on = False
        GPIO.setup(self.INFRARED_PIN1, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN2, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN3, GPIO.IN)
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        GPIO.setup(self.LED_PIN, GPIO.OUT)


    def check_occupancy(self, pin: int) -> bool:
        if pin in (self.INFRARED_PIN1, self.INFRARED_PIN2, self.INFRARED_PIN3):
            return not GPIO.input(pin)
        raise ParkingGarageError

    def get_number_occupied_spots(self) -> int:
        count = 0
        for pin in [self.INFRARED_PIN1, self.INFRARED_PIN2, self.INFRARED_PIN3]:
            if self.check_occupancy(pin):
                count += 1
        return count

    def calculate_parking_fee(self, entry_time: datetime) -> float:
        entry_hours = entry_time.hour
        exit_time = self.rtc.read_datetime()
        exit_hours = exit_time.hour
        tot = exit_hours - entry_hours

        exit_minutes = exit_time.minute
        entry_minutes = entry_time.minute
        if exit_minutes > entry_minutes:
            tot += 1

        return tot * 2.5

    def open_garage_door(self) -> None:
        self.servo.ChangeDutyCycle(10)
        self.door_open = True

    def close_garage_door(self) -> None:
        self.servo.ChangeDutyCycle(5)
        self.door_open = False

    def turn_on_red_light(self) -> None:
        GPIO.output(self.LED_PIN, True)
        self.red_light_on = True

    def turn_off_red_light(self) -> None:
        GPIO.output(self.LED_PIN, False)
        self.red_light_on = False

    def manage_red_light(self) -> None:
        # See User Story #6
        pass


    # This method is meant to show you how to release the hardware resources when the program running on real hardware ends.
    def cleanup(self) -> None:
        self.servo.stop() # Stops generating PWM on the pin
        GPIO.cleanup() # Resets every GPIO pin


class ParkingGarageError(Exception):
    pass
