"""Generic utility functions."""
from __future__ import unicode_literals, print_function, division, absolute_import
import re

from six import add_metaclass
from sqlalchemy.types import SchemaType, TypeDecorator, Enum
from clldutils import misc
from clldutils import jsonlib


DATETIME_ISO_FORMAT = jsonlib.DATETIME_ISO_FORMAT


def summary(text, max_length=70):
    res = ''
    words = list(reversed(text.split()))
    while words:
        nextword = words.pop()
        if len(res) + len(nextword) + 1 > max_length:
            # too long, add the word back onto the remainder
            words.append(nextword)
            break
        res += ' ' + nextword
    if words:
        res += ' ...'
    return res.strip()


parse_json_with_datetime = jsonlib.parse
format_json = jsonlib.format
jsondump = jsonlib.dump
jsonload = jsonlib.load
nfilter = misc.nfilter
to_binary = misc.to_binary
dict_merged = misc.dict_merged

#: A singleton which can be used to distinguish no-argument-passed from None passed as
#: argument in callables with optional arguments.
NO_DEFAULT = misc.NO_DEFAULT

xmlchars = misc.xmlchars
UnicodeMixin = misc.UnicodeMixin
format_size = misc.format_size
slug = misc.slug
encoded = misc.encoded
cached_property = misc.cached_property


#
# From "The Enum Recipe": http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
#
class EnumSymbol(UnicodeMixin):

    """Define a fixed symbol tied to a parent class."""

    def __init__(self, cls_, name, value, description, *args):
        self.cls_ = cls_
        self.name = name
        self.value = value
        self.description = description
        self.args = args

    def __reduce__(self):
        """Allow unpickling to return the symbol linked to the DeclEnum class."""
        return getattr, (self.cls_, self.name)  # pragma: no cover

    def __iter__(self):
        return iter([self.value, self.description])

    def __repr__(self):
        return "<%s>" % self.name

    def __unicode__(self):
        return self.value

    def __lt__(self, other):
        return self.value < getattr(other, 'value', None)

    def __json__(self, request=None):
        return self.value


class EnumMeta(type):

    """Generate new DeclEnum classes."""

    def __init__(cls, classname, bases, dict_):
        cls._reg = reg = cls._reg.copy()
        for k, v in dict_.items():
            if isinstance(v, tuple):
                sym = reg[v[0]] = EnumSymbol(cls, k, *v)
                setattr(cls, k, sym)
        return type.__init__(cls, classname, bases, dict_)

    def __iter__(cls):
        return iter(sorted(cls._reg.values()))


@add_metaclass(EnumMeta)
class DeclEnum(object):

    """Declarative enumeration."""

    _reg = {}

    @classmethod
    def from_string(cls, value):
        try:
            return cls._reg[value]
        except KeyError:
            raise ValueError("Invalid value for %r: %r" % (cls.__name__, value))

    @classmethod
    def values(cls):
        return list(cls._reg.keys())

    @classmethod
    def db_type(cls):
        return DeclEnumType(cls)


class DeclEnumType(SchemaType, TypeDecorator):
    def __init__(self, enum):
        self.enum = enum
        self.impl = Enum(
            *enum.values(),
            name="ck%s" % re.sub(
                '([A-Z])', lambda m: "_" + m.group(1).lower(), enum.__name__))

    def _set_table(self, table, column):
        self.impl._set_table(table, column)  # pragma: no cover

    def copy(self):
        return DeclEnumType(self.enum)  # pragma: no cover

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum.from_string(value.strip())


# Standard abbreviations according to the Leipzig Glossing Rules
# see http://www.eva.mpg.de/lingua/resources/glossing-rules.php
LGR_ABBRS = {
    'A': 'agent-like argument of canonical transitive verb',
    'ABL': 'ablative',
    'ABS': 'absolutive',
    'ACC': 'accusative',
    'ADJ': 'adjective',
    'ADV': 'adverb(ial)',
    'AGR': 'agreement',
    'ALL': 'allative',
    'ANTIP': 'antipassive',
    'APPL': 'applicative',
    'ART': 'article',
    'AUX': 'auxiliary',
    'BEN': 'benefactive',
    'CAUS': 'causative',
    'CLF': 'classifier',
    'COM': 'comitative',
    'COMP': 'complementizer',
    'COMPL': 'completive',
    'COND': 'conditional',
    'COP': 'copula',
    'CVB': 'converb',
    'DAT': 'dative',
    'DECL': 'declarative',
    'DEF': 'definite',
    'DEM': 'demonstrative',
    'DET': 'determiner',
    'DIST': 'distal',
    'DISTR': 'distributive',
    'DU': 'dual',
    'DUR': 'durative',
    'ERG': 'ergative',
    'EXCL': 'exclusive',
    'F': 'feminine',
    'FOC': 'focus',
    'FUT': 'future',
    'GEN': 'genitive',
    'IMP': 'imperative',
    'INCL': 'inclusive',
    'IND': 'indicative',
    'INDF': 'indefinite',
    'INF': 'infinitive',
    'INS': 'instrumental',
    'INTR': 'intransitive',
    'IPFV': 'imperfective',
    'IRR': 'irrealis',
    'LOC': 'locative',
    'M': 'masculine',
    'N': 'neuter',
    'N-': 'non- (e.g. NSG nonsingular, NPST nonpast)',
    'NEG': 'negation, negative',
    'NMLZ': 'nominalizer/nominalization',
    'NOM': 'nominative',
    'OBJ': 'object',
    'OBL': 'oblique',
    'P': 'patient-like argument of canonical transitive verb',
    'PASS': 'passive',
    'PFV': 'perfective',
    'PL': 'plural',
    'POSS': 'possessive',
    'PRED': 'predicative',
    'PRF': 'perfect',
    'PRS': 'present',
    'PROG': 'progressive',
    'PROH': 'prohibitive',
    'PROX': 'proximal/proximate',
    'PST': 'past',
    'PTCP': 'participle',
    'PURP': 'purposive',
    'Q': 'question particle/marker',
    'QUOT': 'quotative',
    'RECP': 'reciprocal',
    'REFL': 'reflexive',
    'REL': 'relative',
    'RES': 'resultative',
    'S': 'single argument of canonical intransitive verb',
    'SBJ': 'subject',
    'SBJV': 'subjunctive',
    'SG': 'singular',
    'TOP': 'topic',
    'TR': 'transitive',
    'VOC': 'vocative',
}
