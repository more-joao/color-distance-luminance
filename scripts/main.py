from matplotlib.image import imread
from matplotlib import pyplot as plt
import numpy as np
import math
import time

# everything is rounded to 4 decimal places

def get_matrix(image_path, mode='export'): # if mode is anything else -> no file will be created | image must be jpg
    print('calculating matrix...')
    array = imread(image_path)
    if mode == 'export':
        with open('C:/Users/pote1/python/2_projects/painting_data_analysis/test_images/data.txt', 'w+') as data:
            for x in array:
                for y in x:
                    data.write(f"{y[0],y[1],y[2]};")
                data.write("\n")
    return array


def gen_image(file='', matrix=None):
    if matrix is None:
        with open(file, "r+") as data:
            rows = data.readlines()
            n_columns = len(rows[0].split(';'))-1  # adjust for trailing semicolon
            matrix = np.zeros((len(rows), n_columns, 3), dtype=int)
            for i, row in enumerate(rows):
                for j, col in enumerate(row.split(';')[0:n_columns]):
                    matrix[i][j] = [float(x.strip(' ')) for x in col.split('(')[1].split(')')[0].split(',')]
    else:
        plt.imshow(matrix, interpolation='nearest')
        plt.show()
        

# distance functions


def manhattan_distance(colors=[(0, 0, 0), (0, 0, 0)]):
    r_diff = abs(colors[0][0] - colors[1][0])
    g_diff = abs(colors[0][1] - colors[1][1])
    b_diff = abs(colors[0][2] - colors[1][2])
    distance = (r_diff + g_diff + b_diff)
    return round(distance, 4)


def canberra_distance(colors=[(0, 0, 0), (0, 0, 0)]):
    distance = 0
    for x in range(0, 3):
        numerator = abs(colors[0][x]-colors[1][x])
        denominator = abs(colors[0][x]+colors[1][x])
        if denominator == 0:
            term = 0
        else:
            term = numerator/denominator
        distance += term
    return round(distance, 4)


def euclidean_distance(colors=[(0, 0, 0), (0, 0, 0)]):
    distance = math.sqrt((colors[0][0]-colors[1][0])**2 + (colors[0][1]-colors[1][1])**2 + (colors[0][2]-colors[1][2])**2)
    return distance


def queenwise_distance(colors=[(0, 0, 0), (0, 0, 0)]):
    distances = []
    for x in range(0, 3):
        distances.append(abs(colors[0][x]-colors[1][x]))
    return max(distances)


def calculate_luminance(color=(0, 0, 0)):
    nr = color[0]/255
    ng = color[1]/255
    nb = color[2]/255

    # gamma correction
    nr =  nr/12.92 if nr <= 0.03928 else ((nr+0.055)/1.055)**2.4
    ng = ng/12.92 if ng <= 0.03928 else ((ng+0.055)/1.055)**2.4
    nb = nb/12.92 if nb <= 0.03928 else ((nb+0.055)/1.055)**2.4

    lum = 0.2126*nr + 0.7152*ng + 0.0722*nb

    return round(lum, 4)


