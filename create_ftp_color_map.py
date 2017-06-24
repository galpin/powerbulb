# Copyright 2017 Martin Galpin (galpin@gmail.com)
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

from powerbulb.colors import create_ftp_color_map


def main(ftp, output, kind):
    create_ftp_color_map(ftp, kind).save(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Creates a color map based on a specified Functional "
                    "Threshold Power (FTP), specified in W.")
    parser.add_argument('--ftp', type=int, required=True,
                        help='The FTP value, specified in W.')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='The file to which to write the color map.')
    parser.add_argument('--kind', '-k', type=str, required=False, default='discrete',
                        help='The The kind of map (either "discrete" or "continuous").')
    args = parser.parse_args()
    main(args.ftp, args.output, args.kind)
