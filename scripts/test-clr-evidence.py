#!/usr/bin/env python3
"""Corroborate REA metadata against source bytes; never load package assemblies.
Row locations are supplied by REA, not independently derived table offsets.
Format reference: ECMA-335 sixth edition, II.22/II.24/II.25.
"""
import hashlib
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/baseline/b01/clr'


def headers(data):
    def u(fmt, off):
        return struct.unpack_from('<' + fmt, data, off)
    pe, = u('I', 60)
    assert data[:2] == b'MZ' and data[pe:pe+4] == b'PE\0\0'
    machine, sections = u('HH', pe+4)
    optional_size, = u('H', pe+20)
    optional = pe+24
    magic, = u('H', optional)
    directory = optional + {0x10b: 96, 0x20b: 112}[magic]
    cli_rva, cli_size = u('II', directory+14*8)
    section_records = []
    for i in range(sections):
        at = optional+optional_size+i*40
        virtual_size, va, size, offset = u('IIII', at+8)
        section_records.append((va, size, offset))
    def mapped(rva, size):
        matches = [off+rva-va for va, rawsize, off in section_records
                   if va <= rva and rva+size <= va+rawsize]
        assert len(matches) == 1, 'RVA not uniquely file backed'
        offset = matches[0]
        assert offset+size <= len(data), 'truncated file'
        return offset
    cli = mapped(cli_rva, cli_size)
    cb, major, minor, mrva, msize, flags = u('IHHIII', cli)
    assert cb >= 72 and cli_size >= 72
    md = mapped(mrva, msize)
    assert data[md:md+4] == b'BSJB'
    vlen, = u('I', md+12)
    assert md+16+vlen <= md+msize
    version = data[md+16:md+16+vlen].rstrip(b'\0').decode('ascii')
    cursor = md+16+((vlen+3)//4)*4
    _, count = u('HH', cursor)
    cursor += 4
    streams = {}
    for _ in range(count):
        off, size = u('II', cursor)
        name_start = cursor+8
        end = data.index(0, name_start, min(name_start+32, md+msize))
        name = data[name_start:end].decode('ascii')
        assert name not in streams and off+size <= msize
        streams[name] = (md+off, size)
        cursor = (end+4)//4*4
    tables, table_size = streams.get('#~', streams.get('#-', (None, None)))
    assert tables is not None and table_size >= 24
    heap_sizes = data[tables+6]
    return {'machine': machine, 'cli': cli, 'runtime': f'{major}.{minor}',
            'flags': flags, 'metadata': md, 'metadata_size': msize,
            'version': version, 'streams': streams, 'heap_sizes': heap_sizes}


class EvidenceTests(unittest.TestCase):
    def test_all_sources_headers_and_declared_rows(self):
        inventory = json.loads((OUT/'inventory.json').read_text())
        dependency = json.loads((OUT.parent/'dependencies/inventory.json').read_text())
        expected = {r['source'] for r in dependency['pe'] if r['clr_directory'][0]}
        self.assertEqual(expected, {r['source'] for r in inventory['records']})
        self.assertEqual(len(expected), 13)
        audit = []
        for row in inventory['records']:
            data = (ROOT/row['source']).read_bytes()
            raw = json.loads((ROOT/row['raw']).read_text())
            result = raw['normalized_result']
            self.assertEqual(hashlib.sha256(data).hexdigest(), row['sha256'])
            self.assertEqual(raw['subject']['digest']['sha256'], row['sha256'])
            h = headers(data)
            self.assertEqual(result['pe']['machine'], h['machine'])
            for key, value in [('header_offset', h['cli']), ('runtime_version', h['runtime']),
                               ('flags', h['flags']), ('metadata_size', h['metadata_size'])]:
                self.assertEqual(result['pe']['cli'][key], value)
            self.assertEqual(result['metadata']['version'], h['version'])
            self.assertEqual(set(result['metadata']['stream_names']), set(h['streams']))
            sw = 4 if h['heap_sizes'] & 1 else 2
            bw = 4 if h['heap_sizes'] & 4 else 2
            def index(at, width):
                return int.from_bytes(data[at:at+width], 'little')
            def string(i):
                start, size = h['streams']['#Strings']
                self.assertLess(i, size)
                end = data.index(0, start+i, start+size)
                return data[start+i:end].decode('utf-8')
            for ref in [result['assembly'], *result['references']]:
                at = ref['row_offset']
                table, size = h['streams'].get('#~', h['streams'].get('#-'))
                self.assertTrue(table <= at < table+size)
                is_assembly = ref is result['assembly']
                version_at = at+4 if is_assembly else at
                self.assertEqual('.'.join(map(str, struct.unpack_from('<HHHH', data, version_at))), ref['version'])
                flags_at = version_at+8
                self.assertEqual(struct.unpack_from('<I', data, flags_at)[0], ref['flags'])
                self.assertEqual(string(index(flags_at+4+bw, sw)), ref['name'])
                self.assertEqual(string(index(flags_at+4+bw+sw, sw)), ref['culture'] or '')
            self.assertEqual(len(result['references']), result['metadata']['table_row_counts']['AssemblyRef'])
            self.assertEqual(result['coverage'], row['coverage'])
            for key in ('assembly', 'metadata', 'classification', 'target_frameworks', 'references'):
                self.assertEqual(result[key], row[key])
            audit.append({'source': row['source'], **h})
        (OUT/'header-audit.json').write_text(json.dumps(audit, indent=2)+'\n')

    def test_truncated_source_rejected(self):
        row = json.loads((OUT/'inventory.json').read_text())['records'][0]
        data = (ROOT/row['source']).read_bytes()
        for length in (0, 64, 512, 1024):
            with self.subTest(length=length):
                with self.assertRaises((AssertionError, ValueError, struct.error, IndexError)):
                    headers(data[:length])


if __name__ == '__main__':
    unittest.main()
