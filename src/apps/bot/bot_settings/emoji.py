from django.conf import settings

if settings.EMOJI:
    BABY_ANGEL = " \U0001F47C "
    KIDS = " \U0001F467\U0001F466 "

    OK = " \U0001F44D "
    PRESS_BUTTON = " \U0001F447 "
    GO_BACK = " \U0001F448 "
    GO_AHEAD = " \U0001F449 "
    WRITING_HAND = " \U0000270D "
    HANDSHAKE = " \U0001F91D "
    CLAPPING_HANDS = " \U0001F44F "
    SHRUGGING = " \U0001F937 "

    MOTORWAY = " \U0001F6E3 "
    HORSE = " \U0001F40E "
    DESERT_ISLAND = " \U0001F3DD "
    FORCE = " \U0001F4AA "
    RAINING = " \U000026C8 "
    WRESTLING = " \U0001F93C "
    SNOWFLAKE = " \U00002744 "
    VOLCANO = " \U0001F30B "
    AFRIKA = " \U0001F30D "
    AMERICA = " \U0001F30E "
    ASIA = " \U0001F30F "
    FINISH = " \U0001F3C1 "
    PHONE = " \U0001F4F1 "
    EMAIL = " \U0001F4E7 "
    BOOK = " \U0001F4D6 "
    GROWING_HEART = " \U0001F497 "
    SPACER = " "
else:
    BABY_ANGEL = ""
    KIDS = ""

    OK = ""
    PRESS_BUTTON = ""
    GO_BACK = ""
    GO_AHEAD = ""
    WRITING_HAND = ""
    HANDSHAKE = ""
    CLAPPING_HANDS = ""
    SHRUGGING = ""

    MOTORWAY = ""
    HORSE = ""
    DESERT_ISLAND = ""
    FORCE = ""
    RAINING = ""
    WRESTLING = ""
    SNOWFLAKE = ""
    VOLCANO = ""
    AFRIKA = ""
    AMERICA = ""
    ASIA = ""
    FINISH = ""
    PHONE = ""
    EMAIL = ""
    BOOK = ""
    GROWING_HEART = ""
    SPACER = ""

MSK = SPACER + FORCE
MSK_REG = SPACER + MOTORWAY
SPB = SPACER + RAINING
OTHER_REGIONS = SPACER + WRESTLING + SNOWFLAKE + VOLCANO
OUTSIDE_COUNTRY = SPACER + AMERICA + AFRIKA + ASIA
KAZ = SPACER + HORSE
OTHER_COUNTRY = SPACER + DESERT_ISLAND
