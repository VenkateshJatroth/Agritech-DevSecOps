import pytest
from sensor import Sensor

# Test 1: Check if a new sensor is born healthy
def test_initial_state():
    # Create a fake sensor for testing
    my_sensor = Sensor("Test Lab")
    
    # Assert checks if True. If False, the test fails.
    assert my_sensor.battery == 100       # Should start full
    assert my_sensor.location == "Test Lab" # Should remember name

# Test 2: Check if reading data drains battery
def test_battery_drain():
    my_sensor = Sensor("Field A")
    
    # Take a reading
    data = my_sensor.read_data()
    
    # The battery should be slightly less than 100 now (99.9)
    assert my_sensor.battery < 100
    assert my_sensor.battery == 99.9

# Test 3: Check if data format is correct
def test_data_structure():
    my_sensor = Sensor("Field B")
    data = my_sensor.read_data()
    
    # Check if we got the keys we expect
    assert "temp" in data
    assert "hum" in data
    assert "battery" in data
    
    # Check if temp is within realistic bounds (20-35 as per your code)
    assert 20 <= data["temp"] <= 35
