#!/usr/bin/env python
# coding=utf-8

from os.path import expanduser
from shutil import copy

file_name = 'test.ini'

red = 1
green = 1
blue = 1

brightness = 100

horizontal_strip_led_count = 37
vertical_strip_led_count = 24

real_screen_size_x, real_screen_size_y = 2560, 1600

dominant_vertical_strip = True

change_aspect_ratio = False
desired_aspect_ratio = 2.39  # 2.39/1 (> 1)


def position_correction(stretched_size, original_size):
    return int(stretched_size / 2 - original_size / 2)


def single_led_parameters(
        led_number_, position_x_, position_y_, capture_size_x_,
        capture_size_y_, red_, green_, blue_):
    return "[LED_" + str(led_number_) + "]\n" + \
           "IsEnabled=true\n" \
           "Position=@Point(" + str(position_x_) + " " \
           + str(position_y_) + ")\n" + \
           "Size=@Size(" + str(capture_size_x_) + " " \
           + str(capture_size_y_) + ")\n" + \
           "CoefRed=" + str(red_) + "\n" + \
           "CoefGreen=" + str(green_) + "\n" + \
           "CoefBlue=" + str(blue_) + "\n" + \
           "\n"


if __name__ == '__main__':

    print('Generating profile "' + str(file_name) + '"...')

    total_number_of_leds = \
        2 * horizontal_strip_led_count + 2 * vertical_strip_led_count

    dominant_horizontal_strip = False if dominant_vertical_strip else True

    x_corner_correction = 2 if dominant_vertical_strip else 0
    y_corner_correction = 2 if dominant_horizontal_strip else 0

    if change_aspect_ratio:
        screen_aspect_ratio = real_screen_size_x / real_screen_size_y

        if desired_aspect_ratio >= screen_aspect_ratio:
            screen_size_x = real_screen_size_x
            screen_size_y = \
                int(round(real_screen_size_x / desired_aspect_ratio, 0))
            offset_x = 0
            offset_y = int(round((real_screen_size_y - screen_size_y) / 2, 0))
        else:  # Not working yet
            screen_size_x = \
                int(round(real_screen_size_y / desired_aspect_ratio, 0))
            screen_size_y = real_screen_size_y
            offset_x = int(round((real_screen_size_x - screen_size_x) / 2, 0))
            offset_y = 0
    else:
        screen_size_x = real_screen_size_x
        screen_size_y = real_screen_size_y
        offset_x = 0
        offset_y = 0

    base_capture_size_x = int(round(screen_size_x / (
        horizontal_strip_led_count + x_corner_correction), 0))
    base_capture_size_y = int(round(screen_size_y / (
        vertical_strip_led_count + y_corner_correction), 0))

    overlap_stretch_ratio = 1.5  # 1.5

    horizontal_strip_stretch_ratio = 3.6  # 3.6
    horizontal_strip_capture_size_x = \
        int(overlap_stretch_ratio * base_capture_size_x)
    horizontal_strip_capture_size_y = \
        int(horizontal_strip_stretch_ratio * base_capture_size_y)
    horizontal_strip_x_position_correction = position_correction(
        horizontal_strip_capture_size_x, base_capture_size_x)

    vertical_strip_stretch_ratio = 5.9  # 5.9
    vertical_strip_capture_size_x = \
        int(vertical_strip_stretch_ratio * base_capture_size_x)
    vertical_strip_capture_size_y = \
        int(overlap_stretch_ratio * base_capture_size_y)
    vertical_strip_y_position_correction = position_correction(
        vertical_strip_capture_size_y, base_capture_size_y)

    # Lower by number, not spatially (upper limit in real space)!
    vertical_strip_upper_y_limit = \
        screen_size_y + offset_y - vertical_strip_capture_size_y
    vertical_strip_lower_y_limit = offset_y

    horizontal_lower_y_limit = offset_y

    copy_to_prismatik_profiles_folder = True
    output_file_contents_in_terminal = False

    preamble = \
        "[General]\n" + \
        "LightpackMode=Ambilight\n" + \
        "IsBacklightEnabled=true\n" + \
        "\n" + \
        "[Grab]\n" + \
        "Grabber=DDupl\n" + \
        "IsAvgColorsEnabled=false\n" + \
        "IsSendDataOnlyIfColorsChanges=true\n" + \
        "Slowdown=50\n" + \
        "LuminosityThreshold=3\n" + \
        "IsMinimumLuminosityEnabled=true\n" + \
        "IsDX1011GrabberEnabled=false\n" + \
        "IsDX9GrabbingEnabled=false\n" + \
        "\n" + \
        "[MoodLamp]\n" + \
        "LiquidMode=false\n" + \
        "Color=#00ff00\n" + \
        "Speed=50\n" + \
        "\n" + \
        "[Device]\n" + \
        "RefreshDelay=100\n" + \
        "Brightness=" + str(brightness) + "\n" + \
        "Smooth=100\n" + \
        "Gamma=2.004\n" + \
        "ColorDepth=128\n" + \
        "\n"

    file = open(file_name, 'w')

    file.write(preamble)

    # TOP horizontal strip

    start_top = 1
    end_top = horizontal_strip_led_count

    for overall_led_number in range(start_top, end_top + 1):
        position_x = overall_led_number * base_capture_size_x \
                     - horizontal_strip_x_position_correction
        position_y = horizontal_lower_y_limit
        file.write(
            single_led_parameters(
                overall_led_number,
                position_x,
                position_y,
                horizontal_strip_capture_size_x,
                horizontal_strip_capture_size_y,
                red,
                green,
                blue
            )
        )

    # (facing front of screen) RIGHT vertical strip

    start_right = end_top + 1
    end_right = start_right + (vertical_strip_led_count - 1)
    right_strip_led_number = 1

    for overall_led_number in range(start_right, end_right + 1):

        position_x = screen_size_x - vertical_strip_capture_size_x

        value = (right_strip_led_number - 1) * base_capture_size_y \
                - vertical_strip_y_position_correction + offset_y

        if value <= vertical_strip_upper_y_limit:
            if value >= vertical_strip_lower_y_limit:
                position_y = value
            else:
                position_y = vertical_strip_lower_y_limit
        else:
            position_y = vertical_strip_upper_y_limit

        file.write(
            single_led_parameters(
                overall_led_number,
                position_x,
                position_y,
                vertical_strip_capture_size_x,
                vertical_strip_capture_size_y,
                red,
                green,
                blue
            )
        )
        right_strip_led_number += 1

    # BOTTOM horizontal strip

    start_bottom = end_right + 1
    end_bottom = start_bottom + (horizontal_strip_led_count - 1)
    bottom_strip_led_number = 1

    for overall_led_number in range(start_bottom, end_bottom + 1):
        position_x = screen_size_x \
                     - ((bottom_strip_led_number + 1) * base_capture_size_x) \
                     - horizontal_strip_x_position_correction
        position_y = screen_size_y + offset_y - horizontal_strip_capture_size_y
        file.write(
            single_led_parameters(
                overall_led_number,
                position_x,
                position_y,
                horizontal_strip_capture_size_x,
                horizontal_strip_capture_size_y,
                red,
                green,
                blue
            )
        )
        bottom_strip_led_number += 1

    # (facing front of screen) LEFT vertical strip

    start_left = end_bottom + 1
    end_left = start_left + (vertical_strip_led_count - 1)
    left_strip_led_number = 1

    for overall_led_number in range(start_left, end_left + 1):
        position_x = 0
        y_value = screen_size_y + offset_y \
                  - (left_strip_led_number * base_capture_size_y) \
                  - vertical_strip_y_position_correction
        position_y = y_value if y_value >= vertical_strip_lower_y_limit \
            else vertical_strip_lower_y_limit
        file.write(
            single_led_parameters(
                overall_led_number,
                position_x,
                position_y,
                vertical_strip_capture_size_x,
                vertical_strip_capture_size_y,
                red,
                green,
                blue
            )
        )
        left_strip_led_number += 1

    file.close()

    if end_left != total_number_of_leds:
        print("Number of LEDs don't add up at end!")

    if output_file_contents_in_terminal:
        file = open(file_name, 'r')
        print(file.read())
        file.close()

    if copy_to_prismatik_profiles_folder:
        print("Copying profile to Primatik profiles folder...")
        copy(file_name,
             str(expanduser("~") + '/Prismatik/Profiles/' + file_name))

    print("Complete.")