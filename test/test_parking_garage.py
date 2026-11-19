from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
from unittest.mock import MagicMock

import mock.GPIO as GPIO
import parking_garage
from mock.SDL_DS3231 import SDL_DS3231
from src.parking_garage import ParkingGarage
from src.parking_garage import ParkingGarageError

class TestParkingGarage(TestCase):

    @patch.object(GPIO, "setup")
    def test_detection_sensors_configuration(self, mock_setup: MagicMock):
        parking_garage = ParkingGarage()
        mock_setup.assert_any_call(ParkingGarage.INFRARED_PIN1, GPIO.IN)
        mock_setup.assert_any_call(ParkingGarage.INFRARED_PIN2, GPIO.IN)
        mock_setup.assert_any_call(ParkingGarage.INFRARED_PIN3, GPIO.IN)

    @patch.object(GPIO, "input")
    def test_check_occupancy_car_detected(self, mock_input: MagicMock):
        mock_input.return_value = False
        parking_garage = ParkingGarage()
        occupied = parking_garage.check_occupancy(ParkingGarage.INFRARED_PIN1)
        self.assertTrue(occupied)

    @patch.object(GPIO, "input")
    def test_check_occupancy_car_not_detected(self, mock_input: MagicMock):
        mock_input.return_value = True
        parking_garage = ParkingGarage()
        occupied = parking_garage.check_occupancy(ParkingGarage.INFRARED_PIN1)
        self.assertFalse(occupied)

    def test_check_occupancy_raises_error(self):
        parking_garage = ParkingGarage()
        self.assertRaises(ParkingGarageError, parking_garage.check_occupancy, ParkingGarage.SERVO_PIN)

    @patch.object(GPIO, "input")
    def test_get_number_occupied_spots_garage_full(self, mock_input: MagicMock):
        mock_input.side_effect = [False, False, False]
        parking_garage = ParkingGarage()
        n_spots = parking_garage.get_number_occupied_spots()
        self.assertEqual(3, n_spots)

    @patch.object(GPIO, "input")
    def test_get_number_occupied_spots_garage_not_full(self, mock_input: MagicMock):
        mock_input.side_effect = [False, True, False]
        parking_garage = ParkingGarage()
        n_spots = parking_garage.get_number_occupied_spots()
        self.assertEqual(2, n_spots)

    @patch.object(SDL_DS3231, "__init__", return_value = None)
    def test_rtc_configuration(self, mock_rtc: MagicMock):
        parking_garage = ParkingGarage()
        mock_rtc.assert_called_once()

    @patch.object(SDL_DS3231, "read_datetime")
    def test_calculate_parking_fee_full_hours(self, mock_exit_time: MagicMock):
        mock_exit_time.return_value = datetime(2026, 11, 19, 10, 11)
        parking_garage = ParkingGarage()
        entry_time = datetime(2026, 11, 19, 8, 11)
        fee = parking_garage.calculate_parking_fee(entry_time)
        self.assertEqual(5, fee)

    @patch.object(SDL_DS3231, "read_datetime")
    def test_calculate_parking_fee_fraction_hours(self, mock_exit_time: MagicMock):
        mock_exit_time.return_value = datetime(2026, 11, 19, 10, 12)
        parking_garage = ParkingGarage()
        entry_time = datetime(2026, 11, 19, 8, 11)
        fee = parking_garage.calculate_parking_fee(entry_time)
        self.assertEqual(7.5, fee)

    @patch.object(GPIO, "setup")
    @patch.object(GPIO.PWM, "__init__", return_value = None)
    @patch.object(GPIO.PWM, "start")
    def test_servo_configuration(self, mock_start:MagicMock, mock_pwm:MagicMock, mock_setup: MagicMock):
        parking_garage = ParkingGarage()
        mock_setup.assert_any_call(ParkingGarage.SERVO_PIN, GPIO.OUT)
        mock_pwm.assert_any_call(ParkingGarage.SERVO_PIN, 50)
        mock_start.assert_any_call(5)
        self.assertFalse(parking_garage.door_open)

    @patch.object(GPIO.PWM, "ChangeDutyCycle")
    def test_open_garage_door(self, mock_change: MagicMock):
        parking_garage = ParkingGarage()
        parking_garage.door_open = False
        parking_garage.open_garage_door()
        mock_change.assert_called_once_with(10)
        self.assertTrue(parking_garage.door_open)

    @patch.object(GPIO.PWM, "ChangeDutyCycle")
    def test_close_garage_door(self, mock_change: MagicMock):
        parking_garage = ParkingGarage()
        parking_garage.door_open = True
        parking_garage.close_garage_door()
        mock_change.assert_called_once_with(5)
        self.assertFalse(parking_garage.door_open)

    @patch.object(GPIO, "setup")
    def test_red_light_configuration(self, mock_setup: MagicMock):
        parking_garage = ParkingGarage()
        mock_setup.assert_any_call(ParkingGarage.LED_PIN, GPIO.OUT)
        self.assertFalse(parking_garage.red_light_on)

    @patch.object(GPIO, "output")
    def test_turn_on_red_light(self, mock_output: MagicMock):
        parking_garage = ParkingGarage()
        parking_garage.turn_on_red_light()
        mock_output.assert_called_once_with(ParkingGarage.LED_PIN, True)
        self.assertTrue(parking_garage.red_light_on)

    @patch.object(GPIO, "output")
    def test_turn_off_red_light(self, mock_output: MagicMock):
        parking_garage = ParkingGarage()
        parking_garage.red_light_on = True
        parking_garage.turn_off_red_light()
        mock_output.assert_called_once_with(ParkingGarage.LED_PIN, False)
        self.assertFalse(parking_garage.red_light_on)

