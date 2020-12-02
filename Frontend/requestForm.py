from wtforms import ValidationError, Form, BooleanField, StringField, PasswordField, validators
import re


def validateYearRange(form, field):
	years = str(field.data)
	print(years)
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
			try:
				lowerYear = int(yearList[0])
				higherYear = int(yearList[1])
			except ValueError:
				raise ValidationError("Couldn't parse the year, is it actually a year?")
			if higherYear < lowerYear:
				raise ValidationError('Year range error! Ensure your range makes sense.')
		else:
			return



# To do: have strict year range be a pop up, finish form implementation, edit distance???

class SearchForm(Form):
	termRe = re.compile("(\w+)(,\s*\w+)*")
	papersRe = re.compile("(((\w+)\s*)*(,\s*((\w+)\s*)*)*){0,1}")
	yearsRe = re.compile("\d{4}[-,.]*(\d{4}){0,1}")
	searchTerm = StringField("What word do you want to graph?", [validators.DataRequired(), validators.Regexp(termRe,
																						 message="Separate search terms with commas (e.g. 'chapeau, bonbon').")])
	papers = StringField("Do you want a specific paper or papers?", [validators.Regexp(papersRe,
													  message="Separate desired papers with commas (e.g. 'Le Matin, Le Petit journal').")])
	yearRange = StringField("Do you want a specific year range?", [validators.Regexp(yearsRe,
															message="Acceptable example ranges: '1870-1890', '1840.1860', '1920,1940'"),
										  validateYearRange])
	strictYearRange = BooleanField("Restrict to papers publishing within year range?",
								   [validators.DataRequired()])
