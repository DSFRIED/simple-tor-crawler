from marshmallow import Schema, fields, post_load, pre_load


class Paste(Schema):
    title = fields.Str()
    author = fields.Method()
    content = fields.Str()
    date = fields.DateTime()

    @pre_load
    def prepare_paste(self, data):
        UNKNOWN_AUTHORS = ('guest', 'unknown', 'anonymous')
        if data['author'].lower() in UNKNOWN_AUTHORS:
            data['author'] = ''

    @post_load
    def make_paste(self, data):
        return Paste(data)