def color_classification(matrix, basis, tolerance=0.5, print_mode=True, name=None, output_folder=None):
    print(f'classifying colors for {name}; dimensions: {matrix.shape[1]}x{matrix.shape[0]}')
    start = time.time()

    if print_mode is False:
        with open(f'{output_folder}/luminance_data_{name}.txt', 'w+') as lum_file:
            lum_file.write(f'group_and_title,luminance_class,lum_class_length,mean_distance,max_distance,min_distance,dist_class_span\n')
        with open(f'{output_folder}/distance_data_{name}.txt', 'w+') as dist_file:
            dist_file.write(f'group_and_title,distance_class,dist_class_len,mean_luminance,max_luminance,min_luminance\n')
    
    distances = []
    luminances = []

    for row in matrix:
        for color in row:
            distances.append((round(canberra_distance([color, basis]), 5), tuple(color)))
            luminances.append((calculate_luminance(tuple(color)), tuple(color)))

    print('calculated luminances and distances')

    distances = sorted(distances)
    luminances = sorted(luminances)

    # classify colors into distance groups
    ordered_distances = {}
    for d, color in distances:
        added = False
        for key in ordered_distances:
            if abs(key - d) <= tolerance:
                ordered_distances[key].append((d, color)) if (d, color) not in ordered_distances[key] else None
                added = True
                break
        if not added:
            ordered_distances[d] = [(d, color)]

    # classify colors into luminance groups
    ordered_luminances = {}
    for l, color in luminances:
        added = False
        for key in ordered_luminances:
            if abs(key - l) <= tolerance:
                ordered_luminances[key].append((l, color)) if (l, color) not in ordered_luminances[key] else None
                added = True
                break
        if not added:
            ordered_luminances[l] = [(l, color)]

    print('classes determined')

    if print_mode:
        print(f'{len(ordered_distances)} distance classes for {tolerance} tolerance.')
        print(f'{len(ordered_luminances)} luminance classes for {tolerance} tolerance.')
        print(f'predominant white distance: {max([ordered_distances[c] for c in ordered_distances], key=len)[0][0]}')
        print(f'predominant lumimance: {max([ordered_luminances[c] for c in ordered_luminances], key=len)[0][0]}')
    else:
        with open(f'{output_folder}/group_data.txt', 'a+') as group_file:
            group_file.write(f'{tolerance},{name},{len(ordered_distances)},{max([ordered_distances[c] for c in ordered_distances], key=len)[0][0]},{len(ordered_luminances)},{max([ordered_luminances[c] for c in ordered_luminances], key=len)[0][0]}\n')
    
    intersections = {}
    for lum in ordered_luminances:
        intersections[lum] = []
        for dist in ordered_distances:
            if len([z for z in [y[1] for y in ordered_luminances[lum]] if z in [x[1] for x in ordered_distances[dist]]]) != 0:
                intersections[lum].append(dist)
            #print(f'luminance: {lum, len(ordered_luminances[lum])}, distance: {dist, len(ordered_distances[dist])}, intersection: {[x[1] for x in ordered_luminances[lum] if x[1] in [y[1] for y in ordered_distances[dist]] and x[1] in [z[1] for z in ordered_luminances[lum]]]}')

    print('intersections calculated')

    if print_mode is False:
        with open(f'{output_folder}/distance_data_{name}.txt', 'a+') as dist_file:
            for cl in ordered_distances:
                luminances = []
                for color in ordered_distances[cl]:
                    luminances.append(round(calculate_luminance(color[1]), 4))
                dist_file.write(f'{name},{cl},{len(ordered_distances[cl])},{round(sum(luminances)/len(luminances), 4)},{max(luminances)},{min(luminances)}\n')
            
        print('distance data exported')
        with open(f'{output_folder}/luminance_data_{name}.txt', 'a+') as lum_file:
            for cl in ordered_luminances:
                distances = []
                for color in ordered_luminances[cl]:
                    distances.append(round(canberra_distance([color[1], (255, 255, 255)]), 4))
                lum_file.write(f'{name},{cl},{len(ordered_luminances[cl])},{round(sum(distances)/len(distances), 4)},{max(distances)},{min(distances)},({max(intersections[cl])} - {min(intersections[cl])})\n')
        print('luminance data exported')

    else:
        for cl in ordered_distances:
            luminances = []
            for color in ordered_distances[cl]:
                luminances.append(round(calculate_luminance(color[1]), 4))
            print(f'distance class: {cl} | class length: {len(ordered_distances[cl])} | mean luminance: {round(sum(luminances)/len(luminances), 4)} | max luminance: {max(luminances)} | min luminance: {min(luminances)}')
            
        for cl in ordered_luminances:
            distances = []
            for color in ordered_luminances[cl]:
                distances.append(round(canberra_distance([color[1], (255, 255, 255)]), 4))
            print(f'luminance class: {cl} | class length: {len(ordered_luminances[cl])} | mean distance: {round(sum(distances)/len(distances), 4)} | max distance: {max(sorted(distances))} | min distance: {min(sorted(distances))} | d_class_span: {max(intersections[cl])} - {min(intersections[cl])}')
        
    end = time.time()
    print(f'time elapsed: {round((end-start)/60, 4)} minutes.\n')


def image_group_analysis(sources=[], group_name='no_name', output_folder=None):
    with open(f'{output_folder}/group_data.txt', 'w+') as group_file:
        group_file.write('tolerance,group+title,n_distance_classes,predom_dist_class,n_luminance_classes,predom_lum_class\n')
    for i,src in enumerate(sources):
        matrix = get_matrix(image_path=src, mode='nan')
        color_classification(matrix=matrix, basis=(255, 255, 255), tolerance=0.05, print_mode=False, name=group_name+f'_{src.split("/")[-1].split(".")[0]}', output_folder=output_folder)


from os import listdir
onlyfiles = [f for f in listdir('somepath')]

group_path = 'somepath'
actual_group = [group_path+x for x in onlyfiles]

#image_group_analysis(actual_group, group_name='group3', output_folder="somefolder")
