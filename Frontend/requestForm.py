from wtforms import ValidationError, Form, TextAreaField, BooleanField, StringField, validators
import re

class Regexp(object):
	"""
    Validates the field against a user provided regexp.

    :param regex:
        The regular expression string to use. Can also be a compiled regular
        expression pattern.
    :param flags:
        The regexp flags to use, for example re.IGNORECASE. Ignored if
        `regex` is not a string.
    :param message:
        Error message to raise in case of a validation error.
    """

	def __init__(self, regex, flags=0, message=None):
		self.regex = regex
		self.message = message

	def __call__(self, form, field, message=None):
		match = self.regex.fullmatch(field.data or '')
		if not match:
			if message is None:
				if self.message is None:
					message = field.gettext('Invalid input.')
				else:
					message = self.message

			raise ValidationError(message)
		return match



def validateYearRange(form, field):
	years = str(field.data)
	yearList = years.split("-")
	if len(yearList) == 2:
		pass
	else:
		yearList = years.split(",")
		if len(yearList) == 2:
			pass
		else:
			yearList = years.split()
			if len(yearList) == 2:
				pass
			else:
				pass
		if len(yearList) == 2:
			pass
		else:
			return
	try:
		lowerYear = int(yearList[0])
		higherYear = int(yearList[1])
	except ValueError:
		raise ValidationError("Couldn't parse the year, is it actually a year?")
	if higherYear < lowerYear:
		raise ValidationError('Year range error! Check that the range makes sense.')


# To do: have strict year range be a pop up, finish form implementation, edit distance???


class SearchForm(Form):
	termRe = re.compile("(\w+)(,\s*\w+)*")
	yearsRe = re.compile("(\d{4}[-,.]*(\d{4}){0,1}){0,1}")
	papers = StringField("Do you want a specific paper or papers?")
	searchTerm = StringField("What word do you want to graph?", [validators.InputRequired(), Regexp(termRe,message="Separate search terms with commas (e.g. 'chapeau, bonbon').")])
	yearRange = StringField("Do you want a specific year range?", [Regexp(yearsRe,message="Acceptable example ranges: '1870-1890', '1840.1860', '1920,1940'"),
																   validateYearRange])
	strictYearRange = BooleanField("Restrict to papers that published continuously over this year range?")


