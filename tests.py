# coding=utf-8

from unittest import TestCase
from scraper import audiojelly, beatport


class BeatportTest(TestCase):
    maxDiff = None

    def test_simple_album(self):
        expected = {'title': u'Love Love Love Yeah', 'label': [u'Playhouse'], 'released': u'2007-01-22',
                    'catalog': [u'PLAY131'], 'discs': {
                1: [('1', [], u'Love Love Love Yeah', u'07:55'), ('2', [], u'Bus Driver', u'03:07'),
                    ('3', [], u'Christiane', u'00:24'), ('4', [], u'So Cold', u'03:32')]},
                    'link': 'http://www.beatport.com/release/love-love-love-yeah/43577',
                    'artists': [{'type': 'Main', 'name': u'Rework'}], 'genre': [u'Electro House', u'DJ Tools']}

        r = beatport.Release.release_from_url('http://www.beatport.com/release/love-love-love-yeah/43577')

        self.assertEqual(expected, r.data)

    def test_remix_track_artist(self):
        expected = {'title': u'Love Spy / Love Dies', 'label': [u'Karatemusik'], 'released': u'2006-04-19',
                    'catalog': [u'KM013'], 'discs': {1: [(
                '1', [{'type': 'Remixer', 'name': u'Error Error'}], u'Love Spy / Love Dies [Error Error Remix]',
                u'07:27'),
                ('2', [], u'Love Spy / Love Dies', u'07:07'), ('3', [], u'Reply 23', u'06:58')]},
                    'link': 'http://www.beatport.com/release/love-spy-love-dies/27944',
                    'artists': [{'type': 'Main', 'name': u'Polygamy Boys'}], 'genre': [u'Tech House', u'Electro House']}

        r = beatport.Release.release_from_url('http://www.beatport.com/release/love-spy-love-dies/27944')

        self.assertEqual(expected, r.data)

    def test_various_artists(self):
        expected = {'title': u'DJ Tunes Compilation', 'format': u'Album', 'label': [u'Carlo Cavalli Music Group'],
                    'released': u'2012-01-05', 'catalog': [u'CMG117'], 'discs': {
                1: [('1', [{'type': 'Main', 'name': u'Sam Be-Kay'}], u'Forever Loved', u'5:20'), (
                    '2', [{'type': 'Main', 'name': u'Eros Locatelli'}, {'type': 'Remixer', 'name': u'Alex Faraci'}],
                    u'Sweep [Alex Faraci Remix]', u'6:38'), ('3', [{'type': 'Main', 'name': u'Babette Duwez'},
                        {'type': 'Main', 'name': u'Joel Reichert'}, {'type': 'Remixer', 'name': u'David Ahumada'}],
                                                             u'Humo Y Neon [David Ahumada Remix]', u'4:58'), (
                    '4', [{'type': 'Main', 'name': u'Alex Faraci'}, {'type': 'Remixer', 'name': u'Massimo Russo'}],
                    u'Night Melody [Massimo Russo La Guitarra Remix]', u'6:17'),
                    ('5', [{'type': 'Main', 'name': u'Fingers Clear'}], u'30 m [Original mix]', u'6:33'),
                    ('6', [{'type': 'Main', 'name': u'Erion Gjuzi'}], u'Just Begin', u'7:09'),
                    ('7', [{'type': 'Main', 'name': u'Dany Cohiba'}], u'Achakkar [Original mix]', u'6:28'), (
                        '8',
                        [{'type': 'Main', 'name': u'Massimo Russo'}, {'type': 'Remixer', 'name': u'Italianbeat Guys'}],
                        u'Raveline [Italianbeat Guys Remix]', u'6:46'), (
                        '9', [{'type': 'Main', 'name': u'Jurgen Cecconi'}, {'type': 'Main', 'name': u'Beethoven Tbs'}],
                        u'Grey 2 Fade feat. Babette Duwez [Jurgen Cecconi Mix]', u'10:53'),
                    ('10', [{'type': 'Main', 'name': u'Carlo Cavalli'}], u'Tanzmania', u'7:00')]},
                    'link': 'http://www.beatport.com/release/dj-tunes-compilation/851318',
                    'artists': [{'type': 'Main', 'name': 'Various'}],
                    'genre': [u'Progressive House', u'House', u'Deep House', u'Minimal', u'Tech House']}

        r = beatport.Release.release_from_url('http://www.beatport.com/release/dj-tunes-compilation/851318')

        self.assertEqual(expected, r.data)

    def test_404(self):
        r = beatport.Release.release_from_url('http://www.beatport.com/release/blubb/123')
        try:
            r.data
            self.assertFalse(True)
        except beatport.BeatportAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e


