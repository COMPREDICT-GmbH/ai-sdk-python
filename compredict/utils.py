def adjust_file_name_to_content_type(content_type: str):
    format = content_type.split("/")[1]
    return f"features.{format}"


def extract_error_message(text: str):
    """
    Try to extract error message from AI Core 500 HTML response.
    """
    beginning = text.find("Exception Value:")
    end = text.find("Request information")
    if beginning == -1 or end == -1:
        return "Internal Server Error"
    else:
        return text[beginning + 17:end - 1]
