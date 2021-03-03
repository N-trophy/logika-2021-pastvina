from unittest import TestCase
import subprocess


def int_to_roman(num: int):
    """
    Converts an integer into a roman number
    :param num: integer to convert
    :return: roman number
    """
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num


class RomanTestCase(TestCase):
    def test_trivial(self):
        pairs = [
            (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
            (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
            (10, "X"), (9, "IX"), (5, "V"), (4, "IV"),
            (1, "I")
        ]

        for num, rom in pairs:
            self.assertEqual(int_to_roman(num), rom)

    def test_random(self):
        pairs = [
            (1909, "MCMIX"), (150, "CL"), (350, "CCCL"),
        ]

        for num, rom in pairs:
            self.assertEqual(int_to_roman(num), rom)
