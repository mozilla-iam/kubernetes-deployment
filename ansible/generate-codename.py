#!/usr/bin/env python

from faker import Faker

fake = Faker()


if __name__ == "__main__":
    color = fake.safe_color_name()
    day = fake.day_of_month()
    print("{}-{}".format(color, day))
