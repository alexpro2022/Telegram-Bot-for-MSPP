# CallBack Query data (reserved 0-99)
(
    GET_AGE,
    GET_LOCATION,
    GET_COUNTRY,
    GET_REGION,
    GET_CITY_OR_AND_FUND,
    GET_FUND,
    GET_FUNDS_INFO,
    NO_FUND,
    GET_NEW_FUND_FORM,
    GET_NEW_MENTOR_FORM,
    SEND_NEW_MENTOR_FORM,
    SEND_NEW_FUND_FORM,
    GO_BACK,
) = map(chr, range(13))
