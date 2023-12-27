import csv, os, json, struct, sys
import struct
import argparse

class File_Collector:
    def __init__(self):
        self.file_dict = {}
        self.active_fn = ''
        self.tmp_files_folder = 'tmp_files'
        os.makedirs(self.tmp_files_folder, exist_ok=True)
        self.processed_files = [ filename.name[:-5] for filename in os.scandir(self.tmp_files_folder) if filename.is_file() ]
    def parse_line(self, line):
        if line[' Message Id'] == ' C20':
            bytes_payload = bytes.fromhex(line[' Data'])
            mode, ses_id,bs, offset = struct.unpack('<BBHI', bytes_payload[:8])
            fn = bytes_payload[10:].decode()
            print(f'Found header for filename: {fn}')
            self.active_fn = fn
            joined_path_to_tmp = os.path.join(self.tmp_files_folder, f'{fn}.json')
            if os.path.exists(joined_path_to_tmp):
                print('Collecting already received file')
                with open(joined_path_to_tmp, 'r') as fp:
                    self.file_dict = json.load(fp)
            else:
                print('Receiving as new file')
                self.file_dict['meta'] = { 'bs': bs, 'fn': fn }
                self.file_dict['data'] = {}
        elif line[' Message Id'] == ' C2B':
            if self.active_fn != '':
                bytes_payload = bytes.fromhex(line[' Data'])
                size  = struct.unpack('<I', bytes_payload)
                self.file_dict['meta']['size'] = (list(size))
        elif line[' Message Id'] == ' C24':
            if self.active_fn != '':
                bytes_payload = bytes.fromhex(line[' Data'])
                offset = str(struct.unpack('<I', bytes_payload[1:5])[0])
                data = line[' Data'][5*2:]
                if offset not in self.file_dict['data'].keys():
                    self.file_dict['data'][offset] = data
                    # print(f"Add new data to file with offset {offset}")
                # print(f'Found data with offset: {offset}, collecting it...')
    def store_in_tmp_file(self):
        # Hack to convert str offset from json to int and sort it
        sorted_data = sorted(self.file_dict['data'].items(), key=lambda x: int(x[0]))
        self.file_dict['data'] = dict(sorted_data)
        with open(os.path.join(self.tmp_files_folder, f'{self.active_fn}.json'), 'w') as out_file:
            json.dump(self.file_dict, out_file, indent=4)
    def dump(self):
        # Dump collected binary data to file
        print('dumping file...')
        with open(self.active_fn, 'bw') as o_bin_file:
            for data_hex in self.file_dict['data'].values():
                o_bin_file.write(bytes.fromhex(data_hex))
        print('done!')
    def check_received(self):
        if self.active_fn != '':
            self.store_in_tmp_file()
            # Check if all parts received by offset
            prev_offset = 0
            received_offsets = list(self.file_dict['data'].keys())
            is_all_blocks_received = True
            bs = 187
            if int(received_offsets[0]) != 0:
                print("Part with 0 offset not received")
                prev_offset = int(received_offsets[0])
                is_all_blocks_received = False
            for cur_offset in received_offsets[1:]:
                int_cur_offset = int(cur_offset)
                if prev_offset + bs != int_cur_offset:
                    print(f"{int((int_cur_offset - prev_offset) / bs)} blocks from offset {prev_offset} is not received")
                    is_all_blocks_received = False
                prev_offset = int_cur_offset
            # Check if all file received by size.
            if is_all_blocks_received:
                if 'size' in self.file_dict['meta']: 
                    last_offset = list(self.file_dict['data'].keys())[-1]
                    hex_str=self.file_dict['data'][last_offset]
                    number_of_elements_in_last_block = int(len(hex_str)/2)
                    if self.file_dict['meta']['size'][0] == (int(last_offset) + int(number_of_elements_in_last_block)):
                        is_all_blocks_received = True
                    else:
                        print('File received incomplete')
                        is_all_blocks_received = False
                else:
                    print('No information about file size, probably need another receive session, or try to --force_dump')
            return is_all_blocks_received

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract files from Telemetry Viewer log file")
    parser.add_argument("--force-dump", help="Force dump to even if all data pieces are not collected",
                       action='store_true')
    parser.add_argument("filename", help="Absolute path to log for process")
    args = parser.parse_args()
    filename = args.filename

    fc = File_Collector()
    with open(filename) as f:
        csv_reader = csv.DictReader(f, delimiter=';')
        for row in csv_reader:
            fc.parse_line(row)
    if fc.check_received() or args.force_dump:
        fc.dump()
