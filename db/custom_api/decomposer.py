"""Decompose custom URL.

    URL format (? marks optional parameter):

    {domain}/series/{varname}/{freq}/{?suffix}/{?start}/{?end}/{?finaliser}

    Examples:
        oil/series/BRENT/m/eop/2015/2017/csv
        ru/series/EXPORT_GOODS/m/bln_rub

    Tokens:
        {domain} is reserved, future use: 'all', 'ru', 'oil', 'ru:bank', 'ru:77'

        {varname} is GDP, GOODS_EXPORT, BRENT (capital letters with underscores)

        {freq} is any of:
            a (annual)
            q (quarterly)
            m (monthly)
            w (weekly)
            d (daily)

        {?suffix} may be:

            unit of measurement (unit):
                example: bln_rub, bln_usd, tkm

            rate of change for real variable (rate):
                rog - change to previous period
                yoy - change to year ago
                base - base index

            aggregation command (agg):
                eop - end of period
                avg - average
"""

from datetime import date

from db.api.errors import CustomError400

ALLOWED_FREQUENCIES = ('d', 'w', 'm', 'q', 'a')

ALLOWED_REAL_RATES = (
    'rog',
    'yoy',
    'base'
)
ALLOWED_AGGREGATORS = (
    'eop',
    'avg'
)
ALLOWED_FINALISERS = (
    # 'info',  # resereved: retrun json with variable and url description
    'csv',   # to implement: return csv (default)
    'json',  # to implement: return list of dictionaries
    # 'xlsx'   # resereved: return Excel file
)


def as_date(year: int, month: int, day: int):
    """Generate YYYY-MM-DD dates based on components."""
    return date(year=year,
                month=month,
                day=day).strftime('%Y-%m-%d')


class ListElements(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def get_years(self):
        """Extract years from *tokens* list.
           Pops values found away from *tokens*.
        """
        start, end = None, None
        integers = [x for x in self.tokens if x.isdigit()]
        n_years_found = len(integers)
        if n_years_found == 1:
            start = int(integers[0])
        if n_years_found == 2:
            end = int(integers[1])
        for year in integers:
            self._pop(year)
        return start, end

    def _pop(self, value):
        self.tokens.pop(self.tokens.index(value))

    def get_one(self, allowed_values):
        """Find entries of *allowed_values* list into *tokens* list.
           Pops values found away from *tokens*.
           Return None or one value found.
        """
        values_found = [p for p in allowed_values if p in self.tokens]
        if not values_found:
            return None
        elif len(values_found) == 1:
            x = values_found[0]
            self._pop(x)
            return x
        else:
            raise CustomError400(values_found)

    def first(self):
        if len(self.tokens) == 1:
            return self.tokens[0]
        else:
            return False


class Tokens(object):
    def __init__(self, inner_path: str):
        # make list of non-empty strings
        tokens = [token.strip() for token in inner_path.split('/') if token]
        elements = ListElements(tokens)
        self.start_year, self.end_year = elements.get_years()
        # order of assignment is important as .get_one() modifis state of 'elements'
        self._fin = elements.get_one(ALLOWED_FINALISERS)
        self._rate = elements.get_one(ALLOWED_REAL_RATES)
        self._agg = elements.get_one(ALLOWED_AGGREGATORS)
        if elements.first():
            self._unit = elements.first()
        else:
            self._unit = self._rate or None

    @property
    def unit(self):
        return self._unit

    @property
    def start(self):
        if self.start_year:
            return as_date(self.start_year, month=1, day=1)
        else:
            return None

    @property
    def end(self):
        if self.end_year:
            return as_date(self.end_year, month=12, day=31)
        else:
            today = date.today()
            return as_date(today.year, today.month, today.day)

    # not used
    @property
    def fin(self):
        return self._fin

    @property
    def rate(self):
        return self._rate

    # not used
    @property
    def agg(self):
        return self._agg


def validate_frequency(freq):
    if freq not in ALLOWED_FREQUENCIES:
        raise CustomError400(f'Frequency <{freq}> is not valid')


def validate_rate_and_agg(rate, agg):
    if rate and agg:
        raise CustomError400("Cannot combine rate and aggregation.")



class Indicator(object):

    def __init__(self, domain, varname, freq, inner_path):
        self.varname = varname
        validate_frequency(freq)
        self._freq = freq
        self.token = Tokens(inner_path)
        validate_rate_and_agg(self.token.rate, self.token.agg)

    @property
    def start_date(self):
        return self.token.start

    @property
    def end_date(self):
        return self.token.end

    @property
    def freq(self):
        return self._freq

    @property
    def name(self):
        # BRENT or GDP_yoy
        name = self.varname
        # may add rate or arbitrary string
        unit = self.token.unit
        if unit:
            name = f'{name}_{unit}'
        return name

    @property
    def query_param(self):
        keys = 'name', 'freq', 'start_date', 'end_date'
        return {key: getattr(self, key) for key in keys}
