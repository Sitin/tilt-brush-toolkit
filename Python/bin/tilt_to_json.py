#!/usr/bin/env python

# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import json
import os

from tiltbrush.tilt import Tilt


DEFAULT_AUTHOR = ''
DEFAULT_BRUSH_TYPE = 'smooth'
DEFAULT_BRUSH_SIZE = 0.25


def get_args():
    parser = argparse.ArgumentParser(description="Convert a .tilt file to A-Painter JSON format")
    parser.add_argument('files', type=str, nargs='+', help="Files to convert")
    parser.add_argument('--author', type=str, default=DEFAULT_AUTHOR, help="Author of the files")
    parser.add_argument('--brush_type', type=str, default=DEFAULT_BRUSH_TYPE,
                        help="Brush type (currently we support only one brush type for all strokes)")
    parser.add_argument('--brush_size', type=str, default=DEFAULT_BRUSH_SIZE,
                        help="Brush type (currently we support only one brush size for all strokes)")

    return parser.parse_args()


def parse_stroke(stroke, brush_size=DEFAULT_BRUSH_SIZE):
    timestamp_idx = stroke.cp_ext_lookup['timestamp']
    pressure_idx = stroke.cp_ext_lookup['pressure']

    control_points = []
    for cp in stroke.controlpoints:
        control_points.append({
            'position': cp.position,
            'orientation': cp.orientation,
            'timestamp': cp.extension[timestamp_idx],
            'pressure': cp.extension[pressure_idx],
        })

    parsed_stroke = {
        'brush': {
            'index': stroke.brush_idx,
            'color': stroke.brush_color,
            'size': brush_size
        },
        'points': control_points
    }

    return parsed_stroke


def save_as_json(tilt, out_filename, author=DEFAULT_AUTHOR, brush_type=DEFAULT_BRUSH_TYPE, brush_size=DEFAULT_BRUSH_SIZE):
    json_data = {
        'version': 1,
        'author': author,
        'strokes': [parse_stroke(s, brush_size=brush_size) for s in tilt.sketch.strokes],
        'brushes': [brush_type for _ in tilt.metadata['BrushIndex']]
    }

    with open(out_filename, 'w') as out:
        json.dump(json_data, out)


def main():
    args = get_args()

    print('-' * 60)
    print('Tilt Brush to A-Painter JSON.')
    print('author="{author}", brush_type={brush_type}, brush_size={brush_size}'
          .format(author=args.author, brush_type=args.brush_type, brush_size=args.brush_size))
    print('-' * 60)

    for filename in args.files:
        tilt = Tilt(filename)
        out_filename = os.path.splitext(tilt.filename)[0] + '.json'
        save_as_json(tilt, out_filename,
                     author=args.author, brush_type=args.brush_type, brush_size=args.brush_size)
        print('Converted: "{tiltfile}" to "{jsonfile}"'.format(tiltfile=filename, jsonfile=out_filename))

    print('{} files converted.'.format(len(args.files)))

if __name__ == '__main__':
    main()
