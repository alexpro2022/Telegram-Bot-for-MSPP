from . import emoji

ARITHMETIC = "Арифметика добра"
ARITHMETIC_FUND = (
    ARITHMETIC + " - помогает детям-сиротам стать личностью, "
    "поддерживает приемные семьи, содействует семейному устройству.")

ELDER_BROTHERS = "Старшие братья старшие сестры"
ELDER_BROTHERS_FUND = (
    ELDER_BROTHERS + " - подбирает наставников детям и "
    "подросткам, находящихся в трудной жизненной ситуации.")

IN_YOUR_HANDS = "В твоих руках"
IN_YOUR_HANDS_FUND = (
    IN_YOUR_HANDS + " - помогает подросткам, оставшимся без поддержки "
    "родителей, подготовиться к самостоятельной жизни.")

VOLONTIERS = "Волонтеры в помощь детям-сиротам"
VOLONTIERS_FUND = (
    VOLONTIERS + " - помогает детям сиротам в "
    "детских домах и больницах, ищет им приемных родителей и "
    "поддерживает семьи в трудной жизненной ситуации.")

KIDS_PLUS = "Дети плюс"
KIDS_PLUS_FUND = (
    KIDS_PLUS + " - оказывает поддержку детям, подросткам и молодым людям с "
    "ВИЧ, семьям, в которых живут дети с ВИЧ.")

OUR_KIDS = "Дети наши"
OUR_KIDS_FUND = (
    " - помогает в социальной адаптации воспитанников "
    "детских домов, поддерживает кризисные семьи.")

SUN_CITY = "Солнечный город"
SUN_CITY_FUND = (
    SUN_CITY + " - помогает детям и семьям, которые оказались "
    "в трудной жизненной ситуации.")

FUNDS_INFO_SEPARATOR = f"\n{emoji.GROWING_HEART*3}\n"

FUNDS = {
    ARITHMETIC: ARITHMETIC_FUND,
    ELDER_BROTHERS: ELDER_BROTHERS_FUND,
    IN_YOUR_HANDS: IN_YOUR_HANDS_FUND,
    VOLONTIERS: VOLONTIERS_FUND,
    KIDS_PLUS: KIDS_PLUS_FUND,
    OUR_KIDS: OUR_KIDS_FUND,
    SUN_CITY: SUN_CITY_FUND,
}


'''
FUNDS_TEXT = (
    conversation.BOT_SPEAKING + ARITHMETIC_FUND,
    ELDER_BROTHERS_FUND,
    IN_YOUR_HANDS_FUND,
    VOLONTIERS_FUND,
    KIDS_PLUS_FUND,
    OUR_KIDS_FUND,
    SUN_CITY_FUND,
)
DESCRIPTION = FUNDS_INFO_SEPARATOR.join(FUNDS_TEXT)

'''
