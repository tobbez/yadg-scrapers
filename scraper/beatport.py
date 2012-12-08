# coding=utf-8
import json
from base import BaseRelease, BaseSearch, BaseAPIError


READABLE_NAME = 'Beatport'
SCRAPER_URL = 'http://www.beatport.com/'


class BeatportAPIError(BaseAPIError):
    pass


class Release(BaseRelease):

    url = 'http://api.beatport.com/catalog/releases/detail'
    url_regex = '^http://(?:www\.)?beatport\.com/release/(.*?)/(\d+)$'
    exception = BeatportAPIError

    def __init__(self, id, release_name=''):
        self.id = id

        self._release_name = release_name

    def __unicode__(self):
        return u'<BeatportRelease: id=%d>' % self.id

    @staticmethod
    def _get_args_from_match(match):
        if not match.group(1):
            return (int(match.group(2)), )
        return (int(match.group(2)), match.group(1))

    def get_params(self):
        return {'format':'json','v':'1.0','id':self.id}

    def get_release_url(self):
        return 'http://www.beatport.com/release/%s/%d' % (self._release_name, self.id)

    def prepare_response_content(self, content):
        try:
            response = json.loads(content)
        except:
            self.raise_exception(u'invalid server response')

        if response['metadata']['count'] != 1:
            self.raise_exception(u'got more than one release for given id')

        self.parsed_response = response['results']

    def get_release_date(self):
        if self.parsed_response.has_key('releaseDate'):
            return self.parsed_response['releaseDate']
        return None

    def get_release_format(self):
        if self.parsed_response.has_key('category') and not self.parsed_response['category'] in ('Release','Uncategorized'):
            return self.parsed_response['category']
        return None

    def get_labels(self):
        if self.parsed_response.has_key('label'):
            return [self.parsed_response['label']['name'],]
        return []

    def get_catalog_numbers(self):
        if self.parsed_response.has_key('catalogNumber'):
            return [self.parsed_response['catalogNumber'],]
        return []

    def get_release_title(self):
        if self.parsed_response.has_key('name'):
            return self.parsed_response['name']
        return None

    def get_release_artists(self):
        if self.parsed_response.has_key('artists'):
            #get all real 'Artists' (not 'Remixers', etc.)
            real_artists = []
            for artist in self.parsed_response['artists']:
                if artist['type'].lower() == 'artist' and artist['name']:
                    real_artists.append(self.format_artist(artist['name'], self.ARTIST_TYPE_MAIN))
            #we assume that it is a Various Artists release if the release type is 'Album'
            #and the number of 'Artists' (not 'Remixers') is greater 1
            if self.parsed_response.has_key('category') and self.parsed_response['category'] == 'Album' and len(real_artists) > 1:
                artists = [self.format_artist(self.ARTIST_NAME_VARIOUS, self.ARTIST_TYPE_MAIN),]
            else:
                artists = real_artists
            self.artists = artists
            return artists
        return []

    def get_genres(self):
        if self.parsed_response.has_key('genres'):
            return map(lambda x: x['name'], self.parsed_response['genres'])
        return []

    def get_disc_containers(self):
        return {1:{}}

    def get_track_containers(self, discContainer):
        if self.parsed_response.has_key('tracks'):
            i = 0
            containers = []
            for track in self.parsed_response['tracks']:
                i += 1
                containers.append({'track_no':i, 'track':track})
            return containers
        return []

    def get_track_number(self, trackContainer):
        return str(trackContainer['track_no'])

    def get_track_artists(self, trackContainer):
        track = trackContainer['track']
        if track.has_key('artists'):
            track_main_artists = []
            track_additional_artists = []
            for track_artist_candidate in track['artists']:
                if track_artist_candidate['name']:
                    track_artist_type = track_artist_candidate['type'].lower()
                    if track_artist_type == 'artist':
                        track_main_artists.append(self.format_artist(track_artist_candidate['name'], self.ARTIST_TYPE_MAIN))
                    elif track_artist_type == 'remixer':
                        track_additional_artists.append(self.format_artist(track_artist_candidate['name'], self.ARTIST_TYPE_REMIXER))
            if track_main_artists == self.artists:
                track_artists = track_additional_artists
            else:
                track_artists = track_main_artists + track_additional_artists
            return track_artists
        return []

    def get_track_title(self, trackContainer):
        track = trackContainer['track']
        if track.has_key('name'):
            track_title = track['name']
            if track.has_key('mixName') and track['mixName'] != 'Original Mix':
                track_title += u' [' + self.remove_whitespace(track['mixName']) + u']'
            return track_title
        return None

    def get_track_length(self, trackContainer):
        track = trackContainer['track']
        if track.has_key('length'):
            return track['length']
        return None


class Search(BaseSearch):

    url = 'http://api.beatport.com/catalog/search'
    exception = BeatportAPIError

    def get_params(self):
        return {'v':'2.0','format':'json','perPage':'25','page':'1','facets':['fieldType:release',], 'highlight':'false', 'query':self.search_term}

    def prepare_response_content(self, content):
        try:
            self.parsed_response = json.loads(content)
        except:
            self.raise_exception(u'invalid server response')

    def get_release_containers(self):
        if self.parsed_response.has_key('results'):
            return filter(lambda x: x.has_key('id'),self.parsed_response['results'])
        return []

    def get_release_name(self, releaseContainer):
        name_components = []
        if releaseContainer.has_key('artists'):
            #get all real 'Artists' (not 'Remixers', etc.)
            real_artists = []
            for artist in releaseContainer['artists']:
                if artist['type'].lower() == 'artist' and artist['name']:
                    real_artists.append(artist['name'])
                #we assume that it is a Various Artists release if the release type is 'Album'
            #and the number of 'Artists' (not 'Remixers') is greater 1
            if releaseContainer.has_key('category') and releaseContainer['category'] == 'Album' and len(real_artists) > 1:
                artists = ['Various',]
            else:
                artists = real_artists
            if artists:
                name_components.append(u', '.join(artists))
        if releaseContainer.has_key('name'):
            name_components.append(releaseContainer['name'])
        name = u' \u2013 '.join(name_components)
        return name

    def get_release_info(self, releaseContainer):
        add_info = []
        if releaseContainer.has_key('releaseDate'):
            add_info.append(releaseContainer['releaseDate'])
        if releaseContainer.has_key('label'):
            add_info.append(releaseContainer['label']['name'])
        if releaseContainer.has_key('catalogNumber'):
            add_info.append(releaseContainer['catalogNumber'])
        info = u' | '.join(add_info)
        return info

    def get_release_instance(self, releaseContainer):
        id = releaseContainer['id']
        if releaseContainer.has_key('slug'):
            slug = releaseContainer['slug']
        else:
            slug = ''
        return Release(id, slug)

    def __unicode__(self):
        return u'<BeatportSearch: term="' + self.search_term + u'">'