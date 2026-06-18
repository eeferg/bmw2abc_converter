# Grace note and decoration lookup tables.
# Ported from bww2abc.js by Jean-Francois Moine (GPL3+).
# BWW token -> ABC grace note sequence (placed inside {})
# ABC pitch letters: G=Low-G, A=Low-A, B=B, c=C, d=D, e=E, f=F, g=High-G, a=High-A

GRACE: dict[str, str] = {
    # Single Grace notes
    "ag": "A",
    "bg": "B",
    "cg": "c",
    "dg": "d",
    "eg": "e",
    "fg": "f",
    "gg": "g",
    "tg": "a",

    # Regular Doublings
    "dblg": "gGd",
    "dbla": "gAd",
    "dbb": "gBd",
    "dbc": "gcd",
    "dbd": "gde",
    "dbe": "gef",
    "dbf": "gfg",
    "dbhg": "gf",
    "dbha": "ag",

    # Thumb Doublings
    "tdblg": "aGd",
    "tdbla": "aAd",
    "tdbb": "aBd",
    "tdbc": "acd",
    "tdbd": "ade",
    "tdbe": "aef",
    "tdbf": "afg",

    # Half Doublings
    "hdblg": "Gd",
    "hdbla": "Ad",
    "hdbb": "Bd",
    "hdbc": "cd",
    "hdbd": "de",
    "hdbe": "ef",
    "hdbf": "fg",

    # Single Strikes (same pitch class as single grace notes)
    "strlg": "G",
    "strla": "A",
    "strb": "B",
    "strc": "c",
    "strd": "d",
    "stre": "e",
    "strf": "f",
    "strhg": "g",

    # G Grace note Strikes
    "gstla": "gAG",
    "gstb": "gBG",
    "gstc": "gcG",
    "gstd": "gdG",
    "lgstd": "gec",
    "gste": "geA",
    "gstf": "gfe",

    # Thumb Strikes
    "tstla": "aAG",
    "tstb": "aBG",
    "tstc": "acG",
    "tstd": "adG",
    "ltstd": "adc",
    "tste": "aeA",
    "tstf": "afe",
    "tsthg": "agf",

    # Half Strikes
    "hstla": "AG",
    "hstb": "BG",
    "hstc": "cG",
    "hstd": "dG",
    "lhstd": "ed",
    "hste": "eA",
    "hstf": "fe",
    "hsthg": "gf",

    # Regular Grips
    "grp": "GdG",
    "hgrp": "dG",
    "grpb": "GBG",

    # G Grace note Grips
    "ggrpla": "gAGdG",
    "ggrpb": "gBGdG",
    "ggrpc": "gcGdG",
    "ggrpd": "gdGdG",
    "ggrpdb": "gdGBG",
    "ggrpe": "geGdG",
    "ggrpf": "gfGfG",

    # Thumb Grips
    "tgrpla": "aAGdG",
    "tgrpb": "aBGdG",
    "tgrpc": "acGdG",
    "tgrpd": "adGdG",
    "tgrpdb": "adGBG",
    "tgrpe": "aeGdG",
    "tgrpf": "afGfG",
    "tgrphg": "agGfG",

    # Half Grips
    "hgrpla": "AGdG",
    "hgrpb": "BGdG",
    "hgrpc": "cGdG",
    "hgrpd": "dGdG",
    "hgrpdb": "dGBG",
    "hgrpe": "eGdG",
    "hgrpf": "fGfG",
    "hgrphg": "gGdG",
    "hgrpha": "aGdG",

    # Taorluaths and Bublys
    "tar": "GdGe",
    "tarb": "GBGe",
    "htar": "dGe",
    "bubly": "GeGcG",
    "hbubly": "dGcG",

    # Birls
    "brl": "GAG",
    "abr": "AGAG",
    "gbr": "gAGAG",
    "tbr": "aAGAG",

    # Light, Heavy and Half D Throws
    "thrd": "Gdc",
    "hvthrd": "GdGc",
    "hthrd": "dc",
    "hhvthrd": "dGc",

    # Regular Peles
    "pella": "gAeAG",
    "pelb": "gBeBG",
    "pelc": "gcecG",
    "peld": "gdedG",
    "lpeld": "gdedc",
    "pele": "gefea",
    "pelf": "gfgfe",

    # Thumb Peles
    "tpella": "aAeAG",
    "tpelb": "aBeBG",
    "tpelc": "acecG",
    "tpeld": "adedG",
    "ltpeld": "adedc",
    "tpele": "aefeA",
    "tpelf": "afgfe",
    "tpelhg": "agagf",

    # Half Peles
    "hpella": "AeAG",
    "hpelb": "BeBG",
    "hpelc": "cecG",
    "hpeld": "dedG",
    "lhpeld": "dedc",
    "hpele": "efeA",
    "hpelf": "fgfe",
    "hpelhg": "gagf",

    # Regular Double Strikes
    "st2la": "GAG",
    "st2b": "GBG",
    "st2c": "GcG",
    "st2d": "GdG",
    "lst2d": "cdc",
    "st2e": "AeA",
    "st2f": "efe",
    "st2hg": "fgf",
    "st2ha": "gag",

    # G Grace note Double Strikes
    "gst2la": "gAGAG",
    "gst2b": "gBGBG",
    "gst2c": "gcGcG",
    "gst2d": "gdGdG",
    "lgst2d": "gdcdc",
    "gst2e": "geAeA",
    "gst2f": "gfefe",

    # Thumb Double Strikes
    "tst2la": "aAGAG",
    "tst2b": "aBGBG",
    "tst2c": "acGcG",
    "tst2d": "adGdG",
    "ltst2d": "adcdc",
    "tst2e": "aeAeA",
    "tst2f": "afefe",
    "tst2hg": "agfgf",

    # Half Double Strikes
    "hst2la": "AGAG",
    "hst2b": "BGBG",
    "hst2c": "cGcG",
    "hst2d": "dGdG",
    "lhst2d": "dcdc",
    "hst2e": "eAeA",
    "hst2f": "fdfd",
    "hst2hg": "gfgf",
    "hst2ha": "agag",

    # Regular Triple Strikes
    "st3la": "GAGAG",
    "st3b": "GBGBG",
    "st3c": "GcGcG",
    "st3d": "GdGdG",
    "lst3d": "cdcdc",
    "st3e": "AeAeA",
    "st3f": "efefe",
    "st3hg": "fgfgf",
    "st3ha": "gagag",

    # G Grace note Triple Strikes
    "gst3la": "gAGAGAG",
    "gst3b": "gBGBGBG",
    "gst3c": "gcGcGcG",
    "gst3d": "gdGdGdG",
    "lgst3d": "gdcdcdc",
    "gst3e": "geAeAeA",
    "gst3f": "gfefefe",

    # Thumb Triple Strikes
    "tst3la": "aAGAGAG",
    "tst3b": "aBGBGBG",
    "tst3c": "acGcGcG",
    "tst3d": "adGdGdG",
    "ltst3d": "adcdcdc",
    "tst3e": "aeA2AeA",
    "tst3f": "afefefe",
    "tst3hg": "agfgfgf",

    # Half Triple Strikes
    "hst3la": "AGAGAG",
    "hst3b": "BGBGBG",
    "hst3c": "cGcGcG",
    "hst3d": "dGdGdG",
    "lhst3d": "dcdcdc",
    "hst3e": "eAeAEA",
    "hst3f": "fefefe",
    "hst3hg": "gfgfgf",
    "hst3ha": "agagag",

    # Double Grace Notes
    "dlg": "dG",
    "dla": "dA",
    "db": "dB",
    "dc": "dc",
    "elg": "eG",
    "ela": "eA",
    "eb": "eB",
    "ec": "ec",
    "ed": "ed",
    "flg": "fG",
    "fla": "fA",
    "fb": "fB",
    "fc": "fc",
    "fd": "fd",
    "fe": "fe",
    "glg": "gG",
    "gla": "gA",
    "gb": "gB",
    "gc": "gc",
    "gd": "gd",
    "ge": "ge",
    "gf": "gf",
    "tlg": "aG",
    "tla": "aA",
    "tb": "aB",
    "tc": "ac",
    "td": "ad",
    "te": "ae",
    "tf": "af",
    "thg": "ag",

    # Cadences
    "cadged": "ge4d",
    "cadge": "ge4",
    "caded": "e4d",
    "cade": "e4",
    "cadaed": "ae4d",
    "cadae": "ae4",
    "fcadged": "gHe4d",
    "fcadge": "gHe4",
    "fcaded": "He4d",
    "fcade": "He4",
    "fcadaed": "aHe4d",
    "fcadae": "aHe4",
    "cadgf": "gf4",
    "cadaf": "af4",
    "fcadgf": "gHf4",
    "fcadaf": "aHf4",

    # E, F and High G Throws
    "embari": "eAfA",
    "endari": "fege",
    "chedari": "geae",

    # High A and D Throws
    "dili": "ag",
    "tra": "G2dc",
    "htra": "dc",
    "tra8": "G2dc",

    # G Grace note, Thumb and Half Throws
    "gedre": "geAfA",
    "gdare": "gfege",
    "tedre": "aeAfA",
    "tdare": "afege",
    "tchechere": "ageae",
    "dre": "AfA",
    "hedale": "ege",
    "hchechere": "eae",

    # Grips (alternate)
    "deda": "GeG",

    # Echo Beat Grace notes
    "echolg": "G2",
    "echola": "A2",
    "echob": "B2",
    "echoc": "c2",
    "echod": "d2",
    "echoe": "e2",
    "echof": "f2",
    "echohg": "g2",
    "echoha": "a2",

    "darodo": "GdGcG",
    "darodo16": "G2dGcG2",
    "hdarodo": "dGcG",
    "hiharin": "dAGAG",
    "rodin": "GBG",
    "chelalho": "f4de",
    "din": "G2",
}

# Decoration tokens: BWW token -> ABC decoration string (placed before the note)
DECO: dict[str, str] = {
    "pembari": "P",
    "pendari": "P",
    "pechedari": "P",
    "pehedari": "P",
    "pdili": "!trill!",
    "ptra": "!trill!",
    "phtra": "!trill!",
    "ptra8": "!trill!",
    "pgrp": "!trill!",
    "pdarodo": "!turn!",
    "pdarodo16": "!turn!",
    "phdarodo": "!turn!",
    "phiharin": "P",
    "fine": "!fine!y",
    "dacapoalfine": "!D.C.alfine!y",
    "coda": "O",
    "dacapoalcoda": "!D.C.alcoda!y",
    "codasection": "O",
}
