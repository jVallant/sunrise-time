import time
from math import pi, sin, cos, tan, acos, radians, degrees
import os
from datetime import datetime

standard_input = ['48.2082','16.3738', 'r', '2:00', '','SunriseTZ'] # Vienna

tmp_file='tmp_raw_timezone.zic'
months=['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


offset=24
def main() -> None:
    # ------------- inputs -------------
    print(f'Sunrise timezone creator \n')

    latitude = float(input('Your location (latitude, N is positive S is negative) '))
    assert -180<latitude<180, f'Input: {latitude} allowed inputs: -180<latitude<180' 
    longitude = float(input('Your location (longitude, E is positive, w is negative): '))
    assert -180<longitude<180, f'Input: {longitude} allowed inputs: -180<longitude<180' 

    sunrise_set_noon = input('base time on r: sunrise, s: sunset or n: solar noon: ').lower()
    sunrise_set_noon = sunrise_set_noon.replace('sunrise', 'r').replace('sunset', 's').replace('solar noon','n')
    assert sunrise_set_noon in {'r','s','n'}, f'Input: {sunrise_set_noon}, allowed inputs: r, s, n, sunset, sunrise, solar noon'

    start_time = input('time at sunrise/sunset (default: 6:00 in 24h format): ')
    if start_time == '':
        start_time = '6:00'
    try: 
        start_time = time.strptime(start_time, '%H:%M')
    except: 
        start_time = time.strptime(start_time, '%H:%M:%S')

    recalibration_time = input('time when clock time is changed (default: -120 in min before sunrise): ')
    if recalibration_time == '':
        recalibration_time = '-120'
    recalibration_time = float(recalibration_time)

    timezoneName= input('Timezone Name: ')
    if recalibration_time == '':
        recalibration_time = 'SunriseTZ'
    #assert timezoneName!=''

    startYear=str(datetime.now().year) 
    endYear=str(datetime.now().year+2) # maximum of 500 time changes, otherwise there is some weird behavior (500/256 ~=2)

    # ------------- processing -------------
    file=open(tmp_file, 'w')
    file.write('# SunriseTimezone\n')
    file.write('# Rule NAME FROM TO - IN ON AT SAVE LETTER/S\n')
    for day, sunrise in sunrise_calculator(2013,latitude,longitude,sunrise_set_noon): 
        if day.tm_yday%2==0: # needs to skip every other day otherwise there are too many lines (limit is 256) https://codebrowser.dev/glibc/glibc/timezone/zic.c.html#2987 -> https://codebrowser.dev/glibc/glibc/timezone/tzfile.h.html#111
            continue 
        #            Rule  NAME  FROM  TO  TYPE  IN  ON  AT  SAVE  LETTER/S
        file.write(f'Rule Rule {startYear} {endYear} - {months[day.tm_mon]} {day.tm_mday:2} {int((-sunrise+recalibration_time)//60)+offset:2}:{int((sunrise+recalibration_time)%60):02} {-int(sunrise//60)+offset:2}:{int(sunrise%60):02}:{int(sunrise%1*60):02} - \n')
    file.write('# Zone NAME STDOFF RULES FORMAT [UNTIL]\n')
    file.write(f'Zone {timezoneName} {start_time.tm_hour-offset}:{start_time.tm_min:02} Rule SUN{sunrise_set_noon.capitalize()}\n')
    file.close()

    # ------------- done -------------
    print(f'\nPlease execute command: sudo zic {tmp_file}')
    print(f'and the command: sudo timedatectl set-timezone {timezoneName}\n')

    #os.system(f'zic -v {tmp_file}') # needs sudo 
    #print(open(tmp_file).read())
    
    if input('Remove tmp file [Y/n]:') in ['','y','Y','yes','Yes']:
        os.remove(tmp_file)
        print('tmp file deleted')

def sunrise_calculator(year: int, latitude_deg: float, longitude_deg: float, sunrise:str = 'r')  -> list[tuple[time.struct_time, float]]: # returns sunrises of the year in utc
    latitude = radians(latitude_deg)
    longitude = radians(longitude_deg)
    days_per_year=365
    hour_offset=0
    if year %4==0: # is leap year
        days_per_year=366
    else:
        # !!!!!!!!!!!!!!!!!!!!! following hour offset may be incorrect
        hour_offset=year %4 * 6 # hour offset due to having leap year

    #source: https://gml.noaa.gov/grad/solcalc/solareqns.PDF
    def calculator(day: int) -> float:
        # note: the sun rising later in Jan than in Dec is not a bug! 
        fractional_year= 2*pi/days_per_year*(day-1+(hour_offset-12)/24) # in rad
        equation_of_time = 229.18*(0.000075 + 0.001868*cos(fractional_year) - 0.032077*sin(fractional_year) - 0.014615*cos(2*fractional_year)- 0.040849*sin(2*fractional_year)) # in min
        declination = 0.006918 - 0.399912*cos(fractional_year) + 0.070257*sin(fractional_year) - 0.006758*cos(2*fractional_year) + 0.000907*sin(2*fractional_year) - 0.002697*cos(3*fractional_year) + 0.00148*sin (3*fractional_year) # in rad
        hour_angle  = acos(cos(1.58533492)/(cos(latitude)* cos(declination))- tan(latitude) * tan(declination)) # in rad. 1.58533492rad = 90.833deg
        if sunrise== 'r': # sunrise
            return 720 - 4*degrees(longitude + hour_angle) - equation_of_time #  in min
        if sunrise == 's': # sunset
            return 720 - 4*degrees(longitude - hour_angle ) - equation_of_time #  in min
        if sunrise == 'n': # solar noon
            return 720 - 4*longitude_deg - equation_of_time #  in min
        raise Exception 
    
    return [(time.strptime(str(d),'%j'),  calculator(d)) for d in range(1,days_per_year+1)]


if __name__ == '__main__':
    main()
