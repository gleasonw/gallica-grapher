import gallicaWrapper


class GetAndPut:

    def getAndInsertRecordsForArgs(self, args, dbLink, identifier=None, requestStateHandlers=None):
        #need to pass handlers to wrapper
        #papersearch ?
        api = gallicaWrapper.connect('sru')
        records = api.get(**args)
        return dbLink.insert(
            records=records,
            requestStateHandlers=requestStateHandlers,
            identifier=identifier
        )