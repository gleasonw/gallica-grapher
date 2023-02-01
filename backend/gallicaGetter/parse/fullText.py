from parse.parseHTML import parse_html


def parse_responses_to_records(responses, on_get_total_records):
    return (parse_html(response.xml) for response in responses)
