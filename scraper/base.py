import requests, re, logging


class BaseAPIError(Exception):
    pass


class ExceptionMixin(object):
    exception = BaseAPIError

    def get_exception(self):
        return self.exception

    def raise_exception(self, message):
        raise self.get_exception(), u'%s [%s]' % (message, unicode(self))


class StatusCodeError(requests.RequestException):
    """The request returned a status code that was not 200"""
    pass


class RequestMixin(object):
    REQUEST_METHOD_POST = 'post'
    REQUEST_METHOD_GET = 'get'

    url = None
    params = None
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0.2) Gecko/20100101 Firefox/6.0.2'}
    request_method = REQUEST_METHOD_GET
    post_data = None
    request_kwargs = {}
    forced_response_encoding = None

    _cached_response = None

    def _make_request(self, method, url, params, headers, post_data, kwargs):
        """
        The internal method that makes the actual request and returns a response object. This should normally not be used
        directly.
        """
        if method == self.REQUEST_METHOD_POST:
            r = requests.post(url=url, data=post_data, params=params, headers=headers, **kwargs)
        else:
            r = requests.get(url=url, params=params, headers=headers, **kwargs)
        return r

    def raise_request_exception(self, message):
        raise StatusCodeError(message)

    def get_url(self):
        return self.url

    def get_params(self):
        return self.params

    def get_headers(self):
        return self.headers

    def get_request_method(self):
        return self.request_method

    def get_post_data(self):
        return self.post_data

    def get_request_kwargs(self):
        return self.request_kwargs

    def get_forced_response_encoding(self):
        return self.forced_response_encoding

    def get_response_content(self, response):
        return response.text

    def get_response(self):
        if self._cached_response is None:
            self._cached_response = self._make_request(method=self.get_request_method(), url=self.get_url(), params=self.get_params(), headers=self.get_headers(), post_data=self.get_post_data(), kwargs=self.get_request_kwargs())
            if self._cached_response.status_code != 200:
                self.raise_request_exception('%d' % (self._cached_response.status_code if self._cached_response.status_code else 500)) #make sure we don't crash
            forced_encoding = self.get_forced_response_encoding()
            if forced_encoding:
                self._cached_response.encoding = forced_encoding
        return self._cached_response


class UtilityMixin(object):
    presuffixes = [
        (u'The ', u', The'),
        (u'A ', u', A'),
    ]

    def get_presuffixes(self):
        return self.presuffixes

    def swap_suffix(self, string):
        for (prefix, suffix) in self.get_presuffixes():
            if string.endswith(suffix):
                string = prefix + string[:-len(suffix)]
                #we assume there is only one suffix to swap
                break
        return string

    def remove_whitespace(self, string):
        return ' '.join(string.split())


class LoggerMixin(object):

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    _logger = None

    def get_logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(name=self.__module__ + '.' + self.__class__.__name__)
        return self._logger

    def get_extra_log_kwargs(self):
        return {'instance':unicode(self)}

    def log(self, level, msg):
        logger = self.get_logger()
        logger.log(level, msg, extra=self.get_extra_log_kwargs())


