from gallicaGetter.parse.parseHTML import parse_html


def parse_responses_to_records(responses):
    return (parse_html(response.data) for response in responses)
