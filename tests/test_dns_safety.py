from pathlib import Path
import unittest

import yaml
from octodns.processor.filter import NameRejectlistFilter
from octodns.record import Record
from octodns.zone import Zone


class ApexSafetyTests(unittest.TestCase):
    def guard(self):
        config = yaml.safe_load((Path(__file__).resolve().parents[1] / 'octodns.yaml').read_text())
        name = 'preserve-manual-apex'
        self.assertIn(name, config['zones']['elsys.club.']['processors'])
        options = dict(config['processors'][name])
        self.assertEqual(options.pop('class'), 'octodns.processor.filter.NameRejectlistFilter')
        return NameRejectlistFilter(name, **options)

    def zone(self):
        zone = Zone('elsys.club.', [])
        for name in ['', 'ai', 'devops']:
            zone.add_record(Record.new(zone, name, {'type': 'A', 'ttl': 300, 'value': '192.0.2.1'}))
        zone.add_record(Record.new(zone, 'info', {'type': 'CNAME', 'ttl': 300,
                                              'value': 'tues-clubs-bridge.pages.dev.'}))
        return zone

    def test_existing_manual_apex_cannot_be_deleted_by_sync(self):
        zone = self.guard().process_target_zone(self.zone(), None)
        self.assertEqual({r.name for r in zone.records}, {'ai', 'devops', 'info'})

    def test_apex_management_stays_outside_desired_zone_until_explicit_handoff(self):
        zone = self.guard().process_source_zone(self.zone(), [])
        self.assertEqual({r.name for r in zone.records}, {'ai', 'devops', 'info'})


if __name__ == '__main__':
    unittest.main()
