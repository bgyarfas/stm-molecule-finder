from collections import OrderedDict, namedtuple
from struct import Struct

class CStruct(OrderedDict):
    @property
    def struct_str(self):
        return ''.join(self.values())

board_info_def_v2 = CStruct({
    'assembly':                  'i',
    'firmware_rev':              'i',
    'board_rev':                 'i',
    'board_serial':              'i',
    'digital_serial':            'i',
    'analog_serial':             'i',
    'adc_offset_pa':             'q',
    'adc_offset_m_meas':         'd',
    'adc_offset_b_meas':         'd',
    'adc_offset_m_cond':         'd',
    'adc_offset_b_cond':         'd',
    'dac_offset_uv':             'q',
    'dac_offset_m_cis_meas':     'd',
    'dac_offset_b_cis_meas':     'd',
    'dac_offset_m_trans_meas':   'd',
    'dac_offset_b_trans_meas':   'd',
    'dac_offset_m_cis_cond':     'd',
    'dac_offset_b_cis_cond':     'd',
    'dac_offset_m_trans_cond':   'd',
    'dac_offset_b_trans_cond':   'd',
    'dac_stepup_meas':           'd',
    'dac_stepup_cond':           'd',
    'conversion_value':          'Q',
    'conversion_accuracy':       'Q',
    'transcap_nf':               'Q',
    'bessel_cutoff_freq_khz':    'Q',
    'rc_time_ns':                'q',
    'cap_parasitic_ff':          'q',
    'voltage_stepdown':          'd',
    'reference_voltage':         'q',
    'sense_resistor':            'q',
    'cond_resistor':             'q',
    'default_cis_positive':      'q',
    'default_cis_negative':      'q',
    'default_cond_positive':     'q',
    'default_cond_negative':     'q',
    'dac_resolution_meas':       'q',
    'dac_resolution_cond':       'q',
    'common_cis':                'B',
    'inversed_voltage':          'B',
    'cis_channel':               'q',
    'emf_offset':                'q',
})

board_info_def_v1 = board_info_def_v2.copy()
board_info_def_v1.pop('cap_parasitic_ff')

board_info_nt_v1 = namedtuple('BoardInfo', board_info_def_v1.keys())
board_info_nt_v2 = namedtuple('BoardInfo', board_info_def_v2.keys())

data_file_header_def = CStruct({
    'version':         'L',
    'data_size_bytes': 'L',
    'assembly':        '64s',
    'firmware_rev':    '64s',
    'board_rev':       '64s',
    'board_serial':    '256s',
    'digital_serial':  '64s',
    'analog_serial':   '64s',
    'repo_manifest':   '4096s',
    'board_info':      '',
})

data_file_header_nt = namedtuple('DataFileHeader', data_file_header_def.keys())

data_block_header_def = CStruct({
    'timestamp':       'd',
    'sampling_rate':   'q',
    'seqno':           'Q',
    'overrun':         'Q',
    'cis':             'q',
    'trans':           'q',
    'pore':            'q',
    'conditioning':    'B',
    'samples_size':    'I',
})

data_block_header_nt = namedtuple('DataBlockHeader', data_block_header_def.keys())

board_info_struct_v1 = Struct(board_info_def_v1.struct_str)
board_info_struct_v2 = Struct(board_info_def_v2.struct_str)
data_block_struct = Struct(data_block_header_def.struct_str)
data_file_struct = Struct(data_file_header_def.struct_str)