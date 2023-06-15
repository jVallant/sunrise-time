# Sunrise Timezone

## Goal

Creating a program which crates a timezone based on the sunrise, solar\noon or sunset given a specific coordinate. Add the tz file the system tz files and make it the users timezone.

## Problems:

- Many programs (ex. Browsers) will ignore it as their libaries have tz files build in and they will not lock at system files
- Works for Linux, likely android (if rooted, and file copied from PC) and maybe Mac

## Usage

1. execute 'python sunrise-timezone.py'
2. fill out the questions
3. execute 'sudo zic tmp_raw_timezone.zic' to create the tz file into the system directory (/usr/share/zoneinfo/)
4. execute 'sudo timedatectl set-timezone SunriseTZ' to switch to the timezone (SunriseTZ is the default name)


