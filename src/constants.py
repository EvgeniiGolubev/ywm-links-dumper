API_BASE = "https://api.webmaster.yandex.net/v4"
XLSX_FIELDS = ["source_url", "destination_url", "discovery_date", "source_last_access_date"]
BAD_KEYWORDS = [
    # adult
    "porn", "porno", "pornhub", "xvideos", "xnxx", "xxx",
    "sex", "hentai", "nude", "cam", "cams", "webcam",
    "onlyfans", "erotic", "escort",

    # gambling
    "casino", "slots", "slot", "roulette", "poker",
    "bookmaker", "bookie", "bet", "bets", "betting",
    "stake", "wager", "1xbet", "parimatch", "fonbet",
    "leonbets", "melbet", "vulkan", "joycasino",
    "pin-up", "pinup", "gg.bet", "bet365", "marathonbet",

    # loans / scams
    "payday", "loan", "microloan", "mfo",

    # pharma
    "viagra", "cialis", "levitra", "tramadol", "modafinil",
    "steroids", "anabolic", "clenbuterol", "pharmacy", "pills",

    # drugs
    "cannabis", "marijuana", "weed", "hash", "kush", "cbd",
    "lsd", "mdma", "ecstasy",

    # piracy
    "torrent", "torrents", "warez", "pirate", "crack",
    "keygen", "serials", "nulled", "mod apk", "apk mod",
    "free download full",

    # dating / spam
    "adult", "dating", "hookup", "milfs", "camgirls",
    "livejasmin", "bongacams", "chaturbate",

    # hyip / binary options
    "hyip", "ponzi", "binary", "options",
]