# coding=utf-8
import lxml.html, re
from base import BaseRelease, BaseSearch, BaseAPIError


READABLE_NAME = 'Audiojelly'
SCRAPER_URL = 'http://www.audiojelly.com/'


class AudiojellyAPIError(BaseAPIError):
    pass


class Release(BaseRelease):

    _base_url = 'http://www.audiojelly.com/'
    url_regex = '^http://(?:www\.)?audiojelly\.com/releases/(.*?)/(\d+)$'
    exception = AudiojellyAPIError

    _various_artists_aliases = ['Various', 'Various Artists']

    def __init__(self, id, release_name):
        self.id = id

        self._release_name = release_name

    def __unicode__(self):
        return u'<AudiojellyRelease: id=%d, name="%s">' % (self.id, self._release_name)

    @staticmethod
    def _get_args_from_match(match):
        return (int(match.group(2)), match.group(1))

    def get_url(self):
        return self._base_url + 'releases/%s/%d' % (self._release_name,self.id)

    def get_release_url(self):
        return self.get_url()

    def _separate_multiple_artists(self, artist_string):
        artists = re.split('\\s*?(?:,|&|with)\\s*?', artist_string)
        artists = map(self.remove_whitespace, artists)
        return artists

    def _split_artists(self, artist_string):
        formatted_artists = []
        artists = re.split('\\s*?(?:ft\\.?|feat\\.?|featuring)\\s*?', artist_string)
        main_artists = self._separate_multiple_artists(artists[0])
        for main_artist in main_artists:
            formatted_artists.append(self.format_artist(main_artist, self.ARTIST_TYPE_MAIN))
        if len(artists) > 1:
            featuring_artists = artists[1:]
            for featuring_artist_string in featuring_artists:
                featuring_artists = self._separate_multiple_artists(featuring_artist_string)
                for featuring_artist in featuring_artists:
                    formatted_artists.append(self.format_artist(featuring_artist, self.ARTIST_TYPE_FEATURE))
        return formatted_artists

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

        self._label_dict = dict(map(lambda x: (x.getprevious().text_content().lower(), x),filter(lambda x: x.getprevious() is not None,self.parsed_response.cssselect('label + span.spec'))))
        self._track_artists_equal_release_artist = True

        # check if the artists of each track equal the release artists
        if self._label_dict.has_key('artist'):
            release_artists = self._label_dict['artist'].text_content()
            release_artists = self.remove_whitespace(release_artists)

            track_artists = self.parsed_response.cssselect('span.artistName')
            for track_artist_span in track_artists:
                track_artist = track_artist_span.text_content()
                track_artist = self.remove_whitespace(track_artist)
                self._track_artists_equal_release_artist = track_artist == release_artists
                if not self._track_artists_equal_release_artist:
                    break

    def get_release_date(self):
        if self._label_dict.has_key('release date'):
            release_date = self._label_dict['release date'].text_content()
            release_date = self.remove_whitespace(release_date)
            if release_date:
                return release_date
        return None

    def get_labels(self):
        if self._label_dict.has_key('label'):
            label_anchors = self._label_dict['label'].cssselect('a')
            labels = []
            for anchor in label_anchors:
                link_text = anchor.text_content()
                link_text = self.remove_whitespace(link_text)
                if link_text:
                    labels.append(link_text)
            return labels
        return []

    def get_catalog_numbers(self):
        if self._label_dict.has_key('cat number'):
            cat_number = self._label_dict['cat number'].text_content()
            cat_number = self.remove_whitespace(cat_number)
            if cat_number:
                return [cat_number,]
        return []

    def get_release_title(self):
        title_h1 = self.parsed_response.cssselect('div.pageHeader h1')
        if len(title_h1) == 1:
            title_h1 = title_h1[0]
            title = title_h1.text_content()
            title = self.remove_whitespace(title)
            if title:
                return title
        else:
            self.raise_exception(u'could not determine title h1')

    def get_release_artists(self):
        if self._label_dict.has_key('artist'):
            artist_anchors = self._label_dict['artist'].cssselect('a')
            artists = []
            for anchor in artist_anchors:
                artist = anchor.text_content()
                artist = self.remove_whitespace(artist)
                if artist:
                    if artist in self._various_artists_aliases:
                        artists.append(self.format_artist(self.ARTIST_NAME_VARIOUS, self.ARTIST_TYPE_MAIN))
                    else:
                        artists.extend(self._split_artists(artist))
            return artists
        else:
            self.raise_exception(u'could not find artist span')

    def get_genres(self):
        if self._label_dict.has_key('genre'):
            genre_anchors = self._label_dict['genre'].cssselect('a')
            genres = []
            for anchor in genre_anchors:
                genre = anchor.text_content()
                genre = self.remove_whitespace(genre)
                if genre:
                    genre = re.split('\\s*?(?:/|,)\\s*?', genre)
                    genres.extend(filter(lambda x: x,genre))
            return genres
        return []

    def get_disc_containers(self):
        release_tracklist = self.parsed_response.cssselect('div.trackList.release')
        if len(release_tracklist) != 1:
            self.raise_exception(u'could not get track list div')
        return {1 : release_tracklist[0]}

    def get_track_containers(self, discContainer):
        return discContainer.cssselect('div.trackListRow')

    def get_track_number(self, trackContainer):
        track_number = trackContainer.cssselect('p.trackNum')
        if len(track_number) == 1:
            track_number = track_number[0].text_content()
            track_number = self.remove_whitespace(track_number)
            if track_number:
                track_number = track_number.lstrip('0')
                if not track_number:
                    track_number = '0'
                return track_number
        self.raise_exception(u'could not get track number')

    def get_track_artists(self, trackContainer):
        if not self._track_artists_equal_release_artist:
            artist_span = trackContainer.cssselect('span.artistName')
            if len(artist_span) == 1:
                artists = []
                artist_anchors = artist_span[0].cssselect('a')
                for anchor in artist_anchors:
                    artist = anchor.text_content()
                    artist = self.remove_whitespace(artist)
                    if artist and not artist in self._various_artists_aliases:
                        artists.extend(self._split_artists(artist))
                return artists
        return []

    def get_track_title(self, trackContainer):
        title_span = trackContainer.cssselect('span.trackName')
        if len(title_span) == 1:
            title = title_span[0].text_content()
            title = self.remove_whitespace(title)
            if title:
                return title
        self.raise_exception(u'could not get track title')

    def get_track_length(self, trackContainer):
        length_span = trackContainer.cssselect('span.trackTime')
        if len(length_span) == 1:
            length = length_span[0].text_content()
            length = self.remove_whitespace(length)
            if length:
                return length
        return None


