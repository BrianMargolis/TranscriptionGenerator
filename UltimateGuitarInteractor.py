import logging
import ssl
from urllib import request

from bs4 import BeautifulSoup, Tag

from HTMLParseError import HTMLParseError
from LyricParser import LyricParser


class UltimateGuitarInteractor:
    export_location = ""
    logger = ""

    main_url = ""
    main_html = ""
    main_header = ""

    print_url = ""
    print_html = ""
    print_header = ""

    title = ""
    artist = ""
    original_transcriber = ""
    capo = 0

    lyrics = ""

    # testing
    success = [0, 0, 0, 0]

    def __init__(self, url, export_location, logger_name):
        self.main_url = url
        self.export_location = export_location
        self.logger = logging.getLogger(logger_name)

    def run(self):
        """Run a full execution cycle."""
        self.main_html, self.main_header = self._get_html_and_header(self.main_url)
        self.logger.debug("main HTML and main header.")

        self.title, self.artist, self.original_transcriber, self.capo = self.get_metadata()
        self.logger.debug("title: {0}".format(self.title))
        self.logger.debug("artist: {0}".format(self.artist))
        if self.original_transcriber != "":
            self.logger.debug("original transcriber: {0}".format(self.original_transcriber))
        else:
            self.logger.warning("No original transcriber found.")
        self.logger.debug("capo: {0}".format(str(self.capo)))

        self.print_url = self.get_print_url()
        self.logger.debug("print url: {0}".format(self.print_url))

        self.print_html, self.print_header = self._get_html_and_header(self.print_url)
        self.logger.debug("print HTML and print header.")

        self.lyrics = self.get_lyrics()
        self.logger.debug("lyrics.")

        self._export_tex_file()
        self.logger.debug("Exported.")

        # testing
        self._set_success()

    def get_metadata(self) -> [str, str, str, int]:
        """Parse the main HTML for the song title and artist, original transcriber username, and capo #."""
        title = ""
        artist = ""
        original_transcriber = ""
        capo = 0

        # get the page title for the song title and artist
        soup = BeautifulSoup(self.main_html, "html.parser")
        page_title_result = soup.findAll('title')[0]
        page_title_contents = page_title_result.contents
        page_title = str(page_title_contents[0]).lower()
        # assume [title] CHORDS (ver x) by [artist]
        title = page_title[:page_title.find(" chords")]
        artist = page_title[page_title.find("by ") + 3:page_title.find(" @ ultimate-guitar.com")]

        t_dtdes = soup.findAll('div', attrs={'class': 't_dtde'})

        for t_dtde in t_dtdes:
            if len(t_dtde.contents) > 0 and ' fret ' in t_dtde.contents[0]:
                capo_string = str(t_dtde.contents[0])
                capo = int(capo_string[capo_string.find("fret") - 4:capo_string.find("fret") - 3])
            elif len(t_dtde.contents) >= 6 and 'href' in t_dtde.contents[1].attrs and 'http://profile.ultimate-guitar.com/' in t_dtde.contents[1].attrs['href']:
                username_tag = t_dtde.contents[1]
                username = username_tag.next
                original_transcriber = str(username)

        return title, artist, original_transcriber, capo

    def get_print_url(self):
        """Parse the main HTML for the print url."""
        soup = BeautifulSoup(self.main_html, "html.parser")
        url_code = ""
        url_code_1 = ""
        url_code_2 = ""

        # method 1
        parent_candidates = soup.findAll('div', attrs={"class": "adv-sms-fixed--footer"})
        if len(parent_candidates) > 1:
            raise IOError
        parent = parent_candidates[0]
        children = parent.contents
        for child in children:
            if type(child) == Tag:
                attrs = child.attrs
                if 'name' in attrs and 'value' in attrs and attrs['name'] == 'id':
                    url_code_1 = attrs['value']

        # method 2
        id_candidates = soup.findAll('input', attrs={"name": "id"})
        if len(id_candidates) > 1:
            raise IOError
        id = id_candidates[0]
        url_code_2 = id.attrs['value']

        if url_code_1 == url_code_2 and url_code_1 != "":
            url_code = url_code_1
        else:
            raise HTMLParseError("Error getting the print url")

        return "https://tabs.ultimate-guitar.com/print/{0}?simplified=0".format(url_code)

    def get_lyrics(self):
        """Parse the print html for lyrics."""
        lp = LyricParser(self.print_html)
        return lp.get_lyrics()

    def get_title_and_artist_string(self):
        """Get a human-readable string containing the title and artist."""
        return "{0} by {1}".format(self.title, self.artist)

    @staticmethod
    def _get_html_and_header(url: str) -> [str, str]:
        logging.debug("Getting HTML and header from {0}".format(url))
        context = ssl._create_unverified_context()  # TODO: make this less sketchy
        website = request.urlopen(url, context=context)
        html = website.read().decode("utf-8")
        header = website.info()
        return [html, header]

    def _export_tex_file(self):
        """Create a .tex file holding the lyrics."""
        if not self.export_location.endswith('/'):
            formatted_export_location = self.export_location + '/'
        else:
            formatted_export_location = self.export_location
        formatted_artist = self.artist.lower().replace(' ', '_')
        formatted_title = self.title.replace(' ', '_')

        file_name = "{0}{1}__{2}.tex".format(formatted_export_location, formatted_artist, formatted_title)
        with open(file_name, 'w') as file:
            file.write(self.lyrics)

    # testing
    def _set_success(self):
        self.success[0] = self.title != ""
        self.success[1] = self.artist != ""
        self.success[2] = self.original_transcriber != ""
        self.success[3] = self.capo > 0

    # testing
    def get_success(self):
        return self.success
