import ssl
import urllib.request as url
from html.parser import HTMLParser as Parser


class UltimateGuitarInteractor:
    export_location = ""
    logger_name = ""

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

    def __init__(self, link, export_location, logger_name):
        self.main_link = link
        self.export_location = export_location
        self.logger_name = logger_name

    def run(self):
        """Run a full execution cycle."""
        self.get_main_html()
        self.get_print_link()
        self.get_print_html()
        self.get_metadata()
        self.get_lyrics()
        self.export_tex_file()

    def get_main_html(self):
        """Navigate to the main link specified on object creation and gets the HTML."""
        context = ssl._create_unverified_context()
        website = url.urlopen(self.main_link, context=context)
        self.main_html = website.read().decode("utf-8")
        self.main_header = website.info()
        # TODO: generate print link and get HTML

    def get_print_html(self):
        """Navigate to the print link specified on object creation and gets the HTML."""
        context = ssl._create_unverified_context()
        website = url.urlopen(self.print_link, context=context)
        self.print_html = website.read().decode("utf-8")

    def get_metadata(self):
        """Parse the main HTML for the song title and artist, original transcriber username, and capo #."""
        raise NotImplementedError

    def get_print_link(self):
        """Parse the main HTML for the print link."""
        raise NotImplementedError

    def get_lyrics(self):
        """Navigate to the print link and parse it for lyrics."""
        p = Parser()
        p.feed(self.print_html)
        # TODO: parse for lyrics

    def export_tex_file(self):
        """Create a .tex file holding the lyrics."""
        # TODO: accommodate export_location
        file_name = "{0}__{1}.tex".format(self.artist.lower().replace(" ", "_"), self.title.replace(" ", "_"))
        with open(file_name, "w'") as file:
            file.write(self.lyrics)

    def get_title_and_artist(self):
        return "{0} by {1}".format(self.title, self.artist)
