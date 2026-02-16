# multimeter/multimeter.py
from machine import ADC
from micropython import const

_u16 = const(2**16)

class Voltmeter:
    """
    Set up an ADC to measure voltage.
    """
    r1 = None
    r2 = None
    def __init__(self, pin:int, r1:int|float|None, r2:int|float|None, v_sys:float|int=3.3) -> None:
        """
        Initialize the voltmeter
        :param pin: The ADC-pin number to use (remember to use AGND for ground). It's one of 26, 27, 28 on RP2
        :type pin: int
        :param r1: The resistance [ohm] in the first resistor (going from source -> ADC). None if directly connected (source must be below V_SYS if connected directly!).
        :type r1: int|float|None
        :param r2: The resistance [ohm] in the second resistor (going from ADC -> AGND). None if directly connected (source must be below V_SYS if connected directly!).
        :type r2: int|float|None
        :param v_sys: The system (reference) voltage (Likely 3.3 V)
        :type v_sys: float|int
        """
        self.adc = ADC(pin)
        if r1 is not None and r2 is not None:
            self.r1 = r1
            self.r2 = r2
        self.v_sys = v_sys

    def voltage_raw(self) -> float:
        """
        Get the calculated input voltage at the ADC-pin.
        :return: Voltage [V]
        :rtype: float
        """
        return self.adc.read_u16() * self.v_sys / _u16

    def _calibrate(self, val:int|float) -> float:
        if self.r1 is None or self.r2 is None:
            return val * self.v_sys / _u16
        else:
            return val * self.v_sys / _u16 * (self.r1 + self.r2) / self.r2

    def voltage_calibrated(self) -> float:
        """
        Get the calibrated (source) voltage.
        :return: Voltage [V] at the source
        :rtype: float
        """
        return self._calibrate(self.adc.read_u16())

    def mean(self, n:int=10, calibrate:bool=True) -> float:
        """
        Get the mean voltage over a series of measurements.
        :param n: The number of measurements to average
        :type n: int
        :param calibrate: If True, the value will be the source voltage. Else, the value will be from the ADC-pin
        :type calibrate: bool
        :return: The voltage at the source or ADC-pin averaged over n measurements.
        :rtype: float
        """
        out = 0
        for _ in range(n):
            out += self.adc.read_u16()
        if calibrate:
            return self._calibrate(out / n)
        return out / n