class AudiojellyTest(TestCase):
    maxDiff = None

    def test_simple_album(self):
        expected = {'title': u'Love \u221a Infinity (Love to the Square Root of Infinity)',
                    'label': ['defamation records'], 'released': '2011-10-27', 'catalog': ['5055506333041'], 'discs': {
                1: [('1', [], u'Love \u221a Infinity (Radio Edit)', '02:49'),
                    ('2', [], u'Love \u221a Infinity (Vocal Club Mix)', '06:46'),
                    ('3', [], u'Love \u221a Infinity (Instrumental Club Mix)', '06:46')]},
                    'link': 'http://www.audiojelly.com/releases/love-infinity-love-to-the-square-root-of-infinity/211079'
            , 'artists': [{'type': 'Main', 'name': 'AudioFreQ'}], 'genre': ['Electro House']}

        r = audiojelly.Release.release_from_url(
            'http://www.audiojelly.com/releases/love-infinity-love-to-the-square-root-of-infinity/211079')

        self.assertEqual(expected, r.data)

    def test_featuring_main_artist(self):
        expected = {'title': 'Where Is Love (Love Is Hard To Find)', 'label': ['Ultra Records'],
                    'released': '2011-10-24', 'catalog': ['UL 2903'], 'discs': {
                1: [('1', [], 'Where Is Love (Love Is Hard To Find) (Lucky Date Remix)', '06:15'),
                    ('2', [], 'Where Is Love (Love Is Hard To Find) (Electrixx Radio Edit)', '03:54'),
                    ('3', [], 'Where Is Love (Love Is Hard To Find) (Electrixx Remix)', '06:07'),
                    ('4', [], 'Where Is Love (Love Is Hard To Find) (Matthew Sterling Remix)', '05:32'),
                    ('5', [], 'Where Is Love (Love Is Hard To Find) (Disco Fries Remix)', '05:51'),
                    ('6', [], 'Where Is Love (Love Is Hard To Find) (Mysto & Pizzi Remix)', '05:28'),
                    ('7', [], 'Where Is Love (Love Is Hard To Find) (Ido Shoam Remix)', '05:01'),
                    ('8', [], 'Where Is Love (Love Is Hard To Find) (SpacePlant Remix)', '06:11')]},
                    'link': 'http://www.audiojelly.com/releases/where-is-love-love-is-hard-to-find/210428',
                    'artists': [{'type': 'Main', 'name': 'Mysto'}, {'type': 'Main', 'name': 'Pizzi'},
                            {'type': 'Feature', 'name': 'Johnny Rose'}], 'genre': ['Electronica']}

        r = audiojelly.Release.release_from_url(
            'http://www.audiojelly.com/releases/where-is-love-love-is-hard-to-find/210428')

        self.assertEqual(expected, r.data)

    def test_various_artists(self):
        expected = {'title': 'Plus Various I', 'label': ['Sound Academy Plus'], 'released': '2012-04-01',
                    'catalog': ['SAP042'], 'discs': {
                1: [('1', [{'type': 'Main', 'name': 'Can Yuksel'}], 'With You Forever (Original Mix)', '07:08'), (
                    '2', [{'type': 'Main', 'name': 'Ismael Casimiro'}, {'type': 'Main', 'name': 'Borja Maneje'}],
                    'Electro Deep (Gokhan Guneyli Remix)', '08:48'),
                    ('3', [{'type': 'Main', 'name': 'Roby B.'}], 'Deal (Original Mix)', '06:45'),
                    ('4', [{'type': 'Main', 'name': 'Serdar Ors'}], 'Musica (Can Yuksel Remix)', '06:11')]},
                    'link': 'http://www.audiojelly.com/releases/plus-various-i/230282',
                    'artists': [{'type': 'Main', 'name': 'Various'}], 'genre': ['Tech House']}

        r = audiojelly.Release.release_from_url('http://www.audiojelly.com/releases/plus-various-i/230282')

        self.assertEqual(expected, r.data)

    def test_404(self):
        r = audiojelly.Release.release_from_url('http://www.audiojelly.com/releases/plus-various-i/999999')
        try:
            r.data
            self.assertFalse(True)
        except audiojelly.AudiojellyAPIError as e:
            if not unicode(e).startswith('404 '):
                raise e