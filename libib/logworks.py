# Standard libs:
import json
import logging

# Classes:
class Logger(object):
    """Class to hold logging stuff."""
    
    # Class variables:
    PLAIN_FORMATTER = logging.Formatter(
            fmt='{asctime} [{levelname}] {message}',
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{")

    COLOR_FORMATTER = logging.Formatter(
            fmt='{asctime} \033[{clevel}m[{levelname}]\033[0m {message}',
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{")


    # Constructor:
    def __init__(self, conf_fn=None, nocolor=False):
        # If given a configuration file name, try to read it:
        self.conf = self.read_conf(conf_fn)

        # Avoid colors?:
        self.nocolor = nocolor

        # Logger object:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # Console output handler:
        ch = logging.StreamHandler()
        if self.use_colors:
            ch.setFormatter(self.COLOR_FORMATTER)
        else:
            ch.setFormatter(self.PLAIN_FORMATTER)
        ch.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)


    # Public methods:
    def read_conf(self, fn=None):
        """Read configuration file 'fn' and return dictionary with configuration.
        Return empty dir if we couldn't read.
        """
        if not fn:
            return {}

        try:
            with open(fn) as f_conf:
                return json.load(f_conf)
        except FileNotFoundError:
            print("Could not read logger configuration file '{f}'. Ignoring...".format(f=fn))
            return {}

    def info(self, text):
        """Log (print) 'text' as info."""

        extra = {
            "clevel": self._color_for("info"),
        }

        self.logger.info(text, extra=extra)

    def warning(self, text):
        """Log (print) 'text' as warning."""

        extra = {
            "clevel": self._color_for("warning"),
        }

        self.logger.warning(text, extra=extra)

    def error(self, text):
        """Log (print) 'text' as error."""

        extra = {
            "clevel": self._color_for("error"),
        }

        self.logger.error(text, extra=extra)

    def name_color(self, text):
        """Return 'text' with color for name."""

        return self._colorize_as(text, "name")


    # Private methods:
    def _colorize_as(self, text, which):
        """Return 'text' with color for 'which' type of text."""

        if self.use_colors:
            return Logger.colorize(text, self._color_for(which))
        
        return text

    def _color_for(self, which):
        """Return color for 'which'."""

        try:
            return self.conf["colors"][which]
        except:
            return 0


    # Public properties:
    @property
    def use_colors(self):
        """Return True if colors should be used in terminal.
        False otherwise.
        """
        if self.nocolor:
            return False

        return "colorize" in self.conf and self.conf["colorize"]


    # Static methods:
    @staticmethod
    def colorize(text, color_number=None):
        """Return colorized version of 'text', with terminal color 'color_number' (31, 32...).
        Return bare text if 'color_number' is None.
        """
        if color_number is None:
            return text

        return "\033[{n}m{t}\033[0m".format(t=text, n=color_number)

