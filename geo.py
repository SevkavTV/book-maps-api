from opencage.geocoder import OpenCageGeocode
import argparse


def convert_cities_to_coordinates(key):

    geocoder = OpenCageGeocode(key)

    dict_cities = {}

    with open('cities.txt', 'r', encoding="utf-8") as file:
        for line in file:
            if line not in dict_cities:
                geo_result = geocoder.geocode(line)

                if len(geo_result) > 0:
                    coordinates = (geo_result[0]['geometry']['lat'],
                                   geo_result[0]['geometry']['lng'])

                    dict_cities[line] = coordinates
                    print(line, coordinates)

    with open('coordinates.txt', 'w', encoding="utf-8") as file:
        for key, value in dict_cities.items():

            file.write(key[:-1] + ':' + str(value[0]) +
                       ' ' + str(value[1]) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Indicate your key for <OpenCageGeocode> library')
    parser.add_argument(
        '--key', type=str, help='Key for <OpenCageGeocode> library', required=True)
    args = parser.parse_args()
    convert_cities_to_coordinates(args.key)