class Search(BaseSearch):

    _base_url = 'http://www.audiojelly.com'
    url = _base_url + '/search/all/'
    exception = AudiojellyAPIError

    _not_found = False

    def __unicode__(self):
        return u'<AudiojellySearch: term="' + self.search_term + u'">'

    def get_params(self):
        return {'view':'releases', 'q':self.search_term}

    # Warning: The following is ugly hack territory. The stupid site apparently returns a 500 status code if it cannot
    # find at least one release with the given search term.
    # So instead of raising an exception with a 500 status code, we remember that there was nothing found
    def raise_exception(self, message):
        if message.startswith('500'):
            self._not_found = True
        else:
            super(Search, self).raise_exception(message)

    def prepare_response_content(self, content):
        if not self._not_found:
            #get the raw response content and parse it
            self.parsed_response = lxml.html.document_fromstring(content)

    def get_release_containers(self):
        if self._not_found:
            return []
        return self.parsed_response.cssselect('div.relInfo')[:25]

    def get_release_name(self,releaseContainer):
        release_artist_anchor = releaseContainer.cssselect('div.relArtistName a')
        if len(release_artist_anchor) == 0:
            self.raise_exception(u'could not extract release artist')
        artists = []
        for artist_anchor in release_artist_anchor:
            artist = artist_anchor.text_content()
            artist = self.remove_whitespace(artist)
            if artist:
                artists.append(artist)
        release_title_anchor = releaseContainer.cssselect('div.relReleaseName a')
        if len(release_title_anchor) != 1:
            self.raise_exception(u'could not get release name anchor')
        release_title = release_title_anchor[0].text_content()
        release_title = self.remove_whitespace(release_title)
        return u', '.join(artists) + u' \u2013 ' + release_title

    def get_release_info(self,releaseContainer):
        components = []
        label_div = releaseContainer.cssselect('div.relLabel')
        if len(label_div) == 1:
            label = label_div[0].text_content()
            label = self.remove_whitespace(label)
            if label:
                components.append(label)
        genre_div = releaseContainer.cssselect('div.relGenre')
        if len(genre_div) == 1:
            genre = genre_div[0].text_content()
            genre = self.remove_whitespace(genre)
            if genre:
                components.append(genre)
        if components:
            return u' | '.join(components)
        return None

    def get_release_instance(self,releaseContainer):
        release_title_anchor = releaseContainer.cssselect('div.relReleaseName a')
        if len(release_title_anchor) != 1:
            self.raise_exception(u'could not get release name anchor')
        release_url = self._base_url + release_title_anchor[0].attrib['href']
        return Release.release_from_url(release_url)