import { rest } from 'msw';

export const handlers = [
    rest.get('/api/numPapersOverRange/:startDate/:endDate', (req, res, ctx) => {
        return res(ctx.json({numPapers: 1}));
    }),
    rest.get('/api/continuousPapers', (req, res, ctx) => {
        return res(ctx.json({
            'paperNameCodes': [{
                'title': 'title',
                'code': 'code',
                'startDate': 2000,
                'endDate': 2001
            }]
        }));
    }),
    //mock get papers similar to keyword get
    rest.get('/api/papers/:keyword', (req, res, ctx) => {
        return res(ctx.json({
            'paperNameCodes': [{
                'title': 'A great tests paper',
                'code': 'code',
                'startDate': 2000,
                'endDate': 2001
            }]
        }));
    }),
    rest.post('/api/init', (req, res, ctx) => {
        return res(ctx.json({taskid: '123'}));
    }),
]