class BaseRelease(ExceptionMixin, RequestMixin, UtilityMixin, LoggerMixin):
    ARTIST_TYPE_MAIN = 'Main'
    ARTIST_TYPE_FEATURE = 'Feature'
    ARTIST_TYPE_REMIXER = 'Remixer'
    ARTIST_NAME_VARIOUS = 'Various'

    url_regex = ''

    _data = None
    _release_url = None

    priority = 10

    def raise_request_exception(self, message):
        """
        Make sure the RequestMixin uses ExceptionMixin
        """
        self.raise_exception(message)

    @property
    def data(self):
        if self._data is None:
            self._data = self._extract_infos()
        return self._data

    @property
    def release_url(self):
        if self._release_url is not None:
            return self._release_url
        return self.get_release_url()

    def get_release_url(self):
        """
        This method should return the URL of the release as a string or None.
        """
        return None

    def format_artist(self, artistName, artistType):
        """
        This method returns a formatted artist with it's type.
        """
        return {'name': artistName, 'type': artistType}

    def prepare_response_content(self, content):
        """
        This method is called before any other parsing method with the raw content of the response.
        """
        pass

    def get_release_date(self):
        """
        This method should return the release date as a string or None.
        """
        return None

    def get_release_format(self):
        """
        This method should return the format of the release as a string or None.
        """
        return None

    def get_labels(self):
        """
        This method should return a list of labels or an empty list.
        """
        return []

    def get_catalog_numbers(self):
        """
        This method should return a list of catalog numbers or an empty list.
        """
        return []

    def get_release_title(self):
        """
        This method should return the release title as a string or None.
        """
        return None

    def get_release_country(self):
        """
        This method should return the release country as a string or None
        """
        return None

    def get_release_artists(self):
        """
        This method should return a list of the main release artists or an empty list.
        """
        return []

    def get_genres(self):
        """
        This method should return a list of genres for the release or an emtpy list.
        """
        return []

    def get_styles(self):
        """
        This method should return a list of styles for the release or an empty list.
        """
        return []

    def get_disc_containers(self):
        """
        This method should return a dictionary where each entry's key is the disc number and the corresponding value is
        a kwarg dict that should be passed to get_track_containers
        """
        return {}

    def get_disc_title(self, discContainer):
        """
        This method should return the title of the given disc as a string or None.
        """
        return None

    def get_track_containers(self, discContainer):
        """
        This method should return a list where each entry is a kwarg dict that will be passed to the get_track_*
        methods.
        """
        return []

    def get_track_number(self, trackContainer):
        """
        This method should return the track number as a string or None.
        """
        return None

    def get_track_artists(self, trackContainer):
        """
        This method should return a list of track artists of an empty list.
        """
        return []

    def get_track_title(self, trackContainer):
        """
        This method should return the track title as a string or None.
        """
        return None

    def get_track_length(self, trackContainer):
        """
        This method should return the track length as a string or None.
        """
        return None

    def _extract_infos(self):
        data = {}

        response = self.get_response()

        self.prepare_response_content(self.get_response_content(response))

        releaseDate = self.get_release_date()
        if releaseDate:
            data['released'] = releaseDate

        releaseFormat = self.get_release_format()
        if releaseFormat:
            data['format'] = releaseFormat

        labels = self.get_labels()
        if labels:
            data['label'] = labels

        catalogNumbers = self.get_catalog_numbers()
        if catalogNumbers:
            data['catalog'] = catalogNumbers

        releaseTitle = self.get_release_title()
        if releaseTitle:
            data['title'] = releaseTitle

        releaseArtists = self.get_release_artists()
        if releaseArtists:
            data['artists'] = releaseArtists

        genres = self.get_genres()
        if genres:
            data['genre'] = genres

        styles = self.get_styles()
        if styles:
            data['style'] = styles

        releaseCountry = self.get_release_country()
        if releaseCountry:
            data['country'] = releaseCountry

        releaseUrl = self.release_url
        if releaseUrl:
            data['link'] = releaseUrl

        discContainers = self.get_disc_containers()
        discs = {}
        discTitles = {}
        for discIndex in discContainers:
            discs[discIndex] = []

            discTitle = self.get_disc_title(discContainers[discIndex])
            if discTitle:
                discTitles[discIndex] = discTitle

            trackContainers = self.get_track_containers(discContainers[discIndex])

            for trackContainer in trackContainers:
                trackNumber = self.get_track_number(trackContainer)
                trackArtists = self.get_track_artists(trackContainer)
                trackTitle = self.get_track_title(trackContainer)
                trackLength = self.get_track_length(trackContainer)

                discs[discIndex].append((trackNumber, trackArtists, trackTitle, trackLength))
        if discs:
            data['discs'] = discs
        if discTitles:
            data['discTitles'] = discTitles

        return data

    @staticmethod
    def _get_args_from_match(match):
        return match.groups()

    @classmethod
    def release_from_url(cls, url):
        m = re.match(cls.url_regex,url)
        if m:
            release = cls(*cls._get_args_from_match(m))
            release._release_url = url
            return release
        else:
            return None


class BaseSearch(ExceptionMixin, RequestMixin, UtilityMixin, LoggerMixin):
    _releases = None

    def raise_request_exception(self, message):
        """
        Make sure the RequestMixin uses ExceptionMixin
        """
        self.raise_exception(message)

    def __init__(self, searchTerm):
        """
        This method creates a new instance of a search with the given tern. The term is saved in an instance attribute
        called 'search_term'.
        """
        self.search_term = searchTerm

    @property
    def releases(self):
        if self._releases is None:
            self._releases = self._extract_releases()
        return self._releases

    def prepare_response_content(self, content):
        """
        This method is called before any other parsing method with the raw content of the response.
        """
        pass

    def get_release_containers(self):
        """
        This method should return a list where each entry is an argument that will be passed to the get_release_*
        methods.
        """
        return []

    def get_release_name(self,releaseContainer):
        """
        This method should return the release name as a string or None.
        """
        return None

    def get_release_info(self,releaseContainer):
        """
        This method should return the release info as a string or None.
        """
        return None

    def get_release_instance(self,releaseContainer):
        """
        This method should return the release instance or None. If this method returns None, the release described by
        the given releaseContainer will not be part of the result list.
        """
        return None

    def _extract_releases(self):
        releases = []

        response = self.get_response()

        self.prepare_response_content(self.get_response_content(response))

        releaseContainers = self.get_release_containers()
        for releaseContainer in releaseContainers:
            releaseName = self.get_release_name(releaseContainer)
            releaseInfo = self.get_release_info(releaseContainer)
            releaseInstance = self.get_release_instance(releaseContainer)

            # we only add releases to the result list that we can actually access
            if releaseInstance is not None:
                releases.append({'name':releaseName,'info':releaseInfo,'release':releaseInstance})

        return releases