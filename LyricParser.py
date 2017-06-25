import html2text

WHITESPACE = 'whitespace'
STRUCTURE = 'structure'
LYRICS = 'lyrics'
CHORDS = 'chords'


class LyricParser:
    html = ""
    lyrics = ""
    lyric_lines = ""
    lyric_ids = {}
    lyric_output = ""

    WHITESPACE = 'whitespace'
    STRUCTURE = 'structure'
    LYRICS = 'lyrics'
    CHORDS = 'chords'

    def __init__(self, html):
        self.html = html
        self.parse()

    def parse(self):
        h = html2text.HTML2Text()
        h.ignore_images = True
        h.ignore_emphasis = True
        h.ignore_links = True

        raw = h.handle(self.html)
        trimmed = self._trim_raw_lyrics(raw)
        self.lyric_lines = trimmed.split("\n")

        self._untabify_trimmed_lyrics()
        self._get_lyric_ids()
        self._get_lyric_output()

    def get_lyrics(self):
        return self.lyric_output

    def _untabify_trimmed_lyrics(self):
        for i in range(len(self.lyric_lines)):
            self.lyric_lines[i] = self.lyric_lines[i].replace("    ", "", 1)

    def _get_lyric_ids(self):
        self.lyric_ids = {}
        illegal_chord_characters = ['h', 'j', 'k', 'l', 'n', 'p', 'q', 'r', 't', 'v', 'w', 'x', 'y', 'z', ',', '.']
        structure_names = ['verse', 'chord', 'bridge', 'prechorus', 'pre-chorus']
        for line in self.lyric_lines:
            if line.isspace():
                self.lyric_ids[line] = WHITESPACE
            elif _contains_any(line, illegal_chord_characters):  # if true, cannot be chord type. decide between structure and lyric.
                trimmed = line.replace(' ', '')
                if trimmed[0:1] == '[' and trimmed[len(trimmed) - 1: len(trimmed)] and line[line.find('[') + 1: line.find(']')].lower() in structure_names:
                    self.lyric_ids[line] = STRUCTURE
                else:
                    self.lyric_ids[line] = LYRICS
            else:  # TODO: handle case where a lyric line happens to only be composed of chord-legal characters. check space intervals.
                self.lyric_ids[line] = CHORDS

    def _get_lyric_output(self):
        i = 0
        while i + 1 < len(self.lyric_lines):
            line = self.lyric_lines[i]
            line_id = self.lyric_ids[line]
            next_line = self.lyric_lines[i + 1]
            next_line_id = self.lyric_ids[next_line]
            if line_id == CHORDS and next_line_id == LYRICS:
                output = ""

                chord_tokens = line.rsplit()
                chord_locations = []
                last_chord_start = 0

                for token in chord_tokens:
                    chord_start = line.find(token, last_chord_start)
                    chord_locations.append(chord_start)
                    last_chord_start = chord_start + 1

                chord_tokens = list(map((lambda x: str.format('\[{0}]', x)), chord_tokens))

                last_chord_location = 0
                for j in range(len(chord_tokens)):
                    output += next_line[last_chord_location: chord_locations[j]]
                    output += chord_tokens[j]
                    last_chord_location = chord_locations[j]

                output += next_line[last_chord_location:] + "\n"

                self.lyric_output += output
                i += 2
            else:
                i += 1

    # static private helpers
    @staticmethod
    def _trim_raw_lyrics(raw):
        start_string = 'Over 1,000,000 guitar, guitar pro and bass tabs! Also lessons'
        start = raw.find(start_string)
        stop_string = 'Suggest correction'
        stop = raw.find(stop_string)
        raw = raw[start + 262:stop]
        return raw


def _contains_any(line, illegal_chord_characters):
    return any(illegal_character in line.lower() for illegal_character in illegal_chord_characters)
