import ssl
import urllib.request as url
from html.parser import HTMLParser as Parser


class UltimateGuitarInteractor:
    main_link = ""
    main_html = ""
    main_header = ""
    print_link = ""
    print_html = ""

    title = ""
    artist = ""
    original_transcriber = ""
    capo = 0

    lyrics = ""

    def __init__(self, link):
        self.main_link = link

    def run(self):
        """
        Runs a full execution cycle on the object.

        :return: void
        """
        self.parse_main_link()
        self.parse_for_lyrics()
        self.export_to_tex_file()

    def parse_main_link(self):
        """
        Navigates to the link specified on object creation and parses the HTML for the:
        title
        artist
        original transcriber username
        capo #
        print link (the link to the print context of the page)

        :return: void
        """
        context = ssl._create_unverified_context()
        website = url.urlopen(self.main_link, context=context)
        self.main_html = website.read().decode("utf-8")
        self.main_header = website.info()

    def parse_for_lyrics(self):
        """
        Navigates to the print link and parses it for lyrics.

        :return: void
        """
        p = Parser()
        p.feed(self.main_html)

    def export_to_tex_file(self):
        """
        Creates a .tex file holding the lyrics.

        :return: void
        """
        file_name = "{0}__{1}.tex".format(self.artist.lower().replace(" ", "_"), self.title.replace(" ", "_"))
        with open(file_name, "w'") as file:
            file.write(self.lyrics)
