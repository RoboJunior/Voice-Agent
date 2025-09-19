import validators


# To validate wheather its a valid url or not
async def validate_url(url_string: str) -> bool:
    result = validators.url(url_string.strip())
    return result is True
