def get_records_and_insert(self):
    return self.insert_records(
        records=self.api.get(**self.args),
        identifier=self.identifier,
        stateHooks=self.stateHooks,
        conn=self.conn
    )

