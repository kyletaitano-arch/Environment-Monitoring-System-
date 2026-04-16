import time
import smbus


try:
    import smbus  # type: ignore
except ImportError:
    class SMBus:
        def __init__(self, bus): pass
        def write_i2c_block_data(self, addr, cmd, vals): pass
        def read_i2c_block_data(self, addr, cmd, length): return [0]*length

    smbus = type('smbus', (), {'SMBus': SMBus})


SGP40_ADDRESS = 0x59
bus = smbus.SMBus(1)

# SGP40 command
MEASURE_RAW = [0x26, 0x0F]


# ----------------------------
# CRC8 (required by sensor)
# ----------------------------
def crc8(data):
    crc = 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x31
            else:
                crc <<= 1
            crc &= 0xFF
    return crc


# ----------------------------
# Humidity conversion (%RH -> ticks)
# ----------------------------
def humidity_to_sgp40_format(rh):
    return int(rh * 65535 / 100)


# ----------------------------
# MAIN: Read SRAW VOC
# ----------------------------
def read_voc_raw(humidity_percent=50.0):
    # Humidity conversion
    hum_scaled = humidity_to_sgp40_format(humidity_percent)
    hum_msb = (hum_scaled >> 8) & 0xFF
    hum_lsb = hum_scaled & 0xFF
    hum_crc = crc8([hum_msb, hum_lsb])

    # Fake temperature = 25xB0C (required by SGP40)
    temp_scaled = int((25 + 45) * 65535 / 175)
    temp_msb = (temp_scaled >> 8) & 0xFF
    temp_lsb = temp_scaled & 0xFF
    temp_crc = crc8([temp_msb, temp_lsb])

    # Send measurement command
    bus.write_i2c_block_data(
        SGP40_ADDRESS,
        MEASURE_RAW[0],
        [
            MEASURE_RAW[1],
            hum_msb, hum_lsb, hum_crc,
            temp_msb, temp_lsb, temp_crc
        ]
    )

    time.sleep(0.05)

    # Read response (MSB, LSB, CRC)
    data = bus.read_i2c_block_data(SGP40_ADDRESS, 0x00, 3)

    raw = (data[0] << 8) | data[1]

    # CRC check
    if crc8(data[:2]) != data[2]:
        print("CRC error detected")

    return raw


# ----------------------------
# TEST LOOP
# ----------------------------
if __name__ == "__main__":
    while True:
        voc_raw = read_voc_raw(humidity_percent=50.0)
        print(f"SRAW VOC: {voc_raw}")
        time.sleep(1)