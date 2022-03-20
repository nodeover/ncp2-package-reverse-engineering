import argparse
import binascii
import os.path


class NCP2Unpacker(object):
    data_header = {}
    file_list = []
    file_data = {}
    cmd_offsets = {}
    valid_data = {}
    valid_data['file_type'] = None
    valid_data['unknown_padding_1'] = None  # binascii.unhexlify(b'0100200403000300') or 0100200404000300 (ncp)
    valid_data['unknown_padding_2'] = binascii.unhexlify(b'0000000000000000')
    valid_data['unknown_string'] = b'ARESNPQ_Test'
    fp = None
    debug = True

    def print(self, message):
        '''
        print message
        :param message:message
        :return: None
        '''
        if self.debug:
            print(message)

    def load_cmd(self):
        '''
        load command block
        :param fp: file pointer
        :return: [cmd_name, offset, length]
        '''
        cmd_name = self.fp.read(4).decode('ascii')
        if cmd_name not in ['INFO', 'FTBL', 'DATA']:
            raise Exception("unexpected command loaded. [{} at {}]".format(cmd_name, self.fp.tell()))
        length = int.from_bytes(self.fp.read(4), byteorder='little')
        offset = self.fp.tell()
        self.fp.seek(offset + length)

        # command end check
        if self.fp.read(4) != binascii.unhexlify(b'00005045'):  # (null)(null)PE
            raise Exception("incorrect data length! ({})".format(cmd_name))

        return cmd_name, offset, length

    def load_meta(self):
        '''
        load metadata
        :return:
        '''
        self.print("reading header data...")
        # 1. file_type
        h_file_type = self.fp.read(4)
        if h_file_type == b'NPQF':
            pass
        elif h_file_type == b'RIFF':
            h_file_type_more = self.fp.read(4)
            if h_file_type_more == b'NPQF':
                h_file_type += h_file_type_more
            else:
                raise Exception("Cannot recognize file type. (2)")
        else:
            raise Exception("Cannot recognize file type.")

        self.insert_data('file_type', h_file_type.decode('ascii'))
        self.print('1. file_type: {}'.format(self.data_header['file_type']))

        # 2. unknown_padding_1
        self.insert_data('unknown_padding_1', self.fp.read(8))
        self.print(
            '2. unknown_padding_1: {}'.format(binascii.hexlify(self.data_header['unknown_padding_1']).decode('ascii')))

        # 3. unknown_string
        self.insert_data('unknown_string', self.fp.read(12))
        self.print('3. h_unknown_string: {}'.format(self.data_header['unknown_string']))

        # 4. unknown_padding_2
        self.insert_data('unknown_padding_2', self.fp.read(8))
        self.print(
            '3. unknown_padding_2: {}'.format(binascii.hexlify(self.data_header['unknown_padding_2']).decode('ascii')))

        # success loaded header
        self.print('header loaded successfully!')

        return True

    def read_file_list(self, offset, length):
        file_list = []
        file_data = {}
        self.fp.seek(offset)
        file_cnt = length / 64  # file block size is 64 bytes
        if file_cnt % 1 != 0:
            raise Exception('unexpected file block data')
        file_cnt = int(file_cnt)
        print('[FILE LIST]')
        for cnt in range(1, file_cnt + 1):
            try:
                filename_binary = self.fp.read(44).replace(b'\x00', b'')
                file_name = filename_binary.decode('ascii')
            except Exception as e:
                pass
            file_offset = int.from_bytes(self.fp.read(4), byteorder='little') + self.cmd_offsets['DATA'][0]
            self.fp.read(4)
            file_length = int.from_bytes(self.fp.read(4), byteorder='little')
            if file_length != int.from_bytes(self.fp.read(4), byteorder='little'):
                raise Exception('unexpected file offset data')
            self.fp.read(4)
            print(f'{cnt}\t{file_name}')
            file_list.append(file_name)
            file_data[file_name] = {
                'offset': file_offset,
                'length': file_length
            }
        return file_list, file_data

    def save_data_to_file(self, filename, save_path):
        '''
        save data to file
        :param filename: file name.
        :param save_path: output save path.
        :return:
        '''
        at_file_data = self.file_data[filename]
        self.fp.seek(at_file_data['offset'])
        file_binary = self.fp.read(at_file_data['length'])

        with open(save_path, 'wb') as file:
            file.write(file_binary)

    def insert_data(self, key, data):
        '''
        insert data
        :param key: data key
        :param data: data
        :return:
        '''
        # validate data
        if self.valid_data[key] and self.valid_data[key] != data:
            raise Exception(f'unexpected {key} value!')
        self.data_header[key] = data
        return True

    def __init__(self, input_file, save_path):
        self.fp = open(input_file, 'rb')

        # load metadata
        self.load_meta()

        # read commands stream
        self.print('read commands stream...')
        while True:
            cmd_prefix = self.fp.read(8)
            if cmd_prefix != binascii.unhexlify(b'5053611064000000'):  # PSa(0x01)D
                if len(cmd_prefix) == 0:
                    self.print("data loaded successfully!")
                else:
                    raise Exception('unexpected command prefix loaded.')
                break
            cmd_name, cmd_offset, cmd_length = self.load_cmd()
            self.cmd_offsets[cmd_name] = [cmd_offset, cmd_length]

        self.file_list, self.file_data = self.read_file_list(self.cmd_offsets['FTBL'][0], self.cmd_offsets['FTBL'][1])
        print('file loaded!')

        for at_filename in self.file_list:
            save_path_with_filename = os.path.join(
                save_path,
                at_filename
            )
            self.save_data_to_file(at_filename, save_path_with_filename)


def main():
    input_file = '~/Downloads/music_test.ncp'
    save_path = '~/Desktop/output'
    nu = NCP2Unpacker(input_file, save_path)


if __name__ == '__main__':
    main()
